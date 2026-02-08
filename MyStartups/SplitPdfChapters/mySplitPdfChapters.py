#!/usr/bin/env python3
"""Split a PDF into chapter PDFs based on detected chapter headings."""
from __future__ import annotations

import argparse
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

import pdfplumber
from pypdf import PdfReader, PdfWriter


# Only match "Chapter N" format - excludes Preface, Appendix, Index, etc.
DEFAULT_PATTERN = r"^chapter\s+([0-9]+|[ivxlcdm]+)\b[:.\- ]*(.*)$"


@dataclass
class ChapterStart:
    """Represents a detected chapter heading location."""
    page_index: int  # 0-based page index where chapter starts
    chapter_id: str  # Chapter number (e.g., "1", "2", "10")
    title: str       # Chapter title text


@dataclass
class Chapter:
    """Represents a complete chapter with page range."""
    start_page: int  # 0-based start page (inclusive)
    end_page: int    # 0-based end page (inclusive)
    chapter_id: str  # Chapter number for filename
    title: str       # Chapter title for filename


def _iter_nonempty_lines(text: str) -> Iterable[str]:
    """Yield non-empty lines from text, with whitespace stripped."""
    for line in text.splitlines():
        line = line.strip()
        if line:
            yield line


def _sanitize_filename(value: str, max_len: int = 80) -> str:
    """Convert text to safe filename: lowercase, replace special chars with underscores."""
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)  # Replace non-alphanumeric with _
    value = re.sub(r"_+", "_", value).strip("_")  # Collapse multiple underscores
    if not value:
        return "untitled"
    return value[:max_len]


def parse_page_ranges(
    range_spec: str, 
    total_pages: int, 
    pdf_path: Path, 
    pattern: re.Pattern[str]
) -> list[Chapter]:
    """Parse page range specification like '17-47:intro,48-80:setup'.
    
    Auto-detects chapter info from first page if no title provided.
    Returns list of Chapter objects. Page numbers are 1-based in input.
    """
    chapters: list[Chapter] = []
    # Split by comma to get individual ranges: "17-47:intro,48-80:setup" -> ["17-47:intro", "48-80:setup"]
    parts = [p.strip() for p in range_spec.split(",")]
    
    for idx, part in enumerate(parts, start=1):
        # Parse optional title: "17-47:intro" or just "17-47"
        if ":" in part:
            page_range, title = part.split(":", 1)
            manual_title = title.strip()
        else:
            page_range = part
            manual_title = None
        
        # Parse page range "17-47" into start and end pages
        try:
            start_str, end_str = page_range.split("-")
            start_page = int(start_str.strip()) - 1  # Convert to 0-based
            end_page = int(end_str.strip()) - 1      # Convert to 0-based
        except (ValueError, AttributeError):
            raise ValueError(f"Invalid page range format: {part}. Expected 'start-end' or 'start-end:title'")
        
        # Validate page range is within PDF bounds
        if start_page < 0 or end_page >= total_pages or start_page > end_page:
            raise ValueError(
                f"Invalid page range {start_page+1}-{end_page+1}. "
                f"PDF has {total_pages} pages (valid: 1-{total_pages})"
            )
        
        # Try to auto-detect chapter info from first page if no manual title provided
        chapter_id = str(idx)
        title = manual_title or f"part_{idx}"
        
        if not manual_title:
            # Open PDF and scan first page of this range for chapter heading
            with pdfplumber.open(str(pdf_path)) as pdf:
                first_page = pdf.pages[start_page]
                text = first_page.extract_text() or ""
                heading = _extract_chapter_heading(text, pattern)
                if heading:
                    detected_id, detected_title = heading
                    chapter_id = detected_id
                    title = detected_title if detected_title else title
                    print(f"  Auto-detected from page {start_page + 1}: Chapter {chapter_id} - {title}")
        
        chapters.append(
            Chapter(
                start_page=start_page,
                end_page=end_page,
                chapter_id=chapter_id,
                title=title,
            )
        )
    
    return chapters


def _extract_chapter_heading(text: str, pattern: re.Pattern[str]) -> Optional[tuple[str, str]]:
    """Extract chapter ID and title from page text using regex pattern.
    
    Returns: (chapter_id, title) or None if no match found.
    Handles cases where title is on the next line after "Chapter N".
    """
    lines = list(_iter_nonempty_lines(text))
    for idx, line in enumerate(lines):
        match = pattern.match(line)
        if match:
            chapter_id = match.group(1) or ""  # e.g., "2" from "Chapter 2"
            title = (match.group(2) or "").strip()  # e.g., "Introduction" from "Chapter 2: Introduction"
            
            # If title is empty and there's a next line, use it as title
            # (handles "Chapter 2\nIntroduction" format)
            if not title and idx + 1 < len(lines):
                next_line = lines[idx + 1].strip()
                if not pattern.match(next_line):  # Don't use next line if it's another chapter
                    title = next_line
            return chapter_id, title
    return None


def find_chapter_starts(pdf_path: Path, pattern: re.Pattern[str]) -> list[ChapterStart]:
    """Scan all PDF pages to find chapter headings.
    
    Returns list of ChapterStart objects with page locations and chapter info.
    Shows progress every 10 pages.
    """
    chapter_starts: list[ChapterStart] = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        total = len(pdf.pages)
        print(f"Scanning {total} pages for chapter headings...")
        
        for page_index, page in enumerate(pdf.pages):
            # Show progress periodically
            if (page_index + 1) % 10 == 0 or page_index + 1 == total:
                print(f"  Progress: {page_index + 1}/{total} pages")
            
            # Extract text and search for chapter heading
            text = page.extract_text() or ""
            heading = _extract_chapter_heading(text, pattern)
            if heading:
                chapter_id, title = heading
                chapter_starts.append(
                    ChapterStart(page_index=page_index, chapter_id=chapter_id, title=title)
                )
                print(f"  Found chapter on page {page_index + 1}: {chapter_id} - {title}")
    return chapter_starts


def build_chapters(
    chapter_starts: list[ChapterStart],
    total_pages: int,
    include_front_matter: bool,
) -> list[Chapter]:
    """Convert chapter start positions into complete chapters with page ranges.
    
    Each chapter extends from its start page to one page before the next chapter.
    Optionally includes front matter (pages before first chapter) as chapter 0.
    """
    chapters: list[Chapter] = []

    # Add front matter if requested and there are pages before first chapter
    if include_front_matter and (not chapter_starts or chapter_starts[0].page_index > 0):
        first_end = chapter_starts[0].page_index - 1 if chapter_starts else total_pages - 1
        if first_end >= 0:
            chapters.append(
                Chapter(
                    start_page=0,
                    end_page=first_end,
                    chapter_id="0",
                    title="front_matter",
                )
            )

    # Build chapters from detected start positions
    for idx, start in enumerate(chapter_starts):
        # Chapter ends at page before next chapter (or end of PDF)
        next_start = chapter_starts[idx + 1].page_index if idx + 1 < len(chapter_starts) else total_pages
        chapters.append(
            Chapter(
                start_page=start.page_index,
                end_page=next_start - 1,
                chapter_id=start.chapter_id,
                title=start.title,
            )
        )

    return chapters


def write_chapters(
    input_pdf: Path,
    output_dir: Path,
    chapters: list[Chapter],
) -> None:
    """Write each chapter to a separate PDF file.
    
    Output filename format: <input_basename>_ch<chapter_id>_<sanitized_title>.pdf
    Example: book_ch2_introduction.pdf
    """
    reader = PdfReader(str(input_pdf))
    base_name = input_pdf.stem  # Filename without extension
    print(f"\nWriting {len(chapters)} chapter(s) to {output_dir}...")

    for index, chapter in enumerate(chapters, start=1):
        # Create a new PDF for this chapter
        writer = PdfWriter()
        
        # Copy pages from original PDF (inclusive range)
        for page_num in range(chapter.start_page, chapter.end_page + 1):
            writer.add_page(reader.pages[page_num])

        # Build output filename using detected chapter number and title
        title = _sanitize_filename(chapter.title)
        output_name = f"{base_name}_ch{chapter.chapter_id}_{title}.pdf"
        output_path = output_dir / output_name
        
        # Write PDF file
        with output_path.open("wb") as f:
            writer.write(f)

        print(
            f"Saved: {output_path.name} (pages {chapter.start_page + 1}-{chapter.end_page + 1})"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Split a PDF into chapter PDFs.")
    parser.add_argument("--input", required=True, help="Input PDF file path")
    parser.add_argument(
        "--output",
        help="Output directory (default: same directory as input PDF)",
    )
    parser.add_argument(
        "--page-range",
        help="Manual page ranges (1-based): '17-47:intro,48-80:chapter1' (skips auto-detection)",
    )
    parser.add_argument(
        "--pattern",
        default=DEFAULT_PATTERN,
        help="Regex pattern to detect chapter headings (case-insensitive)",
    )
    parser.add_argument(
        "--include-front-matter",
        action="store_true",
        help="Include pages before the first chapter as a separate PDF",
    )
    return parser.parse_args()


def main() -> None:
    """Main entry point: parse arguments and orchestrate PDF splitting."""
    args = parse_args()
    input_pdf = Path(args.input).expanduser().resolve()
    
    # Validate input file exists
    if not input_pdf.exists():
        raise FileNotFoundError(f"Input PDF not found: {input_pdf}")
    
    # Determine output directory (default: same as input PDF)
    if args.output:
        output_dir = Path(args.output).expanduser().resolve()
    else:
        output_dir = input_pdf.parent

    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Processing: {input_pdf.name}")
    print(f"Output directory: {output_dir}\n")

    total_pages = len(PdfReader(str(input_pdf)).pages)
    
    # Mode 1: Manual page ranges (--page-range option)
    if args.page_range:
        print(f"Using manual page ranges...")
        pattern = re.compile(args.pattern, flags=re.IGNORECASE)
        chapters = parse_page_ranges(args.page_range, total_pages, input_pdf, pattern)
        
        # Display detected/defined chapters
        print(f"\nDefined {len(chapters)} chapter(s):")
        print("=" * 70)
        for idx, ch in enumerate(chapters, start=1):
            print(f"  {idx}. {ch.title}: pages {ch.start_page + 1}-{ch.end_page + 1}")
        print("=" * 70)
    else:
        # Mode 2: Auto-detect chapters by scanning all pages
        pattern = re.compile(args.pattern, flags=re.IGNORECASE)
        chapter_starts = find_chapter_starts(input_pdf, pattern)

        if not chapter_starts:
            raise RuntimeError(
                "No chapter headings detected. Try adjusting --pattern or check the PDF text extraction."
            )

        # Display detected chapters
        print(f"\nDetected {len(chapter_starts)} chapter(s):")
        print("=" * 70)
        for idx, cs in enumerate(chapter_starts, start=1):
            print(f"  {idx}. Chapter {cs.chapter_id}: {cs.title or '(no title)'} [page {cs.page_index + 1}]")
        print("=" * 70)
        
        # Build complete chapters with page ranges
        chapters = build_chapters(chapter_starts, total_pages, args.include_front_matter)
    
    # Ask user confirmation before writing files
    response = input("\nProceed with splitting? (YES/NO): ").strip().upper()
    if response != "YES":
        print("Cancelled.")
        return

    if not chapters:
        raise RuntimeError("No chapters to write after processing.")

    # Write chapter PDFs
    write_chapters(input_pdf, output_dir, chapters)
    print(f"\n✓ Complete! Split into {len(chapters)} file(s).")


if __name__ == "__main__":
    main()

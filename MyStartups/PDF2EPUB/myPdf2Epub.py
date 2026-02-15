#!/usr/bin/env python3
"""
PDF to EPUB Converter
Converts PDF files to EPUB format while preserving images, tables, and formatting.
"""

import argparse
import logging
import os
import sys
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import fitz  # PyMuPDF
from ebooklib import epub
from PIL import Image
import io


class PDFtoEPUBConverter:
    """Main converter class for PDF to EPUB conversion."""
    
    def __init__(self, input_path: str, output_path: Optional[str] = None,
                 keep_index: bool = False, chapter_by_chapter: bool = False):
        """
        Initialize the converter.
        
        Args:
            input_path: Path to input PDF file
            output_path: Path to output EPUB file (optional)
            keep_index: Whether to preserve PDF's table of contents
            chapter_by_chapter: Whether to create separate EPUB files per chapter
        """
        self.input_path = Path(input_path)
        self.keep_index = keep_index
        self.chapter_by_chapter = chapter_by_chapter
        
        # Set output path
        if output_path:
            self.output_path = Path(output_path)
        else:
            self.output_path = self.input_path.with_suffix('.epub')
        
        # Initialize PDF document
        self.pdf_doc = None
        self.book = None
        
        # Setup logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Configure logging for progress tracking."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.logger = logging.getLogger(__name__)
    
    def validate_input(self) -> bool:
        """
        Validate input file exists and is readable.
        
        Returns:
            bool: True if valid, False otherwise
        """
        if not self.input_path.exists():
            self.logger.error(f"Input file not found: {self.input_path}")
            return False
        
        if not self.input_path.is_file():
            self.logger.error(f"Input path is not a file: {self.input_path}")
            return False
        
        if self.input_path.suffix.lower() != '.pdf':
            self.logger.error(f"Input file is not a PDF: {self.input_path}")
            return False
        
        return True
    
    def open_pdf(self) -> bool:
        """
        Open and load the PDF document.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.logger.info(f"Opening PDF file: {self.input_path}")
            self.pdf_doc = fitz.open(self.input_path)
            self.logger.info(f"PDF loaded successfully: {len(self.pdf_doc)} pages")
            return True
        except Exception as e:
            self.logger.error(f"Failed to open PDF: {e}")
            return False
    
    def extract_metadata(self) -> Dict[str, str]:
        """
        Extract metadata from PDF.
        
        Returns:
            Dict containing title, author, subject, etc.
        """
        metadata = self.pdf_doc.metadata
        
        # Extract and clean metadata
        title = metadata.get('title', self.input_path.stem)
        author = metadata.get('author', 'Unknown')
        subject = metadata.get('subject', '')
        
        self.logger.info(f"Extracted metadata - Title: {title}, Author: {author}")
        
        return {
            'title': title,
            'author': author,
            'subject': subject,
            'language': 'en'
        }
    
    def extract_toc(self, filter_chapters_only: bool = True) -> List[Dict]:
        """
        Extract table of contents from PDF.
        
        Args:
            filter_chapters_only: If True, only extract main chapter entries (Chapter 1, Chapter 2, etc.)
        
        Returns:
            List of TOC entries with level, title, and page number
        """
        toc = self.pdf_doc.get_toc()
        self.logger.info(f"Extracted {len(toc)} TOC entries from PDF")
        
        if filter_chapters_only:
            # Filter to only include entries matching "Chapter N" pattern
            filtered_toc = []
            chapter_pattern = re.compile(r'^Chapter\s+\d+', re.IGNORECASE)
            
            for entry in toc:
                level, title, page = entry
                if chapter_pattern.match(title.strip()):
                    filtered_toc.append(entry)
            
            self.logger.info(f"Filtered to {len(filtered_toc)} main chapter entries (Chapter 1, 2, ...)")
            return filtered_toc
        
        return toc
    
    def extract_images_from_page(self, page_num: int) -> List[Tuple[bytes, str]]:
        """
        Extract images from a specific page.
        
        Args:
            page_num: Page number (0-indexed)
        
        Returns:
            List of tuples (image_bytes, image_format)
        """
        page = self.pdf_doc[page_num]
        images = []
        
        try:
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = self.pdf_doc.extract_image(xref)
                
                if base_image:
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    images.append((image_bytes, image_ext))
            
            if images:
                self.logger.debug(f"Extracted {len(images)} images from page {page_num + 1}")
        
        except Exception as e:
            self.logger.warning(f"Error extracting images from page {page_num + 1}: {e}")
        
        return images
    
    def create_cover_image(self) -> Optional[bytes]:
        """
        Create cover image from first page of PDF.
        
        Returns:
            Cover image as bytes or None
        """
        try:
            self.logger.info("Creating cover image from first page")
            page = self.pdf_doc[0]
            
            # Render page to image at high resolution
            mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better quality
            pix = page.get_pixmap(matrix=mat)
            
            # Convert to PIL Image
            img_data = pix.tobytes("png")
            
            # Optimize image size
            img = Image.open(io.BytesIO(img_data))
            
            # Resize if too large
            max_width = 800
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
            # Save to bytes
            output = io.BytesIO()
            img.save(output, format='PNG', optimize=True)
            cover_bytes = output.getvalue()
            
            self.logger.info("Cover image created successfully")
            return cover_bytes
        
        except Exception as e:
            self.logger.warning(f"Failed to create cover image: {e}")
            return None
    
    def extract_text_from_page(self, page_num: int, preserve_formatting: bool = True) -> str:
        """
        Extract text content from a page with formatting.
        
        Args:
            page_num: Page number (0-indexed)
            preserve_formatting: Whether to preserve text formatting
        
        Returns:
            Extracted text as string with HTML formatting
        """
        page = self.pdf_doc[page_num]
        
        if preserve_formatting:
            # Extract text blocks with formatting info
            blocks = page.get_text("dict")["blocks"]
            formatted_text = ""
            
            for block in blocks:
                if block.get("type") == 0:  # Text block
                    for line in block.get("lines", []):
                        line_text = ""
                        for span in line.get("spans", []):
                            text = span.get("text", "")
                            font_size = span.get("size", 12)
                            font_flags = span.get("flags", 0)
                            
                            # Apply formatting based on font properties
                            if font_size > 16:  # Likely a heading
                                text = f"<h2>{text}</h2>"
                            elif font_size > 14:
                                text = f"<h3>{text}</h3>"
                            elif font_flags & 2**0:  # Superscript
                                text = f"<sup>{text}</sup>"
                            elif font_flags & 2**1:  # Italic
                                text = f"<em>{text}</em>"
                            elif font_flags & 2**4:  # Bold
                                text = f"<strong>{text}</strong>"
                            
                            line_text += text
                        
                        if line_text.strip():
                            formatted_text += line_text + "\n"
                    formatted_text += "\n"
            
            return formatted_text
        else:
            return page.get_text("text")
    
    def create_epub_book(self, metadata: Dict) -> epub.EpubBook:
        """
        Create and configure EPUB book.
        
        Args:
            metadata: Book metadata dictionary
        
        Returns:
            Configured EpubBook object
        """
        self.logger.info("Creating EPUB book structure")
        
        book = epub.EpubBook()
        
        # Set metadata
        book.set_identifier(f'pdf2epub_{self.input_path.stem}')
        book.set_title(metadata['title'])
        book.set_language(metadata['language'])
        book.add_author(metadata['author'])
        
        # Add professional CSS stylesheet
        css_style = '''
        @namespace epub "http://www.idpf.org/2007/ops";
        
        body {
            font-family: "Georgia", "Times New Roman", serif;
            font-size: 1em;
            line-height: 1.6;
            margin: 1em;
            text-align: justify;
        }
        
        h1 {
            font-size: 2em;
            font-weight: bold;
            margin-top: 1em;
            margin-bottom: 0.8em;
            text-align: left;
            page-break-before: always;
            border-bottom: 2px solid #333;
            padding-bottom: 0.3em;
        }
        
        h2 {
            font-size: 1.5em;
            font-weight: bold;
            margin-top: 1em;
            margin-bottom: 0.6em;
            text-align: left;
        }
        
        h3 {
            font-size: 1.2em;
            font-weight: bold;
            margin-top: 0.8em;
            margin-bottom: 0.5em;
            text-align: left;
        }
        
        p {
            margin: 0.5em 0;
            text-indent: 1.5em;
        }
        
        p:first-of-type {
            text-indent: 0;
        }
        
        img {
            max-width: 100%;
            height: auto;
            display: block;
            margin: 1em auto;
            page-break-inside: avoid;
        }
        
        strong {
            font-weight: bold;
        }
        
        em {
            font-style: italic;
        }
        
        code {
            font-family: "Courier New", monospace;
            background-color: #f4f4f4;
            padding: 0.2em 0.4em;
            border-radius: 3px;
        }
        
        pre {
            font-family: "Courier New", monospace;
            background-color: #f4f4f4;
            padding: 1em;
            border-radius: 5px;
            overflow-x: auto;
            white-space: pre-wrap;
        }
        
        .chapter {
            page-break-before: always;
        }
        '''
        
        # Create CSS file
        nav_css = epub.EpubItem(
            uid="style_nav",
            file_name="style/nav.css",
            media_type="text/css",
            content=css_style
        )
        book.add_item(nav_css)
        
        return book
    
    def add_cover_to_epub(self, book: epub.EpubBook, cover_bytes: bytes):
        """
        Add cover image to EPUB.
        
        Args:
            book: EpubBook object
            cover_bytes: Cover image as bytes
        """
        book.set_cover("cover.png", cover_bytes)
        self.logger.info("Cover added to EPUB")
    
    def create_chapter_content(self, chapter_num: int, title: str, 
                              text: str, images: List[Tuple[bytes, str]],
                              book: epub.EpubBook) -> epub.EpubHtml:
        """
        Create chapter with text and images using professional formatting.
        
        Args:
            chapter_num: Chapter number
            title: Chapter title
            text: Chapter text content (may contain HTML formatting)
            images: List of image tuples (bytes, format)
            book: EpubBook object
        
        Returns:
            EpubHtml chapter object
        """
        # Create chapter
        chapter = epub.EpubHtml(
            title=title,
            file_name=f'chapter_{chapter_num:03d}.xhtml',
            lang='en'
        )
        
        # Link to CSS stylesheet
        chapter.add_item(book.get_item_with_id('style_nav'))
        
        # Build HTML content - just the body content, ebooklib handles the wrapper
        html_parts = []
        html_parts.append(f'<div class="chapter">')
        html_parts.append(f'<h1>{title}</h1>')
        
        # Process and add text content
        # Split into paragraphs and handle formatting
        lines = text.split('\n')
        current_para = []
        
        for line in lines:
            line = line.strip()
            
            if not line:
                # Empty line - end current paragraph
                if current_para:
                    para_text = ' '.join(current_para)
                    # Check if it's already a heading
                    if not (para_text.startswith('<h') or para_text.startswith('<img')):
                        html_parts.append(f'<p>{para_text}</p>')
                    else:
                        html_parts.append(para_text)
                    current_para = []
            else:
                # Add line to current paragraph
                current_para.append(line)
        
        # Add remaining paragraph
        if current_para:
            para_text = ' '.join(current_para)
            if not (para_text.startswith('<h') or para_text.startswith('<img')):
                html_parts.append(f'<p>{para_text}</p>')
            else:
                html_parts.append(para_text)
        
        # Add images with proper positioning
        if images:
            html_parts.append('<div class="images">')
            for img_idx, (img_bytes, img_ext) in enumerate(images):
                img_filename = f'images/ch{chapter_num:03d}_img{img_idx:03d}.{img_ext}'
                
                # Create image item
                img_item = epub.EpubImage()
                img_item.file_name = img_filename
                img_item.content = img_bytes
                
                # Add image to book
                book.add_item(img_item)
                
                # Add image to HTML with caption
                html_parts.append(f'<figure>')
                html_parts.append(f'<img src="../{img_filename}" alt="Figure {img_idx + 1}"/>')
                html_parts.append(f'<figcaption>Figure {img_idx + 1}</figcaption>')
                html_parts.append(f'</figure>')
            html_parts.append('</div>')
        
        html_parts.append('</div>')
        
        chapter.content = '\n'.join(html_parts)
        
        return chapter
    
    def convert(self) -> bool:
        """
        Main conversion method.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Validate input
            if not self.validate_input():
                return False
            
            # Open PDF
            if not self.open_pdf():
                return False
            
            # Extract metadata
            metadata = self.extract_metadata()
            
            # Create EPUB book
            book = self.create_epub_book(metadata)
            
            # Create and add cover
            cover_bytes = self.create_cover_image()
            if cover_bytes:
                self.add_cover_to_epub(book, cover_bytes)
            
            # Extract TOC if needed (by default only main chapters: Chapter 1, 2, ...)
            toc_entries = []
            if self.keep_index:
                toc_entries = self.extract_toc(filter_chapters_only=True)
            
            # Process pages
            chapters = []
            spine = ['nav']
            
            total_pages = len(self.pdf_doc)
            self.logger.info(f"Processing {total_pages} pages...")
            
            # Group pages into chapters based on TOC or use fixed size
            if toc_entries and self.keep_index:
                # Use TOC to define chapters
                for idx, entry in enumerate(toc_entries):
                    level, title, page_num = entry
                    
                    # Determine page range for this chapter
                    if idx < len(toc_entries) - 1:
                        next_page = toc_entries[idx + 1][2]
                    else:
                        next_page = total_pages
                    
                    # Extract content for chapter
                    chapter_text = ""
                    chapter_images = []
                    
                    for p in range(page_num - 1, min(next_page - 1, total_pages)):
                        chapter_text += self.extract_text_from_page(p) + "\n\n"
                        chapter_images.extend(self.extract_images_from_page(p))
                    
                    # Create chapter
                    chapter = self.create_chapter_content(
                        idx + 1, title, chapter_text, chapter_images, book
                    )
                    
                    book.add_item(chapter)
                    chapters.append(chapter)
                    spine.append(chapter)
                    
                    self.logger.info(f"Created chapter {idx + 1}: {title}")
            
            else:
                # Create one chapter per page or group pages
                pages_per_chapter = 10 if not self.chapter_by_chapter else 1
                
                for page_num in range(total_pages):
                    chapter_num = page_num // pages_per_chapter
                    
                    if page_num % pages_per_chapter == 0:
                        # Start new chapter
                        chapter_title = f"Chapter {chapter_num + 1}"
                        chapter_text = ""
                        chapter_images = []
                    
                    # Add page content to current chapter
                    chapter_text += self.extract_text_from_page(page_num) + "\n\n"
                    chapter_images.extend(self.extract_images_from_page(page_num))
                    
                    # Complete chapter at end of group or end of document
                    if (page_num + 1) % pages_per_chapter == 0 or page_num == total_pages - 1:
                        chapter = self.create_chapter_content(
                            chapter_num + 1, chapter_title, chapter_text, 
                            chapter_images, book
                        )
                        
                        book.add_item(chapter)
                        chapters.append(chapter)
                        spine.append(chapter)
                        
                        self.logger.info(
                            f"Progress: {page_num + 1}/{total_pages} pages processed"
                        )
            
            # Add navigation
            book.toc = tuple(chapters)
            book.add_item(epub.EpubNcx())
            book.add_item(epub.EpubNav())
            
            # Set spine
            book.spine = spine
            
            # Write EPUB file
            self.logger.info(f"Writing EPUB to: {self.output_path}")
            epub.write_epub(self.output_path, book)
            
            self.logger.info("✓ Conversion completed successfully!")
            self.logger.info(f"Output file: {self.output_path}")
            
            return True
        
        except Exception as e:
            self.logger.error(f"Conversion failed: {e}", exc_info=True)
            return False
        
        finally:
            if self.pdf_doc:
                self.pdf_doc.close()


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description='Convert PDF files to EPUB format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --input book.pdf
  %(prog)s --input book.pdf --output mybook.epub
  %(prog)s --input book.pdf --keepIndex
  %(prog)s --input book.pdf --chapter-by-chapter
        """
    )
    
    parser.add_argument(
        '--input',
        required=True,
        help='Path to input PDF file (required)'
    )
    
    parser.add_argument(
        '--output',
        help='Path to output EPUB file (default: same as input with .epub extension)'
    )
    
    parser.add_argument(
        '--keepIndex',
        action='store_true',
        help='Keep the original PDF\'s table of contents/index (default: skip)'
    )
    
    parser.add_argument(
        '--chapter-by-chapter',
        action='store_true',
        help='Create separate EPUB files for each chapter (default: all-in-one)'
    )
    
    return parser.parse_args()


def main():
    """Main entry point."""
    try:
        # Parse arguments
        args = parse_arguments()
        
        # Create converter
        converter = PDFtoEPUBConverter(
            input_path=args.input,
            output_path=args.output,
            keep_index=args.keepIndex,
            chapter_by_chapter=args.chapter_by_chapter
        )
        
        # Perform conversion
        success = converter.convert()
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
    
    except KeyboardInterrupt:
        print("\n\nConversion interrupted by user.")
        sys.exit(130)
    
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

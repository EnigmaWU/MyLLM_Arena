"""
Input Layer - Source Parsers for various input formats
"""

import re
from pathlib import Path
from typing import List, Union
from urllib.parse import urlparse

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

from bs4 import BeautifulSoup
import requests
import markdown

from .models import Document, Section


class SourceParser:
    """Main parser class that routes to specific parsers based on input type."""
    
    def __init__(self):
        self.pdf_parser = PDFParser()
        self.markdown_parser = MarkdownParser()
        self.web_parser = WebParser()
    
    def parse(self, source: str) -> Document:
        """
        Parse a source file or URL into a Document.
        
        Args:
            source: Path to file or URL
            
        Returns:
            Parsed Document object
        """
        # Check if it's a URL
        if source.startswith(("http://", "https://")):
            return self.web_parser.parse_url(source)
        
        # Check if it's a file
        path = Path(source)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {source}")
        
        # Route based on extension
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            return self.pdf_parser.parse_pdf(str(path))
        elif suffix in [".md", ".markdown"]:
            return self.markdown_parser.parse_markdown(str(path))
        elif suffix in [".txt"]:
            return self._parse_text(str(path))
        else:
            raise ValueError(
                f"Unsupported format: {suffix}. "
                f"Supported formats: .pdf, .md, .markdown, .txt, or HTTP/HTTPS URLs"
            )
    
    def _parse_text(self, path: str) -> Document:
        """Simple text file parser."""
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return Document(
            content=content,
            structure=[Section(title="Content", content=content, level=1)],
            source_type="text",
            source_path=path
        )


class PDFParser:
    """Parser for PDF files."""
    
    def parse_pdf(self, path: str) -> Document:
        """Parse PDF file."""
        if fitz is None and pdfplumber is None:
            raise ImportError(
                "PDF parsing requires PyMuPDF or pdfplumber. "
                "Install with: pip install PyMuPDF pdfplumber"
            )
        
        try:
            if fitz:
                return self._parse_with_pymupdf(path)
            else:
                return self._parse_with_pdfplumber(path)
        except Exception as e:
            raise RuntimeError(
                f"Failed to parse PDF (possibly corrupted): {e}\n"
                f"Suggestions:\n"
                f"  • Try re-downloading the PDF\n"
                f"  • Convert to text manually and use --input file.txt\n"
                f"  • Check if file is password-protected"
            )
    
    def _parse_with_pymupdf(self, path: str) -> Document:
        """Parse using PyMuPDF."""
        doc = fitz.open(path)
        content = ""
        sections = []
        
        # Get page count before closing
        page_count = len(doc)
        
        for page_num, page in enumerate(doc):
            page_text = page.get_text()
            content += page_text + "\n"
        
        doc.close()
        
        # Extract sections based on text formatting
        sections = self._extract_sections(content)
        
        return Document(
            content=content,
            structure=sections,
            metadata={"page_count": page_count},
            source_type="pdf",
            source_path=path
        )
    
    def _parse_with_pdfplumber(self, path: str) -> Document:
        """Parse using pdfplumber."""
        content = ""
        
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    content += page_text + "\n"
        
        sections = self._extract_sections(content)
        
        return Document(
            content=content,
            structure=sections,
            metadata={"page_count": len(pdf.pages)},
            source_type="pdf",
            source_path=path
        )
    
    def _extract_sections(self, content: str) -> List[Section]:
        """Extract sections from content based on patterns."""
        sections = []
        lines = content.split('\n')
        
        current_section = None
        current_content = []
        
        for line in lines:
            # Simple heuristic: lines in ALL CAPS or followed by many = or - are headers
            stripped = line.strip()
            
            if self._is_likely_header(stripped, lines):
                if current_section:
                    current_section.content = '\n'.join(current_content)
                    sections.append(current_section)
                
                current_section = Section(
                    title=stripped,
                    content="",
                    level=1
                )
                current_content = []
            else:
                current_content.append(line)
        
        # Add last section
        if current_section:
            current_section.content = '\n'.join(current_content)
            sections.append(current_section)
        
        if not sections:
            sections = [Section(title="Document", content=content, level=1)]
        
        return sections
    
    def _is_likely_header(self, line: str, context_lines: List[str]) -> bool:
        """Heuristic to detect if a line is likely a header."""
        if not line:
            return False
        
        # Short lines in title case or all caps
        if len(line) < 100 and (line.isupper() or line.istitle()):
            return True
        
        # Lines ending with :
        if line.endswith(':') and len(line) < 80:
            return True
        
        # Numbered sections
        if re.match(r'^\d+\.?\s+[A-Z]', line):
            return True
        
        return False


class MarkdownParser:
    """Parser for Markdown files."""
    
    def parse_markdown(self, path: str) -> Document:
        """Parse Markdown file."""
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse structure from markdown headings
        sections = self._extract_markdown_sections(content)
        
        return Document(
            content=content,
            structure=sections,
            source_type="markdown",
            source_path=path
        )
    
    def _extract_markdown_sections(self, content: str) -> List[Section]:
        """Extract sections from markdown based on headings."""
        sections = []
        lines = content.split('\n')
        
        current_section = None
        current_content = []
        current_level = 0
        
        for line in lines:
            # Check for ATX-style headings (# Heading)
            match = re.match(r'^(#{1,6})\s+(.+)$', line)
            
            if match:
                if current_section:
                    current_section.content = '\n'.join(current_content).strip()
                    sections.append(current_section)
                
                level = len(match.group(1))
                title = match.group(2)
                
                current_section = Section(
                    title=title,
                    content="",
                    level=level
                )
                current_content = []
                current_level = level
            else:
                current_content.append(line)
        
        # Add last section
        if current_section:
            current_section.content = '\n'.join(current_content).strip()
            sections.append(current_section)
        
        if not sections:
            sections = [Section(title="Document", content=content, level=1)]
        
        return sections


class WebParser:
    """Parser for web content."""
    
    def parse_url(self, url: str) -> Document:
        """Fetch and parse web content."""
        # Validate URL
        parsed = urlparse(url)
        if not parsed.scheme in ['http', 'https']:
            raise ValueError(f"Invalid URL scheme: {parsed.scheme}. Use http:// or https://")
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            error_msg = str(e).lower()
            if '404' in error_msg:
                raise RuntimeError(f"404 Not Found: {url}")
            elif 'timeout' in error_msg:
                raise RuntimeError(f"Timeout while fetching URL: {url}")
            elif 'resolve' in error_msg or 'dns' in error_msg:
                raise RuntimeError(f"Failed to resolve domain: {url}")
            else:
                raise RuntimeError(f"Network error fetching URL: {e}")
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove navigation, scripts, styles, ads
        for tag in soup(['nav', 'script', 'style', 'aside', 'header', 'footer']):
            tag.decompose()
        
        # Try to find main content
        main_content = (
            soup.find('main') or 
            soup.find('article') or
            soup.find('div', class_=re.compile('content|article|post', re.I)) or
            soup.find('body')
        )
        
        if main_content:
            text = main_content.get_text(separator='\n', strip=True)
        else:
            text = soup.get_text(separator='\n', strip=True)
        
        # Extract sections from headings
        sections = self._extract_html_sections(main_content or soup)
        
        return Document(
            content=text,
            structure=sections,
            metadata={"url": url, "title": soup.title.string if soup.title else ""},
            source_type="web",
            source_path=url
        )
    
    def _extract_html_sections(self, soup) -> List[Section]:
        """Extract sections from HTML headings."""
        sections = []
        
        # Find all headings
        for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            level = int(heading.name[1])
            title = heading.get_text(strip=True)
            
            # Get content until next heading
            content_parts = []
            for sibling in heading.find_next_siblings():
                if sibling.name and sibling.name.startswith('h'):
                    break
                content_parts.append(sibling.get_text(separator='\n', strip=True))
            
            content = '\n'.join(content_parts)
            
            sections.append(Section(
                title=title,
                content=content,
                level=level
            ))
        
        if not sections:
            text = soup.get_text(separator='\n', strip=True)
            sections = [Section(title="Content", content=text, level=1)]
        
        return sections

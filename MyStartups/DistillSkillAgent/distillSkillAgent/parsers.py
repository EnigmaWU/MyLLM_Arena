"""
Input Layer - Source Parsers for various input formats
"""

import json
import re
import sys
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

from .models import Document, Section, ChatMessage, ChatSession


class SourceParser:
    """Main parser class that routes to specific parsers based on input type."""
    
    def __init__(self):
        self.pdf_parser = PDFParser()
        self.markdown_parser = MarkdownParser()
        self.web_parser = WebParser()
        self.chat_session_parser = ChatSessionParser()
    
    def parse(self, source: str) -> Document:
        """
        Parse a source file or URL into a Document.
        
        Args:
            source: Path to file, URL, or '-' for stdin (chat session JSON)
            
        Returns:
            Parsed Document object
        """
        # Check for stdin input (current chat session)
        if source == "-":
            return self.chat_session_parser.parse_stream(sys.stdin)

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
        elif suffix == ".json":
            return self.chat_session_parser.parse_json_file(str(path))
        else:
            raise ValueError(
                f"Unsupported format: {suffix}. "
                f"Supported formats: .pdf, .md, .markdown, .txt, .json, or HTTP/HTTPS URLs"
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
        
        # Extract TOC
        try:
            toc = doc.get_toc()
        except:
            toc = []

        # Extract text per page first
        page_texts = {}
        full_text = []
        for i, page in enumerate(doc):
            text = page.get_text()
            page_texts[i + 1] = text # 1-based index
            full_text.append(text)
            
        doc.close()
        content = "\n".join(full_text)
        
        # Strategy: Use TOC if available and robust
        if toc and len(toc) > 5:
            sections = self._build_sections_from_toc(toc, page_texts, page_count)
        else:
            # Fallback to heuristic
            sections = self._extract_sections(content)
        
        return Document(
            content=content,
            structure=sections,
            metadata={"page_count": page_count, "toc_found": bool(toc)},
            source_type="pdf",
            source_path=path
        )

    def _build_sections_from_toc(self, toc: list, page_texts: dict, total_pages: int) -> List[Section]:
        """Reconstruct sections based on TOC page numbers."""
        # TOC format: [[lvl, title, page, ...], ...]
        sections = []
        
        # We only handle top-level sections for the main structure list, 
        # but we can try to nest them if we want. 
        # For simplicity in 'FindActionBookAlg', a flat list or simple hierarchy is fine.
        # Let's try to flatten 'Chunks' based on TOC entries.
        
        for i, entry in enumerate(toc):
            lvl, title, page = entry[0], entry[1], entry[2]
            
            if page < 0 or page > total_pages:
                continue
                
            # Determine end page
            if i < len(toc) - 1:
                next_entry = toc[i+1]
                end_page = next_entry[2]
            else:
                end_page = total_pages + 1
            
            # Extract content for this section
            # Note: This is imperfect as sections can start mid-page.
            # But it's better than nothing.
            section_content = []
            
            # If start and end are same page
            if page == end_page or (page == end_page - 1): # simplistic check
                 if page in page_texts:
                     section_content.append(page_texts[page])
            else:
                # Collect pages
                # Ensure we don't go out of bounds or negative (PyMuPDF toc sometimes has weird errors)
                start_p = max(1, page)
                end_p = min(end_page, total_pages + 1)
                
                for p_num in range(start_p, end_p):
                    if p_num in page_texts:
                        section_content.append(page_texts[p_num])

            sections.append(Section(
                title=title,
                content="\n".join(section_content),
                level=lvl
            ))
            
        # If TOC yielded nothing useful (e.g. all empty), fallback?
        # For now assume it works if TOC > 5 items
        return sections
    
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


class ChatSessionParser:
    """
    Parser for LLM chat session files.

    Supports multiple export formats:
      - Generic: {"messages": [{"role": "user"|"assistant", "content": "..."}]}
      - Claude:  {"chat_messages": [{"sender": "human"|"assistant", "text": "..."}]}
      - ChatGPT: {"mapping": {"<id>": {"message": {"role": "...",
                               "content": {"parts": [...]}}}}}

    Also accepts a plain list of message objects as the top-level value.
    """

    def parse_json_file(self, path: str) -> Document:
        """Parse a JSON chat session file."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Invalid JSON in chat session file: {path}\n"
                f"  Detail: {e}\n"
                f"  Suggestion: Verify the file is a valid JSON chat session export."
            )
        return self._parse_session_data(data, source_path=path)

    def parse_stream(self, stream) -> Document:
        """Parse a chat session from a text stream (e.g. stdin)."""
        try:
            data = json.load(stream)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Invalid JSON received on stdin.\n"
                f"  Detail: {e}\n"
                f"  Suggestion: Pipe a valid JSON chat session, e.g.:\n"
                f"    cat session.json | myDistillSkillAgent --input - --output-json skill.json"
            )
        return self._parse_session_data(data, source_path="<stdin>")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _parse_session_data(self, data: dict, source_path: str = "") -> Document:
        """Convert raw JSON data into a Document."""
        session = self._build_chat_session(data)
        return self._session_to_document(session, source_path)

    def _build_chat_session(self, data) -> ChatSession:
        """Detect format and return a normalised ChatSession."""
        fmt = self._detect_format(data)

        if fmt == "generic_list":
            messages = self._parse_generic_list(data)
            return ChatSession(messages=messages)

        if fmt == "claude":
            return self._parse_claude(data)

        if fmt == "chatgpt":
            return self._parse_chatgpt(data)

        # Default: generic dict with "messages" key
        return self._parse_generic(data)

    def _detect_format(self, data) -> str:
        """Return a format tag based on the shape of the JSON data."""
        if isinstance(data, list):
            return "generic_list"
        if isinstance(data, dict):
            if "chat_messages" in data:
                return "claude"
            if "mapping" in data:
                return "chatgpt"
        return "generic"

    # --- format-specific parsers ---

    def _parse_generic_list(self, data: list) -> List[ChatMessage]:
        """Parse a top-level JSON array of message objects."""
        messages = []
        for item in data:
            if not isinstance(item, dict):
                continue
            role = item.get("role", "user")
            content = item.get("content", "")
            if isinstance(content, list):
                content = " ".join(str(p) for p in content)
            if content:
                messages.append(ChatMessage(role=role, content=str(content)))
        return messages

    def _parse_generic(self, data: dict) -> ChatSession:
        """Parse the standard generic format: {"messages": [...]}."""
        title = data.get("title", data.get("name", ""))
        raw_messages = data.get("messages", [])
        messages = []
        for item in raw_messages:
            if not isinstance(item, dict):
                continue
            role = item.get("role", "user")
            content = item.get("content", "")
            if isinstance(content, list):
                # OpenAI-style content array
                content = " ".join(
                    p.get("text", str(p)) if isinstance(p, dict) else str(p)
                    for p in content
                )
            if content:
                messages.append(ChatMessage(role=role, content=str(content)))
        return ChatSession(title=str(title), messages=messages)

    def _parse_claude(self, data: dict) -> ChatSession:
        """Parse Anthropic/Claude conversation export format."""
        title = data.get("name", data.get("title", ""))
        raw_messages = data.get("chat_messages", [])
        messages = []
        for item in raw_messages:
            if not isinstance(item, dict):
                continue
            sender = item.get("sender", item.get("role", "user"))
            # Claude uses "human" / "assistant"
            role = "user" if sender in ("human", "user") else "assistant"
            content = item.get("text", item.get("content", ""))
            if content:
                messages.append(ChatMessage(role=role, content=str(content)))
        return ChatSession(title=str(title), messages=messages)

    def _parse_chatgpt(self, data: dict) -> ChatSession:
        """Parse ChatGPT conversation export format (mapping-based)."""
        title = data.get("title", "")
        mapping = data.get("mapping", {})
        messages: List[ChatMessage] = []

        # The mapping is an unordered dict; reconstruct the chain via parent refs.
        # Build a list sorted by a stable traversal (children of the root node).
        nodes = {}
        root_id = None
        for node_id, node in mapping.items():
            nodes[node_id] = node
            if node.get("parent") is None:
                root_id = node_id

        # Walk the conversation tree depth-first, following only the first child
        # at each node. ChatGPT exports use a tree structure to represent
        # conversation branches (edits/regenerations); the main conversation
        # line is always the first child of each node. Branching conversations
        # are silently ignored – only the primary thread is extracted.
        ordered_ids: List[str] = []
        stack = [root_id] if root_id else list(mapping.keys())[:1]
        while stack:
            nid = stack.pop(0)
            ordered_ids.append(nid)
            children = mapping.get(nid, {}).get("children", [])
            stack = children[:1] + stack  # first child = main conversation line

        for nid in ordered_ids:
            node = mapping.get(nid, {})
            msg = node.get("message")
            if not msg:
                continue
            role = msg.get("role", "user")
            if role not in ("user", "assistant", "system"):
                continue
            content_obj = msg.get("content", {})
            if isinstance(content_obj, str):
                content = content_obj
            elif isinstance(content_obj, dict):
                parts = content_obj.get("parts", [])
                content = " ".join(str(p) for p in parts if p)
            else:
                content = str(content_obj)
            if content:
                messages.append(ChatMessage(role=role, content=content))

        return ChatSession(title=str(title), messages=messages)

    # --- conversion to Document ---

    def _session_to_document(self, session: ChatSession, source_path: str) -> Document:
        """
        Convert a ChatSession into a Document for the distillation pipeline.

        The conversation is organised into sections by speaker turn so the
        existing chunking algorithms receive well-structured input.
        """
        sections: List[Section] = []
        full_text_parts: List[str] = []

        if session.title:
            full_text_parts.append(f"# {session.title}\n")

        for i, msg in enumerate(session.messages):
            role_label = "User" if msg.role == "user" else "Assistant"
            section_title = f"Turn {i + 1}: {role_label}"
            sections.append(Section(
                title=section_title,
                content=msg.content,
                level=2,
            ))
            full_text_parts.append(f"## {section_title}\n\n{msg.content}")

        full_text = "\n\n".join(full_text_parts)

        if not sections:
            sections = [Section(title="Chat Session", content="", level=1)]

        return Document(
            content=full_text,
            structure=sections,
            metadata={
                "title": session.title,
                "turn_count": len(session.messages),
                "source_format": "chat_session",
            },
            source_type="chat_session",
            source_path=source_path,
        )

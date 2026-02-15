# PDF2EPUB Converter

A professional PDF to EPUB conversion tool that transforms PDF documents into accessible EPUB format while preserving formatting, images, and structure.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
  - [Basic Usage](#basic-usage)
  - [Command-Line Options](#command-line-options)
  - [Usage Examples](#usage-examples)
- [Output Quality](#output-quality)
- [Troubleshooting](#troubleshooting)

---

## Overview

This tool converts PDF files into EPUB format, making them more accessible and easier to read on e-readers, tablets, and mobile devices. The converter maintains the original document's visual quality including covers, images, tables, and formatting.

---

## Features

- ✅ **High-Quality Conversion**: Preserves original PDF formatting and visual elements
- ✅ **Flexible Output**: Single EPUB or chapter-by-chapter conversion
- ✅ **Index Management**: Optional preservation of PDF table of contents
- ✅ **Visual Elements**: Maintains covers, figures, images, and tables
- ✅ **Progress Tracking**: Real-time conversion status updates
- ✅ **Error Handling**: Comprehensive validation and user-friendly error messages

---

## Requirements

- Python 3.x
- Required Python packages (see `requirements.txt`)

---

## Installation

```bash
# Clone the repository
git clone https://github.com/EnigmaWU/MyLLM_Arena.git

# Navigate to the project directory
cd MyLLM_Arena/MyStartups/PDF2EPUB

# Install dependencies
pip install -r requirements.txt
```

---

## Usage

### Basic Usage

```bash
python3 myPdf2Epub.py --input <input_pdf_file> [--output <output_epub_file>]
```

If `--output` is not specified, the output file will use the same name as the input file with `.epub` extension.

### Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--input` | **[Required]** Path to the input PDF file | — |
| `--output` | **[Optional]** Path to the output EPUB file | `<input_name>.epub` |
| `--keepIndex` | Preserve the original PDF's table of contents/index | Disabled (index skipped) |
| `--chapter-by-chapter` | Generate separate EPUB files for each chapter | Disabled (all-in-one file) |

### Usage Examples

**Example 1: Basic conversion**
```bash
python3 myPdf2Epub.py --input LLMOps.pdf
# Output: LLMOps.epub
```

**Example 2: Specify output filename**
```bash
python3 myPdf2Epub.py --input LLMOps.pdf --output MyBook.epub
# Output: MyBook.epub
```

**Example 3: Keep original index/table of contents**
```bash
python3 myPdf2Epub.py --input LLMOps.pdf --keepIndex
# Output: LLMOps.epub (with index preserved)
```

**Example 4: Convert chapter by chapter**
```bash
python3 myPdf2Epub.py --input LLMOps.pdf --chapter-by-chapter
# Output: LLMOps_Chapter1.epub, LLMOps_Chapter2.epub, ...
```

**Example 5: Combined options**
```bash
python3 myPdf2Epub.py --input LLMOps.pdf --output MyBook.epub --keepIndex --chapter-by-chapter
# Output: MyBook_Chapter1.epub, MyBook_Chapter2.epub, ... (with indices)
```

---

## Output Quality

The converter ensures high-quality EPUB output by:

- **Visual Preservation**: Maintains covers, figures, images, and tables from the original PDF
- **Formatting Integrity**: Preserves text formatting, fonts, and layout structure
- **Progress Monitoring**: Displays work-in-progress log messages during conversion
- **Validation**: Checks file paths and arguments before processing
- **User Guidance**: Provides helpful error messages for incorrect usage

---

## Troubleshooting

### Common Issues

**Missing required arguments:**
```
Error: --input argument is required
Usage: python3 myPdf2Epub.py --input <input_pdf_file> [options]
```

**Invalid file path:**
```
Error: Input file not found: <filepath>
Please verify the file path and try again.
```

**For additional help:**
```bash
python3 myPdf2Epub.py --help
```

---

**Last Updated:** 2026-02-15  
**Version:** 1.0  
**License:** MIT

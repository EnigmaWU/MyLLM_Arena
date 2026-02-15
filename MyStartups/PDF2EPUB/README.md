# PDF2EPUB

- This project converts PDF files into EPUB format, making them more accessible and easier to read on various devices. 

## Usage Design

```bash
    $ python3 myPdf2Epub.py --input <input_pdf_file> [--output <output_epub_file>]
    #such as $ python3 myPdf2Epub.py --input LLMOps.pdf [--output LLMOps.epub]
```

### Additional Options

- `--keepIndex`: Keep the original PDF's index in the EPUB file which is SKIPPED by default.
- `--chapter-by-chapter`: Convert the PDF into separate EPUB files for each chapter, which is ALL-IN-ONE by default.

### Extra Notes

- include 'usage help' messages in the output to guide users on not correct usage such as:
  - missing required arguments or invalid file paths.
- include 'Work-in-Progress' log messages in the output to track the conversion process.
- include 'Cover' and 'Figure/Image/Table/...' existing in original PDF, which means, good format as PDF.

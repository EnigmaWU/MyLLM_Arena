# SplitPdfChapters

- INPUT: PDF file with chapters, such as a book;
- OUTPUT: Separate PDF files for each chapter,
  - save each chapter as a separate PDF file,
  - name the files with PDF file name + chapter index + chapter title.

## Usage Design

```bash
    $ python3 mySplitPdfChapters.py --input <input_pdf_file> [--output <output_directory>]
```

## Requirements

```bash
    $ pip install -r requirements.txt
```

## Notes

- The script detects chapter headings using a regex (default: `chapter|chap` + number).
- Override with `--pattern` if your PDF uses a different format.
- Use `--include-front-matter` to save pages before the first chapter as a separate PDF.


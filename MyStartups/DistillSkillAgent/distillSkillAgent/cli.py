"""
CLI interface for myDistillSkillAgent
"""

import argparse
import sys
import os
from pathlib import Path
from typing import List
import glob

from .parsers import SourceParser
from .distiller import SkillDistiller
from .formatters import (
    AnthropicSkillFormatter,
    ContinueSlashCMDFormatter,
    save_skills_json
)


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="myDistillSkillAgent - Extract and transplant skills from various sources",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract skills from PDF and generate both formats
  myDistillSkillAgent --input BDD.pdf \\
    --output-claude-skill BDD-ExecutableSpec \\
    --output-continue-slash-command bdd-spec.md

  # Extract from web article
  myDistillSkillAgent --input https://martinfowler.com/articles/refactoring.html \\
    --output-claude-skill Refactoring

  # Batch process multiple files
  myDistillSkillAgent --input "books/*.pdf" --output-claude-skill

  # Inspect intermediate JSON
  myDistillSkillAgent --input CleanCode.pdf --output-json skills.json --verbose
        """
    )
    
    parser.add_argument(
        "--input",
        required=True,
        help="Input source: path to file (.pdf, .md, .txt) or URL (http://...)"
    )
    
    parser.add_argument(
        "--output-claude-skill",
        metavar="NAME",
        nargs='?',
        const='skill',
        help="Generate Anthropic SKILL package (.zip). Optional: specify custom name."
    )
    
    parser.add_argument(
        "--output-continue-slash-command",
        metavar="PATH",
        help="Generate Continue slash command (.md). Specify output path."
    )
    
    parser.add_argument(
        "--output-json",
        metavar="PATH",
        help="Save intermediate skill representation as JSON for inspection/editing."
    )
    
    parser.add_argument(
        "--llm",
        choices=["anthropic", "openai", "mockSrvLLM_OpenAI", "local"],
        default="anthropic",
        help="LLM provider to use for skill extraction (default: anthropic)"
    )
    
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed progress during extraction"
    )
    
    return parser.parse_args()


def expand_input_files(input_pattern: str) -> List[str]:
    """Expand glob patterns and comma-separated files."""
    # Check for comma-separated list
    if ',' in input_pattern:
        files = [f.strip() for f in input_pattern.split(',')]
        return files
    
    # Check for glob pattern
    if '*' in input_pattern or '?' in input_pattern:
        matched = glob.glob(input_pattern, recursive=True)
        if not matched:
            print(f"Warning: No files matched pattern: {input_pattern}", file=sys.stderr)
            return []
        return matched
    
    # Single file or URL
    return [input_pattern]


def process_single_source(
    source: str,
    args,
    parser: SourceParser,
    distiller: SkillDistiller
) -> bool:
    """Process a single input source."""
    try:
        if args.verbose:
            print(f"\n{'='*60}")
            print(f"Processing: {source}")
            print(f"{'='*60}")
        
        # Parse input
        if args.verbose:
            print("Parsing input...")
        document = parser.parse(source)
        if args.verbose:
            print(f"  ✓ Parsed {document.source_type} document")
        
        # Distill skills
        skills = distiller.distill(document, verbose=args.verbose)
        
        if not skills:
            print(f"Warning: No skills extracted from {source}", file=sys.stderr)
            if args.verbose:
                print("  Suggestions:", file=sys.stderr)
                print("    • Check if document contains actionable content", file=sys.stderr)
                print("    • Try a different source document", file=sys.stderr)
                print("    • Review extraction with --output-json", file=sys.stderr)
            return False
        
        # Determine output directory
        output_dir = os.getenv("OUTPUT_DIR", ".")
        
        # Generate outputs
        outputs_created = []
        
        # Save JSON if requested
        if args.output_json:
            json_path = args.output_json
            if len(expand_input_files(args.input)) > 1:
                # Multi-file: generate unique names
                base_name = Path(source).stem
                json_path = str(Path(output_dir) / f"{base_name}.json")
            
            save_skills_json(skills, json_path)
            outputs_created.append(f"JSON: {json_path}")
            if args.verbose:
                print(f"  ✓ Generated: {json_path}")
        
        # Generate Anthropic SKILL package
        if args.output_claude_skill is not None:
            skill_name = args.output_claude_skill
            if skill_name == 'skill' or len(expand_input_files(args.input)) > 1:
                # Use source filename as base
                skill_name = Path(source).stem
            
            zip_path = str(Path(output_dir) / skill_name)
            
            formatter = AnthropicSkillFormatter()
            # Format first skill (or could generate multiple)
            output_path = formatter.format(skills[0], zip_path)
            outputs_created.append(f"Anthropic SKILL: {output_path}")
            if args.verbose:
                print(f"  ✓ Generated: {output_path}")
        
        # Generate Continue slash command
        if args.output_continue_slash_command:
            slash_path = args.output_continue_slash_command
            if len(expand_input_files(args.input)) > 1:
                # Multi-file: generate unique names
                base_name = Path(source).stem
                slash_path = str(Path(output_dir) / f"{base_name}-slash.md")
            
            formatter = ContinueSlashCMDFormatter()
            # Format first skill (or could generate multiple)
            output_path = formatter.format(skills[0], slash_path)
            outputs_created.append(f"Continue Slash CMD: {output_path}")
            if args.verbose:
                print(f"  ✓ Generated: {output_path}")
        
        # Print summary
        if outputs_created:
            print(f"✓ {source}: {len(skills)} skills extracted")
            for output in outputs_created:
                print(f"    {output}")
        
        return True
    
    except FileNotFoundError as e:
        print(f"Error: File not found: {source}", file=sys.stderr)
        print(f"Suggestion: Check that the path is correct and the file exists.", file=sys.stderr)
        return False
    
    except ValueError as e:
        error_msg = str(e).lower()
        if "unsupported" in error_msg or "format" in error_msg:
            print(f"Error: Unsupported file format: {source}", file=sys.stderr)
            print(f"Supported formats: .pdf, .md, .txt, or URLs (http://...)", file=sys.stderr)
        else:
            print(f"Error: {e}", file=sys.stderr)
        return False
    
    except PermissionError as e:
        print(f"Error: Permission denied: {source}", file=sys.stderr)
        print(f"Suggestion: Check file permissions or try running with appropriate access rights.", file=sys.stderr)
        return False
    
    except Exception as e:
        error_msg = str(e).lower()
        if "network" in error_msg or "connection" in error_msg or "timeout" in error_msg:
            print(f"Error: Network error while processing {source}: {e}", file=sys.stderr)
            print(f"Suggestion: Check your internet connection and try again.", file=sys.stderr)
        elif "api" in error_msg or "anthropic" in error_msg or "openai" in error_msg:
            print(f"Error: API failure: {e}", file=sys.stderr)
            print(f"Suggestion: Check your API key and rate limits.", file=sys.stderr)
        else:
            print(f"Error processing {source}: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return False


def main():
    """Main CLI entry point."""
    args = parse_args()
    
    # Validate that at least one output format is specified
    if not any([args.output_claude_skill is not None,
                args.output_continue_slash_command,
                args.output_json]):
        print("Error: At least one output format must be specified:", file=sys.stderr)
        print("  --output-claude-skill, --output-continue-slash-command, or --output-json", file=sys.stderr)
        sys.exit(1)
    
    # Expand input files first (before initializing LLM client)
    sources = expand_input_files(args.input)
    
    if not sources:
        print(f"Error: No input files found matching: {args.input}", file=sys.stderr)
        print(f"Suggestion: Check the file path or glob pattern.", file=sys.stderr)
        sys.exit(1)
    
    # Validate input files exist (for non-URLs)
    for source in sources:
        if not source.startswith(('http://', 'https://')):
            if not os.path.exists(source):
                print(f"Error: File not found: {source}", file=sys.stderr)
                print(f"Suggestion: Check that the path is correct and the file exists.", file=sys.stderr)
                sys.exit(1)
            # Check if format is supported
            ext = os.path.splitext(source)[1].lower()
            if ext not in ['.pdf', '.md', '.txt', '']:
                print(f"Error: Unsupported file format: {source}", file=sys.stderr)
                print(f"Supported formats: .pdf, .md, .txt, or URLs (http://...)", file=sys.stderr)
                sys.exit(1)
    
    # Initialize parser
    parser = SourceParser()
    
    # Initialize distiller (may require API key)
    try:
        distiller = SkillDistiller(llm_provider=args.llm)
    except ValueError as e:
        # API key errors
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ImportError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Process sources
    if len(sources) > 1:
        print(f"Batch processing {len(sources)} files...")
        print()
    
    successes = 0
    failures = 0
    
    for source in sources:
        success = process_single_source(source, args, parser, distiller)
        if success:
            successes += 1
        else:
            failures += 1
    
    # Print batch summary
    if len(sources) > 1:
        print()
        print(f"{'='*60}")
        print(f"Summary: {successes} succeeded, {failures} failed")
        print(f"{'='*60}")
    
    # Exit with appropriate code
    sys.exit(0 if failures == 0 else 1)


if __name__ == "__main__":
    main()

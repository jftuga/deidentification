#!/usr/bin/env python3

"""Command line interface for the deidentification package."""

import argparse
import sys
from typing import TextIO

from . import __version__
from .deidentification import Deidentification, DeidentificationConfig, DeidentificationOutputStyle


def process_stream(input_stream: TextIO, config: DeidentificationConfig) -> str:
    """Process input stream and return de-identified text.

    Args:
        input_stream: File-like object to read from
        config: DeidentificationConfig instance with processing settings

    Returns:
        str: De-identified text
    """
    content = input_stream.read()
    deidentifier = Deidentification(config)
    
    if config.output_style == DeidentificationOutputStyle.HTML:
        return deidentifier.deidentify_with_wrapped_html(content)
    return deidentifier.deidentify(content)


def main() -> int:
    """Main entry point for the CLI.

    Returns:
        int: Exit code (0 for success, non-zero for failure)
    """
    parser = argparse.ArgumentParser(
        description="De-identify personally identifiable information in text files"
    )
    
    parser.add_argument(
        "input_file",
        help="text file to deidentify (use '-' for STDIN)",
        metavar="input_file"
    )
    
    parser.add_argument(
        "-r",
        "--replacement",
        default="PERSON",
        help="a word/phrase to replace identified names with (default: PERSON)",
        metavar="REPLACEMENT"
    )
    
    parser.add_argument(
        "-o",
        "--output",
        help="output file (if not specified, prints to STDOUT)",
        metavar="OUTPUT_FILE"
    )
    
    parser.add_argument(
        "-H",
        "--html",
        action="store_true",
        help="output in HTML format"
    )
    
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="display program version and then exit"
    )
    
    args = parser.parse_args()

    # Configure deidentification settings
    config = DeidentificationConfig(
        replacement=args.replacement,
        output_style=DeidentificationOutputStyle.HTML if args.html else DeidentificationOutputStyle.TEXT
    )

    try:
        # Handle input
        if args.input_file == "-":
            result = process_stream(sys.stdin, config)
        else:
            with open(args.input_file, "r", encoding="utf-8") as f:
                result = process_stream(f, config)

        # Handle output
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(result)
        else:
            print(result)

        return 0

    except FileNotFoundError:
        print(f"Error: Could not find input file: {args.input_file}", file=sys.stderr)
        return 1
    except PermissionError:
        print(f"Error: Permission denied accessing file: {args.input_file}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
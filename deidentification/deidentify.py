#!/usr/bin/env python3

"""Command line interface for the deidentification package."""

import argparse
import json
import os
import sys
from io import StringIO
from typing import TextIO

from . import __version__
from .deidentification import Deidentification, DeidentificationConfig, DeidentificationOutputStyle
from .deidentification_constants import pgmUrl
from .file_detection import read_file_with_detection

DEIDENTIFY_EXCLUDE_DELIM = os.environ.get('DEIDENTIFY_EXCLUDE_DELIM', ",")

def create_json_filename(input_file: str) -> str:
    """Creates the metadata JSON filename for a given input file.

    Takes an input filename and creates a corresponding metadata filename
    by replacing the original extension with "--tokens.json".

    Args:
        input_file (str): Original input file path

    Returns:
        str: Path for the metadata JSON file.
            Example: "text.txt" -> "text--tokens.json"

    Note:
        Preserves the original file path, only modifies the extension.
    """
    filename, _ = os.path.splitext(input_file)
    return filename + "--tokens.json"

def save_elements(filename: str, elements: dict):
    """Saves a dictionary of elements to a JSON file with UTF-8 encoding.

    Args:
        filename (str): The base filename to save to. Will be converted to a JSON
            filename using create_json_filename().
        elements (dict): Dictionary containing the elements to save. Values that
            aren't JSON-serializable will be converted to strings.

    Returns:
        None
    """
    outfile = create_json_filename(filename)
    with open(outfile, "w", encoding="utf-8") as fp:
        fp.write(json.dumps(elements, indent=4, default=str))


def process_stream(input_stream: TextIO, config: DeidentificationConfig) -> str:
    """Process input stream and return de-identified text.

    Args:
        input_stream: File-like object to read from
        config: DeidentificationConfig instance with processing settings

    Returns:
        str: The deidentified content as a string. If HTML output style is specified in the config,
            the content will include HTML markup around deidentified elements.

    Note:
        If config.save_tokens is True, identified elements will be saved to a JSON file
        using the filename specified in the config.
    """
    content = input_stream.read()
    deidentifier = Deidentification(config)

    func = deidentifier.deidentify_with_wrapped_html if config.output_style == DeidentificationOutputStyle.HTML else deidentifier.deidentify
    content = func(content)
    if config.save_tokens:
        elements = deidentifier.get_identified_elements()
        save_elements(config.filename, elements)
    return content


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
        version=f"%(prog)s {__version__} : {pgmUrl}",
        help="display program version and then exit"
    )

    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        default=False,
        help="enable debug mode"
    )

    parser.add_argument(
        "-t",
        "--tokens",
        action="store_true",
        default=False,
        help="save identified elements to file ending in `--tokens.json`"
    )

    parser.add_argument(
        "-x",
        "--exclude",
        default=False,
        help="comma-delimited list of entities to exclude from de-identification; or change with DEIDENTIFY_EXCLUDE_DELIM env var"
    )

    args = parser.parse_args()

    # Configure deidentification settings
    excluded_entities = set()
    if args.exclude:
        excluded_entities = set(entity.lower().strip() for entity in args.exclude.split(DEIDENTIFY_EXCLUDE_DELIM))

    config = DeidentificationConfig(
        replacement=args.replacement,
        output_style=DeidentificationOutputStyle.HTML if args.html else DeidentificationOutputStyle.TEXT,
        debug = args.debug == True,
        save_tokens = args.tokens == True,
        excluded_entities = excluded_entities
    )

    try:
        # Handle input
        config.filename = args.input_file if args.input_file != "-" else "STDIN.txt"
        if args.debug:
            print(config, file=sys.stderr)

        if args.input_file == "-":
            result = process_stream(sys.stdin, config)
        else:
            file_contents, encoding = read_file_with_detection(args.input_file)
            if config.debug:
                print(f"DEBUG: Detected file encoding: {encoding}", file=sys.stderr)
            result = process_stream(StringIO(file_contents), config)

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
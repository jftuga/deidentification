# Deidentification

A Python module that removes personally identifiable information (PII) from text documents, focusing on personal names and gender-specific pronouns. This tool uses spaCy's Named Entity Recognition (NER) capabilities combined with custom pronoun handling to provide thorough text de-identification.

## Key Features

- Accurately identifies and replaces personal names using spaCy's NER
- Handles gender-specific pronouns with customizable replacements
- Supports both plain text and HTML output formats
- Uses an optimized backward-processing strategy for accurate text replacements
- Iterative processing ensures comprehensive PII removal
- Configurable replacement tokens and debug output
- GPU acceleration support through spaCy

## Installation

```bash
pip install text-deidentification

# or...

pip install git+https://github.com/jftuga/deidentification.git
```

### Requirements

- Python 3.10 or higher
- spaCy's `en_core_web_trf` model (or another compatible model)

Download the required spaCy model:
```bash
python -m spacy download en_core_web_trf
```

## Usage

### Command Line Interface

The package includes a command-line tool for quick de-identification of text files:

```bash
deidentify input_file [options]
# or:
python -m deidentification.deidentify input_file [options]
```

Options:
- `-r, --replacement TEXT`: Specify replacement text for identified names (default: "PERSON")
- `-o, --output FILE`: Output file (defaults to stdout)
- `-H, --html`: Output in HTML format with highlighted replacements
- `-d, --debug`: Enable debug mode
- `-t, --tokens`: Save identified elements to a JSON file (filename--tokens.json)
- `-x, --exclude EXCLUDE`: comma-delimited list of entities to exclude from de-identification; or change with `DEIDENTIFY_EXCLUDE_DELIM` env var
- `-v, --version`: Display version information

Example:
```bash
# De-identify a text file and save with HTML markup
deidentify input.txt -H -o output.html -r "[REDACTED]"
```

### Python API Usage

```python
from deidentification import Deidentification

# Create a deidentification instance with default settings
deidentifier = Deidentification()

# Process text
text = "John Smith went to the store. He bought some groceries."
deidentified_text = deidentifier.deidentify(text)
print(deidentified_text)
# Output: "PERSON went to the store. HE/SHE bought some groceries."
```

### HTML Output

```python
# Generate HTML output with highlighted replacements
html_output = deidentifier.deidentify_with_wrapped_html(text)
```

### HTML Output Demo

![deidentification html demo](deidentification-html-demo.png)

### Custom Configuration

```python
from deidentification import (
    Deidentification,
    DeidentificationConfig,
    DeidentificationOutputStyle,
)

config = DeidentificationConfig(
    spacy_model="en_core_web_trf",
    output_style=DeidentificationOutputStyle.HTML,
    replacement="[REDACTED]",
    excluded_entities={"Joe Smith","Alice Jones"},
    debug=True
)
deidentifier = Deidentification(config)
```

## Configuration Options

The `DeidentificationConfig` class supports the following options:

- `spacy_load` (bool): Whether to load the spaCy model (default: True)
- `spacy_model` (str): Name of the spaCy model to use (default: "en_core_web_trf")
- `output_style` (DeidentificationOutputStyle): Output format - TEXT or HTML (default: TEXT)
- `replacement` (str): Replacement text for identified names (default: "PERSON")
- `debug` (bool): Enable debug output (default: False)

## How It Works

The de-identification process follows these steps:

1. Text is normalized for consistent processing
2. spaCy processes the text to identify person entities
3. Gender-specific pronouns are identified using a predefined list
4. Entities and pronouns are sorted by their position in reverse order
5. Replacements are made from end to beginning to maintain position accuracy
6. The process repeats until no new entities are detected

The backward-processing strategy is key to accurate replacements, as it prevents position shifts from affecting subsequent replacements.

## Debug Output

When debug mode is enabled, the tool provides detailed information about:
- Identified person entities
- Found pronouns
- Replacement positions and actions
- Processing iterations

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

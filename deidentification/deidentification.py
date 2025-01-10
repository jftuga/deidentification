r"""
deidentification.py
-John Taylor
2024-12-31

This module provides text de-identification capabilities by removing personally identifiable
information (PII) such as names and gender-specific pronouns from text documents. It uses
spaCy's Named Entity Recognition (NER) for identifying person names and includes custom logic
for handling gender pronouns.

The deidentification process works through multiple passes to ensure thorough PII removal.
It first identifies all person entities using spaCy's NER, then locates gender-specific
pronouns. The critical innovation in this implementation is its backward-merging strategy:
rather than processing the text from start to finish, it sorts all identified entities and
pronouns by their position and processes them from end to beginning. This backwards approach
is optimal because string replacements can alter the character positions of subsequent
entities when text lengths change. By working backwards, each replacement's character
positions remain valid since they haven't been affected by previous replacements. The process
iteratively continues until no new person entities are detected, ensuring comprehensive
de-identification even in cases where entity recognition might improve after initial
replacements. The module supports both plain text and HTML output formats, with the latter
providing visual highlighting of replacements through span tags.
"""

from dataclasses import dataclass, fields
from io import StringIO
from operator import itemgetter
from typing import Any, BinaryIO, Optional, Union
from .deidentification_constants import bcolors, GENDER_PRONOUNS, HTML_BEGIN, HTML_END
from .deidentification_constants import pgmName, pgmUrl, pgmVersion, DeidentificationOutputStyle, DeidentificationLanguages
from .normalize_punctuation import normalize_punctuation
import spacy
from spacy.tokens import Doc
import sys

@dataclass
class DeidentificationConfig:
    spacy_load: bool = True
    spacy_model: str = "en_core_web_trf"
    output_style: DeidentificationOutputStyle = DeidentificationOutputStyle.TEXT
    language: DeidentificationLanguages = DeidentificationLanguages.ENGLISH
    replacement: str = DeidentificationLanguages.ENGLISH.value
    debug: bool = False
    save_tokens: bool = False
    filename: Optional[str] = None
    excluded_entities: set[str] = None

    def __str__(self) -> str:
        return "\n".join(f"- {field.name:<15} = {getattr(self, field.name)}"
                         for field in fields(self))

class Deidentification:
    nlp: Optional[spacy.language.Language] = None

    def __init__(self, config: DeidentificationConfig = DeidentificationConfig()):
        """Initialize the Deidentification instance.

        Args:
            config (DeidentificationConfig, optional): Configuration settings for the
                de-identification process. Defaults to DeidentificationConfig().
        """
        self.config = config
        if self.config.excluded_entities is not None:
            self.config.excluded_entities = {entity.lower() for entity in self.config.excluded_entities}

        self.table_class  = None

        if self.config.debug:
            from veryprettytable import VeryPrettyTable
            self.table_class = VeryPrettyTable

        if self.config.spacy_load:
            import torch
            self.original_load = torch.load
            torch.load = self.__safe_load
            spacy.prefer_gpu()
            if not Deidentification.nlp:
                try:
                    Deidentification.nlp = spacy.load(self.config.spacy_model)
                except OSError as err:
                    self.model_not_found_error(str(err))
                except Exception as err:
                    raise err

    def _reset(self):
        """Resets all instance variables to their initial state.

        Initializes or clears various tracking lists and document references used during
        the deidentification process. This includes lists for storing person mentions,
        pronouns, and the spaCy Doc object.

        Attributes:
            all_persons (list[dict]): Stores person entities found in current pass.
            aggregate_persons (list[dict]): Accumulates person entities across multiple passes.
            aggregate_pronouns (list[dict]): Accumulates pronouns across multiple deidentification iterations.
            all_pronouns (list[dict]): Stores pronouns found in current pass.
            doc (Optional[Doc]): Reference to the spaCy Doc object being processed.
            replaced_text (Optional[str]): Stores the text after replacement operations.
        """
        self.all_persons: list[dict] = []

        # this combines all self.all_persons lists from multiple passes of self._find_all_persons()
        self.aggregate_persons: list[dict] = []

        # this combines all self.all_pronouns lists from multiple loop iterations in self.deidentify()
        self.aggregate_pronouns: list[dict] = []

        self.all_pronouns: list[dict] = []
        self.doc: Optional[Doc] = None

        # used by self.get_identified_elements()
        self.replaced_text = None

    def __str__(self) -> str:
        """Return a string representation of the Deidentification instance.

        Args:
            None

        Returns:
            str: A formatted string showing program info and configuration settings.
        """
        program_info = [
            f"- {'name':<15} = {pgmName}",
            f"- {'version':<15} = {pgmVersion}",
            f"- {'url':<15} = {pgmUrl}",
        ]
        return "\n".join(program_info) + "\n" + str(self.config)

    def model_not_found_error(self, err: str):
        """Handles errors related to missing spaCy models and provides installation instructions.

        This function processes spaCy model errors, specifically handling cases where
        a required model cannot be found. If the error indicates a missing model,
        it prints installation instructions to stderr and exits the program.

        Args:
            err: Error message string from the spaCy library.
        """
        print(file=sys.stderr)
        print(str(err), file=sys.stderr)
        if "Can't find model" in str(err):
            print(file=sys.stderr)
            print("Please manually run the following command one time to download the required 500 MB model:", file=sys.stderr)
            print(file=sys.stderr)
            print(f"python -m spacy download {self.config.spacy_model}", file=sys.stderr)
            print(file=sys.stderr)
            sys.exit(1)

    def deidentify(self, text: str) -> str:
        """De-identify personal information in the input text.

        Processes the input text to identify and replace personal names and gender pronouns.
        Iteratively processes the text until no more entities are detected.

        Args:
            text (str): The input text to be de-identified.

        Returns:
            str: The de-identified text with personal information replaced.
        """
        self._reset()

        self.text = normalize_punctuation(text)
        self.doc = Deidentification.nlp(self.text)
        initial_persons_count = self._find_all_persons()
        if self.config.debug:
            self.__debug_log(f"deidentify(): first iter, persons={len(self.all_persons)}")
        self._find_all_pronouns()
        self.aggregate_pronouns.extend(self.all_pronouns)

        if self.config.debug:
            self.__print_entities_table(self.all_persons)
            self.__print_entities_table(self.all_pronouns)

        merged = self._merge_metadata()
        replaced_text = self._replace_merged(self.text, merged)

        # To catch any missing persons, rerun until no more entities are detected
        persons_count = initial_persons_count
        while persons_count > 0:
            self.doc = Deidentification.nlp(replaced_text)
            persons_count = self._find_all_persons()
            if self.config.debug:
                self.__debug_log(f"deidentify(): next iter, persons={len(self.all_persons)}")
            if persons_count == 0:
                break
            self.all_pronouns = []
            merged = self._merge_metadata()
            replaced_text = self._replace_merged(replaced_text, merged)

        self.replaced_text = replaced_text
        return replaced_text

    def deidentify_with_wrapped_html(self, text: str, html_begin: str = HTML_BEGIN, html_end:str = HTML_END) -> str:
        """De-identify text and wrap the result in HTML.

        Args:
            text (str): The input text to be de-identified.
            html_begin (str, optional): Opening HTML content. Defaults to HTML_BEGIN.
            html_end (str, optional): Closing HTML content. Defaults to HTML_END.

        Returns:
            str: HTML-formatted de-identified text.
        """
        self.config.output_style = DeidentificationOutputStyle.HTML
        buffer = StringIO()
        buffer.write(html_begin)
        body = self.deidentify(text)
        body = body.replace("\n", "<br />\n")
        buffer.write(body)
        buffer.write(html_end)
        return buffer.getvalue()

    def get_identified_elements(self) -> dict:
        elements = {"message": self.text, "entities": self.aggregate_persons, "pronouns": self.aggregate_pronouns}
        return elements

    def _find_all_persons(self) -> int:
        """Find all person entities in the current document.

        Uses spaCy's named entity recognition to identify person names.

        Returns:
            int: Number of person entities found (-1 if document is empty).
        """
        if not len(self.doc):
            return -1

        # Clear out any previous persons
        self.all_persons = []

        for ent in self.doc.ents:
            if "PERSON" == ent.label_ and ent.text.lower().strip() not in self.config.excluded_entities:
                # When this function is run a second time, skip replacing PERSON
                # this is done because sometimes not all persons are found only
                # on one iteration by spaCy
                if ent.text == self.config.replacement:
                    continue
                record = {"text": ent.text, "start_char": ent.start_char, "end_char": ent.end_char, "label": ent.label_, "shapes": [token.shape_ for token in ent]}
                self.all_persons.append(record)
        self.aggregate_persons.extend(self.all_persons)
        return len(self.all_persons)

    def _find_all_pronouns(self) -> int:
        """Find all gender pronouns in the current document.

        Identifies pronouns and proper nouns that match known gender pronouns.

        Returns:
            int: Number of pronouns found (-1 if document is empty).
        """
        if not len(self.doc):
            return -1

        # Clear out any previous pronouns
        self.all_pronouns = []

        # self.config.language equals something like: DeidentificationLanguages.ENGLISH
        gender_keys = GENDER_PRONOUNS[self.config.language].keys()
        for token in self.doc:
            if (token.pos_ == "PRON" or token.pos_ == "PROPN") and token.text.lower() in gender_keys:
                record = {"text": token.text, "start_char": token.idx, "end_char": token.idx + len(token.text) - 1, "label": token.pos_, "shapes": [token.shape_]}
                self.all_pronouns.append(record)
        return len(self.all_pronouns)

    def _merge_metadata(self) -> list[dict]:
        """Merge person entities and pronouns metadata into a single sorted list.

        Creates a unified list of all identified entities and pronouns, sorted by
        their position in the text.

        Returns:
            list[dict]: Merged list of entity and pronoun metadata.
        """
        # Initialize counters for each type
        p = 0  # pronouns
        e = 0  # entities
        m = 0  # missed

        # Clear any existing merged data
        merged = []

        # All lists are empty
        if not (self.all_persons or self.all_pronouns):
            return []

        sorted_misses = []
        sorted_all_persons = sorted(self.all_persons, key=itemgetter("start_char"), reverse=True)
        sorted_all_pronouns = sorted(self.all_pronouns, key=itemgetter("start_char"), reverse=True)

        # Continue until we've processed all items
        while e < len(sorted_all_persons) or p < len(sorted_all_pronouns) or m < len(sorted_misses):
            # Get current positions for each type (use None if exhausted)
            persons_pos = sorted_all_persons[e]["start_char"] if e < len(sorted_all_persons) else None
            pronoun_pos = sorted_all_pronouns[p]["start_char"] if p < len(sorted_all_pronouns) else None

            # Find the highest position among non-None values
            positions = []
            if persons_pos is not None:
                positions.append(("entity", persons_pos, e))
            if pronoun_pos is not None:
                positions.append(("pronoun", pronoun_pos, p))

            if not positions:  # shouldn't happen but safe to check
                break

            # Sort positions to find highest
            positions.sort(key=lambda x: x[1], reverse=True)
            next_type, _, idx = positions[0]
            if self.config.debug:
                self.__debug_log(f"_merge_metadata(): {next_type=} {idx=}")

            # Add the item with the highest position
            if next_type == "entity":
                merged.append({
                    "type": "entity",
                    "index": e,
                    "item": sorted_all_persons[e]
                })
                e += 1
            elif next_type == "pronoun":
                merged.append({
                    "type": "pronoun",
                    "index": p,
                    "item": sorted_all_pronouns[p]
                })
                p += 1
            else:  # miss
                merged.append({
                    "type": "miss",
                    "index": m,
                    "item": sorted_misses[m]
                })
                m += 1

        if self.config.debug:
            self.__debug_log(f"_merge_metadata(): {merged=}")
        return merged

    def _replace_merged(self, replaced_text: str, merged: list[dict]) -> str:
        """Replace identified entities and pronouns in the text.

        Args:
            replaced_text (str): The original text to perform replacements on.
            merged (list[dict]): List of merged entity and pronoun metadata.

        Returns:
            str: Text with all identified entities and pronouns replaced.
        """
        want_html = self.config.output_style == DeidentificationOutputStyle.HTML
        position = 0
        for obj in merged:
            text = obj["item"]["text"]
            if obj["type"] == "pronoun":
                position = obj["item"]["start_char"]
            elif obj["type"] == "entity":
                position = obj["item"]["start_char"]
            if self.config.debug:
                self.__debug_log(f"_replace_merged(): {obj['type']=}, {position=}, {text=}")

        for obj in merged:
            if obj["type"] == "pronoun":
                start = obj["item"]["start_char"]
                end = start + len(obj["item"]["text"])
                anon = GENDER_PRONOUNS[self.config.language][obj["item"]["text"].lower()]
                if want_html and len(anon):
                    anon = f'<span id="span1">{anon}</span>'
                replaced_text = replaced_text[:start] + anon + replaced_text[end:]
            elif obj["type"] == "entity":
                start = obj["item"]["start_char"]
                end = obj["item"]["end_char"]
                bold_replacement = f'<span id="span2">{self.config.replacement}</span>' if want_html else self.config.replacement
                replaced_text = replaced_text[:start] + bold_replacement + replaced_text[end:]
            elif obj["type"] == "miss":
                start = obj["item"]["start_char"]
                end = start + len(obj["item"]["text"])
                highlighted = f'<span id="span3">{obj["item"]["text"]}</span>' if want_html else self.config.replacement
                replaced_text = replaced_text[:start] + highlighted + replaced_text[end:]
            else:
                self.__debug_log(f"_replace_merged(): unknown object type: {obj['type']}")
                return ""
        return replaced_text

    def __safe_load(self, file: Union[str, BinaryIO], *args: Any, **kwargs: Any) -> Any:
        """A patched version of `torch.load` that sets `weights_only=True` by default.

        This function addresses a security-related change in PyTorch where the
        default behavior of `torch.load` will eventually flip to `weights_only=True`
        to prevent the loading of arbitrary pickle data, which can be exploited
        to execute malicious code. By explicitly setting `weights_only=True`, this
        function ensures compatibility with the future default and mitigates
        potential security risks when loading untrusted models.

        Args:
            file (Union[str, BinaryIO]): The file path or file-like object
                from which to load the model state dictionary.
            *args (Any): Additional positional arguments passed to `torch.load`.
            **kwargs (Any): Additional keyword arguments passed to `torch.load`.

        Returns:
            Any: The result of loading the file, typically a PyTorch model state
            dictionary or weights, depending on the use case.
        """
        kwargs['weights_only'] = True
        return self.original_load(file, *args, **kwargs)

    def __print_entities_table(self, data: list[dict]) -> None:
        """Print a formatted table of entity or pronoun data for debugging.

        Creates and prints a color-coded table showing details of identified entities
        or pronouns, including their text, character positions, labels, and shapes.
        Only prints if debug mode is enabled and table_class is available.

        Args:
            data (list[dict]): List of entity or pronoun dictionaries containing:
                - text: The identified text
                - start_char: Starting character position
                - end_char: Ending character position
                - label: Entity or pronoun label
                - shapes: Token shapes from spaCy

        Returns:
            None
        """
        if not self.config.debug or not self.table_class or not self.doc:
            return

        table_entities = self.table_class()
        table_entities.align = "l"
        table_entities.field_names = ["text", "start_char", "end_char", "label", "shapes"]

        for ent in data:
            table_entities.add_row([
                f"{bcolors.OKGREEN}{ent["text"]}{bcolors.ENDC}",
                f"{bcolors.OKCYAN}{ent["start_char"]}{bcolors.ENDC}",
                f"{bcolors.OKBLUE}{ent["end_char"]}{bcolors.ENDC}",
                f"{bcolors.FAIL}{ent["label"]}{bcolors.ENDC}",
                f"{bcolors.WARNING}{" ".join(ent["shapes"])}{bcolors.ENDC}",
            ])
        print(table_entities, file=sys.stderr)

    def __debug_log(self, message: str) -> None:
        """Internal utility method for debug logging.

        Args:
            message: The debug message to log.
        """
        if self.config.debug:
            print(f"DEBUG: {message}", file=sys.stderr)

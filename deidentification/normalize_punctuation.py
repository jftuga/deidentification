def normalize_punctuation(text: str) -> str:
    """Normalizes Unicode variants of common punctuation marks to their ASCII equivalents.

    Converts various Unicode punctuation marks to their basic ASCII counterparts:
    - Converts typographic apostrophes (U+2019, U+2018, etc.) to ASCII apostrophe (U+0027)
    - Converts en dashes, em dashes, and other hyphens to ASCII hyphen-minus (U+002D)
    - Converts curly quotes to straight quotes (U+0022)
    - Converts ellipsis character to three periods
    - Converts various spaces to regular space
    - Converts bullet points to asterisk
    - Preserves but normalizes common symbols (©, ®, ™)

    Args:
        text: Input string containing possibly non-ASCII punctuation marks.

    Returns:
        A new string with all Unicode punctuation variants replaced with ASCII equivalents.

    Examples:
        >>> text = "Here's a fancy—text with "quotes" and bullets•"
        >>> normalize_punctuation(text)
        "Here's a fancy-text with \"quotes\" and bullets*"
    """
    # Dictionary mapping unicode variants to ASCII versions
    replacements = {
        # Apostrophe variants -> ASCII apostrophe (U+0027)
        chr(0x2019): "'",  # RIGHT SINGLE QUOTATION MARK
        chr(0x2018): "'",  # LEFT SINGLE QUOTATION MARK
        chr(0x02BC): "'",  # MODIFIER LETTER APOSTROPHE
        chr(0x02B9): "'",  # MODIFIER LETTER PRIME
        chr(0x0060): "'",  # GRAVE ACCENT
        chr(0x00B4): "'",  # ACUTE ACCENT

        # Hyphen variants -> ASCII hyphen-minus (U+002D)
        chr(0x2010): "-",  # HYPHEN
        chr(0x2011): "-",  # NON-BREAKING HYPHEN
        chr(0x2012): "-",  # FIGURE DASH
        chr(0x2013): "-",  # EN DASH
        chr(0x2014): "-",  # EM DASH
        chr(0x2015): "-",  # HORIZONTAL BAR
        chr(0x00AD): "-",  # SOFT HYPHEN
        chr(0x2212): "-",  # MINUS SIGN

        # Double quote variants -> ASCII double quote (U+0022)
        chr(0x201C): '"',  # LEFT DOUBLE QUOTATION MARK
        chr(0x201D): '"',  # RIGHT DOUBLE QUOTATION MARK
        chr(0x201F): '"',  # DOUBLE HIGH-REVERSED-9 QUOTATION MARK

        # Ellipsis -> three periods
        chr(0x2026): '...',  # HORIZONTAL ELLIPSIS

        # Space variants -> ASCII space
        chr(0x00A0): ' ',  # NO-BREAK SPACE
        chr(0x202F): ' ',  # NARROW NO-BREAK SPACE
        chr(0x2009): ' ',  # THIN SPACE
        chr(0x2007): ' ',  # FIGURE SPACE

        # Bullet variants -> asterisk
        chr(0x2022): '*',  # BULLET
        chr(0x2023): '*',  # TRIANGULAR BULLET
        chr(0x25E6): '*',  # WHITE BULLET
        chr(0x2043): '*',  # HYPHEN BULLET
        chr(0x00B7): '*',  # MIDDLE DOT
        chr(0x2219): '*',  # BULLET OPERATOR

        # Normalize common symbols
        chr(0x00A9): '(c)',  # COPYRIGHT SIGN
        chr(0x00AE): '(r)',  # REGISTERED SIGN
        chr(0x2122): '(tm)'  # TRADEMARK SIGN
    }

    # Replace each variant with its ASCII equivalent
    normalized_text = text
    for unicode_char, ascii_char in replacements.items():
        normalized_text = normalized_text.replace(unicode_char, ascii_char)

    return normalized_text

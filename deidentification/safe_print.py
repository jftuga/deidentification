import sys

def safe_print(data, is_error: bool = False):
    """Safely prints data to stdout or stderr while handling encoding issues.

    Converts input data to string and processes it through an encode/decode cycle
    to handle any problematic characters that might cause encoding errors.
    Characters that cannot be encoded are ignored rather than raising an error.

    Args:
        data: Data to print. Will be converted to string using str().
        is_error (bool, optional): If True, prints to stderr instead of stdout.
            Defaults to False.

    Note:
        Uses the current stdout encoding for both encode and decode operations.
        Silently ignores characters that cannot be encoded rather than failing.
    """
    dest = sys.stdout if not is_error else sys.stderr
    # can also use 'replace' instead of 'ignore' for errors= parameter
    print(str(data).encode(sys.stdout.encoding, errors='ignore').decode(sys.stdout.encoding), file=dest)


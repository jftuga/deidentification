
import chardet
import sys

def read_file_with_detection(filename: str) -> tuple[str, str|None]:
    """Detects file encoding and reads its contents in a single file read operation.

    Opens the file once in binary mode, uses the bytes for encoding detection,
    then decodes those same bytes using the detected encoding.

    Uses the chardet library to analyze the raw bytes of a file and determine its
    most likely character encoding (e.g., 'utf-8', 'ascii', 'windows-1252', etc.).

    Args:
        filename: Path to the file to read.

    Returns:
        A tuple containing (file_contents: str, detected_encoding: str).
        The file_contents will be decoded using the detected encoding.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        IOError: If there are issues reading the file.
        UnicodeDecodeError: If the content cannot be decoded with the detected encoding.
    """
    with open(filename, 'rb') as file:
        raw_bytes = file.read()

    detected_encoding = chardet.detect(raw_bytes)['encoding']
    all_encodings = (detected_encoding, "utf-8", "ascii", "cp1252", "latin1", "utf-16", "iso-8859-15", "iso-8859-1", "utf-32", "cp1251", "gb2312", "big5")
    decode_succeeded = False
    file_contents = ""
    for encoding in all_encodings:
        try:
            # print(f"Attempting file read with {encoding=} for {filename=}")
            file_contents = raw_bytes.decode(detected_encoding)
            decode_succeeded = True
            break
        except UnicodeDecodeError:
            continue

    if not decode_succeeded:
        print(f"Error: Unable to detect file encoding for: {filename=}", file=sys.stderr)
        return "", None

    return file_contents, detected_encoding


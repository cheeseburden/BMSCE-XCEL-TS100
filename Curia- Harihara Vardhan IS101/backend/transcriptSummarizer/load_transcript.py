"""
Module: load_transcript
Description: Provides a utility function to read a transcript file from disk and
return its contents as a string.
"""

import sys


def load_transcript(file_path):
    """Read the cleaned transcript file and return its contents as a stripped string.

    Args:
        file_path (str): Path to the transcript text file.

    Returns:
        str: The file contents with surrounding whitespace removed.

    Exits:
        Exits the process with code 1 if the file is not found.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)



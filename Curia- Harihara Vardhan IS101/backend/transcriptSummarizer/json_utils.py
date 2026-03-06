"""
Module: json_utils
Description: Utilities to extract and parse a JSON object from a possibly noisy
LLM output string.
"""

import json
import re


def parse_json_output(json_string):
    """Extract and parse a JSON object from a string that may contain extra text.

    Args:
        json_string (str): Raw output from the language model, possibly with
            additional text around the JSON block.

    Returns:
        dict | list | None: Parsed JSON object/array, or None on failure.
    """
    if json_string is None:
        print("Error: LLM returned no output (None).")
        return None

    match = re.search(r"\{.*\}", json_string, re.DOTALL)

    if not match:
        print("Error: No JSON object found in the LLM output.")
        return None

    json_part = match.group(0)

    try:
        return json.loads(json_part)
    except json.JSONDecodeError as error:
        print(f"Error decoding JSON from extracted part: {error}")
        print("Raw LLM output (extracted part):", json_part)
        return None



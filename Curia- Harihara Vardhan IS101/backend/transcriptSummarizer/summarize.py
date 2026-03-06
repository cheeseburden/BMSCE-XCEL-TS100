"""
summarize.py
Description: Orchestrates the transcript summarization pipeline by loading the
raw transcript, cleaning it, summarizing via LLM, and parsing the JSON output.
"""

import json

from .clean_transcript import clean_transcript
from .load_transcript import load_transcript
from .llm_summarizer import summarize_with_llama
from .json_utils import parse_json_output

def summarize_json(transcript_file):
    transcript_text = load_transcript(transcript_file)
    cleaned_text = clean_transcript(transcript_text)
    json_output_string = summarize_with_llama(cleaned_text)
    structured_data = parse_json_output(json_output_string)

    if structured_data:
        return structured_data
    else:
        return None

def main():
    summarize_json('samples/transcript0.txt')

if __name__ == "__main__":
    main()
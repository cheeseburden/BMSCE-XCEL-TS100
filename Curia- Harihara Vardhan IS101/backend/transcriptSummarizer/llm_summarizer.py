import os
import textwrap
import requests
from dotenv import load_dotenv

load_dotenv()

def summarize_with_llama(transcript):
    """Call Google Gemini to extract structured JSON from a transcript using REST API.

    Args:
        transcript (str): Cleaned transcript text.

    Returns:
        str: Raw model output (expected to contain a JSON object).
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set")
        return None

    prompt = textwrap.dedent(f"""
    You are an expert meeting assistant. Your task is to extract key decisions and action items from a meeting transcript.
    The output MUST be a valid JSON object and nothing else. Do not include markdown code fences or any other text.

    ### Instructions ###
    1. **Decisions**: Identify all key decisions made.
    2. **Action Items**: Identify all tasks that need to be completed. For each task, extract:
        - `Summary`: A concise description of the task.
        - `Assignee`: The person responsible for the task.
        - `Priority`: Assign a priority (Highest, High, Medium, Low or Lowest).
        - `Due date`: The due date for the task, if mentioned. If not, use "N/A". The duedate must be of the format "yyyy-MM-dd".

    ### Example JSON Output ###
    {{
      "decisions": [
        "Decision 1: The team will switch to a new project management tool.",
        "Decision 2: The budget for Q3 marketing campaigns will be increased by 15%."
      ],
      "action_items": [
        {{
          "Summary": "Research and evaluate new project management tools.",
          "Assignee": "Sarah",
          "Priority": "Highest",
          "Due date": "2025-09-01"
        }},
        {{
          "Summary": "Update the Q3 marketing budget proposal.",
          "Assignee": "Alex",
          "Priority": "Medium",
          "Due date": "N/A"
        }}
      ]
    }}

    ### Transcript ###
    {transcript}
    """)

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Extract text from the Gemini REST response format
        if "candidates" in data and len(data["candidates"]) > 0:
            content = data["candidates"][0].get("content", {})
            parts = content.get("parts", [])
            if parts:
                return parts[0].get("text", "").strip()
        
        print("Error: Unexpected response format from Gemini API")
        return None
        
    except requests.exceptions.HTTPError as err:
        print(f"HTTP Error calling Gemini API: {err.response.text}")
        return None
    except Exception as e:
        print(f"Error calling Gemini REST API: {e}")
        return None

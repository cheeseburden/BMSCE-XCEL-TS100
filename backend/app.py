from flask import Flask, jsonify, request
try:
    from flask_cors import CORS
except Exception:
    CORS = None
from transcriptSummarizer.summarize import summarize_json
from jira_integration import create_jira_issue
import tempfile
import os

app = Flask(__name__)
if CORS:
    CORS(app)

def create_jira_issues_from_summary(structured_data, jira_config=None):
    """
    Iterates through the action items in the structured data and
    creates a Jira issue for each one using the provided Jira config.
    """
    if not structured_data or "action_items" not in structured_data:
        print("No action items found in the provided data.")
        return structured_data

    if not jira_config:
        print("No Jira config provided — skipping ticket creation.")
        return structured_data

    action_items = structured_data["action_items"]
    jira_errors = []
    for item in action_items:
        # Normalize field names (Gemini may use different keys)
        jira_item = {
            "Summary": item.get("Summary") or item.get("item") or item.get("summary", "Action Item"),
            "Assignee": item.get("Assignee") or item.get("assigned_to", "Unassigned"),
            "Priority": item.get("Priority") or item.get("priority", "Medium"),
            "Due date": item.get("Due date") or item.get("due_by", "N/A")
        }
        result = create_jira_issue(jira_item, jira_config)
        if result:
            item["jiraIssueKey"] = result
        else:
            item["jiraError"] = "Failed to create Jira issue"
            jira_errors.append({
                "summary": jira_item["Summary"],
                "error": "Failed to create Jira issue"
            })
    if jira_errors:
        structured_data["jira_errors"] = jira_errors
    return structured_data


@app.route('/analyze-transcript', methods=['POST'])
def analyze_transcript():
    """
    API endpoint to process a meeting transcript and return
    a structured JSON summary.

    Accepts JSON body: { "transcript": "...", "jiraConfig": { ... } }
    Or plain text body for backward compatibility.
    """

    # Try JSON body first (new format from Express)
    jira_config = None
    if request.is_json:
        data = request.get_json()
        transcript_text = data.get("transcript", "")
        jira_config = data.get("jiraConfig")
    else:
        # Fallback: plain text body
        transcript_text = request.data.decode('utf-8')

    if not transcript_text:
        return jsonify({"error": "No transcript data provided."}), 400

    temp_file = None
    try:
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, encoding='utf-8') as tf:
            tf.write(transcript_text)
            tf.close()
            temp_file = tf.name

        structured_data = summarize_json(temp_file)

        if structured_data is None:
            return jsonify({
                "error": "AI summarization failed. Check GEMINI_API_KEY and model availability."
            }), 500

        # Create Jira issues using per-request config
        structured_data = create_jira_issues_from_summary(structured_data, jira_config)

        return jsonify(structured_data)

    finally:
        if temp_file and os.path.exists(temp_file):
            os.remove(temp_file)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "service": "Curia AI Summarizer"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)

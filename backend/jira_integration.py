import os
import requests
from dotenv import load_dotenv

load_dotenv()

def create_jira_issue(action_item, jira_config=None):
    """
    Creates a single Jira issue from an action item dictionary.
    Requires jira_config with: jiraUrl, jiraProjectKey, jiraEmail, jiraApiToken.
    """
    if not jira_config:
        print("No Jira config provided — skipping ticket creation.")
        return False

    jira_url = jira_config.get("jiraUrl", "").rstrip("/")
    project_key = jira_config.get("jiraProjectKey", "")
    jira_email = jira_config.get("jiraEmail", "")
    jira_token = jira_config.get("jiraApiToken", "")

    if not all([jira_url, project_key, jira_email, jira_token]):
        print("Incomplete Jira config — skipping ticket creation.")
        return False

    summary = action_item.get("Summary") or action_item.get("summary", "Action Item")
    priority = action_item.get("Priority") or action_item.get("priority", "Medium")
    deadline = action_item.get("Due date") or action_item.get("due_date")

    # Build payload dict (not string) — use json= param to avoid redirect stripping auth
    payload = {
        "fields": {
            "project": {"key": project_key},
            "summary": summary,
            "description": {
                "content": [{
                    "content": [{"text": summary, "type": "text"}],
                    "type": "paragraph"
                }],
                "type": "doc",
                "version": 1
            },
            "issuetype": {"name": "Task"},
            "priority": {"name": priority}
        }
    }

    if deadline and deadline.strip() not in ("N/A", "TBD", ""):
        payload["fields"]["duedate"] = deadline

    try:
        response = requests.post(
            f"{jira_url}/rest/api/3/issue",
            json=payload,   # Use json= not data= to avoid redirect issues
            headers={"Accept": "application/json"},
            auth=(jira_email, jira_token),
            timeout=15
        )
        response.raise_for_status()
        key = response.json().get("key")
        print(f"✅ Created Jira issue: {key}")
        return key
    except requests.exceptions.HTTPError as err:
        print(f"❌ Jira HTTP error {err.response.status_code}: {err.response.text[:300]}")
        return False
    except Exception as err:
        print(f"❌ Jira error: {err}")
        return False

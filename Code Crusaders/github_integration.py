"""
GitHub Integration module for the AI Code Review Assistant.
Fetches code files from GitHub repositories using the free public API.
No authentication required for public repos.
"""

import re
import requests
from typing import Optional
from urllib.parse import urlparse


def parse_github_url(url: str) -> Optional[dict]:
    """
    Parse a GitHub URL and extract owner, repo, branch, and file path.
    
    Supports:
    - https://github.com/owner/repo/blob/branch/path/to/file.py
    - https://raw.githubusercontent.com/owner/repo/branch/path/to/file.py
    - https://github.com/owner/repo  (repo root)
    """
    url = url.strip()
    parsed = urlparse(url)

    # Raw GitHub URL
    if "raw.githubusercontent.com" in parsed.hostname:
        parts = parsed.path.strip("/").split("/")
        if len(parts) >= 3:
            owner = parts[0]
            repo = parts[1]
            branch = parts[2]
            file_path = "/".join(parts[3:]) if len(parts) > 3 else ""
            return {
                "owner": owner,
                "repo": repo,
                "branch": branch,
                "file_path": file_path,
                "type": "raw",
            }

    # Regular GitHub URL
    if "github.com" in parsed.hostname:
        parts = parsed.path.strip("/").split("/")
        if len(parts) >= 2:
            owner = parts[0]
            repo = parts[1]

            # File URL: /owner/repo/blob/branch/path/to/file
            if len(parts) >= 4 and parts[2] == "blob":
                branch = parts[3]
                file_path = "/".join(parts[4:])
                return {
                    "owner": owner,
                    "repo": repo,
                    "branch": branch,
                    "file_path": file_path,
                    "type": "file",
                }

            # Tree URL: /owner/repo/tree/branch/path
            if len(parts) >= 4 and parts[2] == "tree":
                branch = parts[3]
                dir_path = "/".join(parts[4:]) if len(parts) > 4 else ""
                return {
                    "owner": owner,
                    "repo": repo,
                    "branch": branch,
                    "file_path": dir_path,
                    "type": "directory",
                }

            # Repo root: /owner/repo
            return {
                "owner": owner,
                "repo": repo,
                "branch": "main",
                "file_path": "",
                "type": "repo",
            }

    return None


def fetch_file_content(owner: str, repo: str, file_path: str, branch: str = "main") -> dict:
    """
    Fetch a single file's content from GitHub API.
    Returns dict with 'content', 'name', 'size', 'url', 'language'.
    """
    api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}?ref={branch}"
    
    headers = {
        "Accept": "application/vnd.github.v3.raw",
        "User-Agent": "AI-Code-Review-Assistant",
    }
    
    try:
        response = requests.get(api_url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            content = response.text
            filename = file_path.split("/")[-1] if file_path else ""
            return {
                "success": True,
                "content": content,
                "filename": filename,
                "file_path": file_path,
                "size": len(content),
                "url": f"https://github.com/{owner}/{repo}/blob/{branch}/{file_path}",
            }
        elif response.status_code == 404:
            # Try with 'master' branch if 'main' failed
            if branch == "main":
                return fetch_file_content(owner, repo, file_path, "master")
            return {"success": False, "error": f"File not found: {file_path}"}
        elif response.status_code == 403:
            return {"success": False, "error": "GitHub API rate limit exceeded. Try again in a minute."}
        else:
            return {"success": False, "error": f"GitHub API error: {response.status_code}"}
            
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Request timed out. Check your internet connection."}
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"Network error: {str(e)}"}


def list_repo_files(owner: str, repo: str, path: str = "", branch: str = "main") -> dict:
    """
    List files in a GitHub repository directory.
    Returns dict with 'files' list containing name, path, type, size.
    """
    api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={branch}"
    
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "AI-Code-Review-Assistant",
    }
    
    try:
        response = requests.get(api_url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            items = response.json()
            if not isinstance(items, list):
                return {"success": False, "error": "Path is a file, not a directory."}
            
            # Filter to code files only
            CODE_EXTENSIONS = {
                ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".cpp", ".c", ".cs",
                ".go", ".rs", ".rb", ".php", ".swift", ".kt", ".scala", ".r",
                ".sql", ".html", ".css", ".sh", ".yml", ".yaml", ".json", ".xml",
                ".dart", ".lua", ".pl", ".h", ".hpp", ".m", ".vue", ".svelte",
            }
            
            files = []
            dirs = []
            for item in items:
                if item["type"] == "dir":
                    dirs.append({
                        "name": item["name"],
                        "path": item["path"],
                        "type": "dir",
                    })
                elif item["type"] == "file":
                    ext = "." + item["name"].rsplit(".", 1)[-1].lower() if "." in item["name"] else ""
                    if ext in CODE_EXTENSIONS:
                        files.append({
                            "name": item["name"],
                            "path": item["path"],
                            "type": "file",
                            "size": item.get("size", 0),
                        })
            
            return {
                "success": True,
                "files": files,
                "dirs": dirs,
                "repo": f"{owner}/{repo}",
                "branch": branch,
                "current_path": path,
            }
        elif response.status_code == 404:
            if branch == "main":
                return list_repo_files(owner, repo, path, "master")
            return {"success": False, "error": f"Repository or path not found."}
        elif response.status_code == 403:
            return {"success": False, "error": "GitHub API rate limit exceeded. Try again in a minute."}
        else:
            return {"success": False, "error": f"GitHub API error: {response.status_code}"}
            
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Request timed out."}
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"Network error: {str(e)}"}


def fetch_from_url(url: str) -> dict:
    """
    High-level function: takes any GitHub URL and returns the file content.
    Handles parsing, validation, and fetching in one call.
    """
    parsed = parse_github_url(url)
    if not parsed:
        return {"success": False, "error": "Invalid GitHub URL. Please paste a valid GitHub file URL."}
    
    if parsed["type"] == "raw":
        # Fetch directly from raw URL
        try:
            response = requests.get(url.strip(), timeout=15, headers={"User-Agent": "AI-Code-Review-Assistant"})
            if response.status_code == 200:
                filename = parsed["file_path"].split("/")[-1] if parsed["file_path"] else "unknown"
                return {
                    "success": True,
                    "content": response.text,
                    "filename": filename,
                    "file_path": parsed["file_path"],
                    "size": len(response.text),
                    "url": url,
                    "repo": f"{parsed['owner']}/{parsed['repo']}",
                }
            return {"success": False, "error": f"Failed to fetch raw file: {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    if parsed["type"] == "file":
        result = fetch_file_content(parsed["owner"], parsed["repo"], parsed["file_path"], parsed["branch"])
        if result["success"]:
            result["repo"] = f"{parsed['owner']}/{parsed['repo']}"
        return result
    
    if parsed["type"] in ("repo", "directory"):
        result = list_repo_files(parsed["owner"], parsed["repo"], parsed["file_path"], parsed["branch"])
        if result["success"]:
            result["type"] = "directory"
        return result
    
    return {"success": False, "error": "Unsupported GitHub URL format."}

"""
Database module for the AI Code Review Assistant.
Uses SQLite for persistent storage of review history.
Lightweight, zero-config, and built into Python.
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Optional


# Use environment variable for DB path if set (e.g., in Docker), otherwise default to local dir
DB_PATH = os.environ.get("CRUSADER_DB_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "review_history.db"))


def _get_connection() -> sqlite3.Connection:
    """Get a SQLite connection with row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database schema. Safe to call multiple times."""
    conn = _get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            date TEXT NOT NULL,
            score INTEGER DEFAULT 0,
            language TEXT DEFAULT '',
            model TEXT DEFAULT '',
            mode TEXT DEFAULT '',
            issues_count INTEGER DEFAULT 0,
            summary TEXT DEFAULT '',
            code_snippet TEXT DEFAULT '',
            elapsed REAL DEFAULT 0,
            review_json TEXT DEFAULT '{}',
            metrics_json TEXT DEFAULT '{}',
            optimized_code TEXT DEFAULT ''
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT DEFAULT ''
        )
    """)
    conn.commit()
    conn.close()


def save_setting(key: str, value: str):
    """Save or update a setting."""
    conn = _get_connection()
    conn.execute(
        "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
        (key, value),
    )
    conn.commit()
    conn.close()


def get_setting(key: str, default: str = "") -> str:
    """Get a setting value by key."""
    conn = _get_connection()
    row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    conn.close()
    return row["value"] if row else default


def get_all_settings() -> dict:
    """Get all settings as a dictionary."""
    conn = _get_connection()
    rows = conn.execute("SELECT key, value FROM settings").fetchall()
    conn.close()
    return {row["key"]: row["value"] for row in rows}


# --- Review functions below (unchanged) ---


def save_review(entry: dict):
    """Save a review entry to the database."""
    conn = _get_connection()
    conn.execute("""
        INSERT INTO reviews (timestamp, date, score, language, model, mode,
                             issues_count, summary, code_snippet, elapsed,
                             review_json, metrics_json, optimized_code)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        entry.get("timestamp", datetime.now().strftime("%I:%M %p")),
        entry.get("date", datetime.now().strftime("%Y-%m-%d")),
        entry.get("score", 0),
        entry.get("language", ""),
        entry.get("model", ""),
        entry.get("mode", ""),
        entry.get("issues_count", 0),
        entry.get("summary", ""),
        entry.get("code_snippet", ""),
        entry.get("elapsed", 0),
        json.dumps(entry.get("review", {})),
        json.dumps(entry.get("metrics", {})),
        entry.get("optimized_code", ""),
    ))
    conn.commit()
    conn.close()


def get_all_reviews() -> list:
    """Retrieve all reviews, ordered by newest first."""
    conn = _get_connection()
    rows = conn.execute("SELECT * FROM reviews ORDER BY id DESC").fetchall()
    conn.close()

    results = []
    for row in rows:
        results.append({
            "id": row["id"],
            "timestamp": row["timestamp"],
            "date": row["date"],
            "score": row["score"],
            "language": row["language"],
            "model": row["model"],
            "mode": row["mode"],
            "issues_count": row["issues_count"],
            "summary": row["summary"],
            "code_snippet": row["code_snippet"],
            "elapsed": row["elapsed"],
            "review": json.loads(row["review_json"]) if row["review_json"] else {},
            "metrics": json.loads(row["metrics_json"]) if row["metrics_json"] else {},
            "optimized_code": row["optimized_code"],
        })
    return results


def get_review_count() -> int:
    """Get total number of reviews."""
    conn = _get_connection()
    count = conn.execute("SELECT COUNT(*) FROM reviews").fetchone()[0]
    conn.close()
    return count


def get_review_by_id(review_id: int) -> Optional[dict]:
    """Get a specific review by ID."""
    conn = _get_connection()
    row = conn.execute("SELECT * FROM reviews WHERE id = ?", (review_id,)).fetchone()
    conn.close()

    if row is None:
        return None

    return {
        "id": row["id"],
        "timestamp": row["timestamp"],
        "date": row["date"],
        "score": row["score"],
        "language": row["language"],
        "model": row["model"],
        "mode": row["mode"],
        "issues_count": row["issues_count"],
        "summary": row["summary"],
        "code_snippet": row["code_snippet"],
        "elapsed": row["elapsed"],
        "review": json.loads(row["review_json"]) if row["review_json"] else {},
        "metrics": json.loads(row["metrics_json"]) if row["metrics_json"] else {},
        "optimized_code": row["optimized_code"],
    }


def clear_history():
    """Delete all review history."""
    conn = _get_connection()
    conn.execute("DELETE FROM reviews")
    conn.commit()
    conn.close()


def get_stats() -> dict:
    """Get aggregate statistics for the dashboard."""
    conn = _get_connection()
    row = conn.execute("""
        SELECT
            COUNT(*) as total,
            COALESCE(AVG(score), 0) as avg_score,
            COALESCE(MAX(score), 0) as best_score,
            COALESCE(SUM(issues_count), 0) as total_issues
        FROM reviews
    """).fetchone()
    conn.close()

    return {
        "total": row["total"],
        "avg_score": round(row["avg_score"], 1),
        "best_score": row["best_score"],
        "total_issues": row["total_issues"],
    }


# Initialize database on module import
init_db()


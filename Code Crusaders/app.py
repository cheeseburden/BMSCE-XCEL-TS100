"""
🔍 AI Code Review Assistant
A premium, AI-powered code review tool built with Streamlit, LangChain, and Groq.
Analyzes code for bugs, security vulnerabilities, performance issues, and teaches best practices.
"""

import sys
import os
import time
from datetime import datetime
import streamlit as st

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from code_analyzer import CodeAnalyzer
from review_engine import CodeReviewEngine
from github_integration import fetch_from_url, fetch_file_content, parse_github_url
from db import save_review, get_all_reviews, clear_history, get_stats, save_setting, get_setting
from utils import (
    SUPPORTED_LANGUAGES,
    SEVERITY_EMOJI,
    SEVERITY_COLOR,
    CATEGORY_EMOJI,
    detect_language,
    sort_issues_by_severity,
    count_by_severity,
    count_by_category,
    generate_markdown_report,
    generate_diff_html,
    generate_split_diff_html,
)

# ─── Page Configuration ─────────────────────────────────────────────────────

st.set_page_config(
    page_title="AI Code Review Assistant",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Session State Init ─────────────────────────────────────────────────────
# Review history is now stored in SQLite (db.py) — persists across restarts

# ─── Custom CSS ──────────────────────────────────────────────────────────────

st.markdown("""
<style>
    /* ── Import Google Font ───────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* ── Global Theme ─────────────────────────────────────────── */
    :root {
        --bg-primary: #0a0e1a;
        --bg-secondary: #111827;
        --bg-card: #1a1f35;
        --bg-card-hover: #1f2640;
        --accent-primary: #6366f1;
        --accent-secondary: #818cf8;
        --accent-glow: rgba(99, 102, 241, 0.3);
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
        --text-muted: #64748b;
        --border-color: #2a2f45;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
        --danger-glow: rgba(239, 68, 68, 0.2);
        --info: #3b82f6;
    }

    .stApp {
        font-family: 'Inter', sans-serif;
    }

    /* ── Header ───────────────────────────────────────────────── */
    .main-header {
        text-align: center;
        padding: 2rem 0 1rem 0;
    }

    .main-header h1 {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.3rem;
        letter-spacing: -0.02em;
    }

    .main-header p {
        color: var(--text-secondary);
        font-size: 1.1rem;
        font-weight: 400;
    }

    /* ── Metric Cards ─────────────────────────────────────────── */
    .metric-card {
        background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-card-hover) 100%);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 4px 24px rgba(0,0,0,0.2);
    }

    .metric-card:hover {
        border-color: var(--accent-primary);
        box-shadow: 0 4px 24px var(--accent-glow);
        transform: translateY(-2px);
    }

    .metric-value {
        font-size: 2.4rem;
        font-weight: 800;
        font-family: 'JetBrains Mono', monospace;
        margin: 0;
    }

    .metric-label {
        color: var(--text-secondary);
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 600;
        margin-top: 0.3rem;
    }

    /* ── Score Circle ─────────────────────────────────────────── */
    .score-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 1.5rem 0;
    }

    .score-circle {
        width: 160px;
        height: 160px;
        border-radius: 50%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        position: relative;
        box-shadow: 0 0 40px var(--accent-glow);
    }

    .score-number {
        font-size: 3.2rem;
        font-weight: 900;
        font-family: 'JetBrains Mono', monospace;
        line-height: 1;
    }

    .score-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-weight: 600;
        color: var(--text-secondary);
        margin-top: 0.3rem;
    }

    /* ── Issue Cards ──────────────────────────────────────────── */
    .issue-card {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }

    .issue-card:hover {
        border-color: var(--accent-secondary);
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }

    .issue-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1rem;
    }

    .severity-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .severity-critical { background: rgba(239,68,68,0.15); color: #ff6b6b; border: 1px solid rgba(239,68,68,0.3); }
    .severity-high { background: rgba(255,140,0,0.15); color: #ff8c00; border: 1px solid rgba(255,140,0,0.3); }
    .severity-medium { background: rgba(255,215,0,0.15); color: #ffd700; border: 1px solid rgba(255,215,0,0.3); }
    .severity-low { background: rgba(68,187,68,0.15); color: #44bb44; border: 1px solid rgba(68,187,68,0.3); }

    .category-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        background: rgba(99,102,241,0.12);
        color: var(--accent-secondary);
        border: 1px solid rgba(99,102,241,0.25);
    }

    .line-ref {
        color: var(--text-muted);
        font-size: 0.8rem;
        font-family: 'JetBrains Mono', monospace;
        margin-left: auto;
    }

    /* ── Learn & Fix Panel ────────────────────────────────────── */
    .learn-fix-panel {
        background: linear-gradient(135deg, rgba(16,185,129,0.08) 0%, rgba(99,102,241,0.08) 100%);
        border: 1px solid rgba(16,185,129,0.2);
        border-radius: 10px;
        padding: 1.2rem;
        margin-top: 1rem;
    }

    .learn-fix-title {
        color: var(--success);
        font-size: 0.9rem;
        font-weight: 700;
        margin-bottom: 0.8rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* ── Strength Card ────────────────────────────────────────── */
    .strength-item {
        background: rgba(16,185,129,0.08);
        border: 1px solid rgba(16,185,129,0.15);
        border-radius: 10px;
        padding: 0.8rem 1.2rem;
        margin-bottom: 0.5rem;
        color: var(--text-primary);
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* ── Sidebar Styling ──────────────────────────────────────── */
    section[data-testid="stSidebar"] {
        background: var(--bg-secondary) !important;
        border-right: 1px solid var(--border-color);
    }

    .sidebar-header {
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 1rem;
    }

    .sidebar-header h2 {
        font-size: 1.4rem;
        font-weight: 700;
        background: linear-gradient(135deg, #6366f1, #a855f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    /* ── Progress Bar ─────────────────────────────────────────── */
    .quality-bar {
        background: var(--bg-secondary);
        border-radius: 8px;
        height: 10px;
        overflow: hidden;
        margin-top: 0.3rem;
    }

    .quality-fill {
        height: 100%;
        border-radius: 8px;
        transition: width 1s ease;
    }

    /* ── Footer ───────────────────────────────────────────────── */
    .footer {
        text-align: center;
        padding: 2rem 0 1rem 0;
        color: var(--text-muted);
        font-size: 0.85rem;
        border-top: 1px solid var(--border-color);
        margin-top: 3rem;
    }

    /* ── Tabs ─────────────────────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 0.5rem 1.2rem;
        font-weight: 600;
    }

    /* ── Hide Streamlit Defaults ──────────────────────────────── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ─── Sidebar ─────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div class="sidebar-header">
        <h2>⚙️ Configuration</h2>
    </div>
    """, unsafe_allow_html=True)

    # API Key input
    st.markdown("### 🔑 API Key")
    saved_api_key = get_setting("api_key", "")
    api_key = st.text_input(
        "Groq API Key",
        value=saved_api_key,
        type="password",
        placeholder="gsk_...",
        help="Get your FREE API key at https://console.groq.com/keys",
    )
    # Auto-save API key when changed
    if api_key != saved_api_key:
        save_setting("api_key", api_key)

    if not api_key:
        st.info("💡 Get a **free** Groq API key at [console.groq.com](https://console.groq.com/keys)")

    st.markdown("---")

    # Model selection
    st.markdown("### 🤖 Model")
    model_options = CodeReviewEngine.get_available_models()
    saved_model = get_setting("model", model_options[0])
    saved_model_idx = model_options.index(saved_model) if saved_model in model_options else 0
    selected_model = st.selectbox(
        "Select Model",
        model_options,
        index=saved_model_idx,
        help="Llama 3.3 70B gives the best reviews. Use 8B for faster results.",
    )
    if selected_model != saved_model:
        save_setting("model", selected_model)

    st.markdown("---")

    # Language selection
    st.markdown("### 💻 Language")
    saved_lang = get_setting("language", SUPPORTED_LANGUAGES[0])
    saved_lang_idx = SUPPORTED_LANGUAGES.index(saved_lang) if saved_lang in SUPPORTED_LANGUAGES else 0
    language = st.selectbox(
        "Programming Language",
        SUPPORTED_LANGUAGES,
        index=saved_lang_idx,
    )
    if language != saved_lang:
        save_setting("language", language)

    # Review mode is always Comprehensive
    review_mode = "🔍 Comprehensive"

    st.markdown("---")

    # Review History in Sidebar (from SQLite DB)
    st.markdown("### 📜 Review History")
    sidebar_history = get_all_reviews()
    if sidebar_history:
        # Show last 10 reviews in sidebar
        for entry in sidebar_history[:10]:
            score = entry.get("score", 0)
            lang = entry.get("language", "?")
            ts = entry.get("timestamp", "")
            date = entry.get("date", "")
            snippet = entry.get("code_snippet", "code")[:30].replace("\n", " ")
            if score >= 80:
                color = "#10b981"
            elif score >= 60:
                color = "#3b82f6"
            elif score >= 40:
                color = "#f59e0b"
            else:
                color = "#ef4444"
            st.markdown(f"""
            <div style="background: var(--bg-card, #1a1f35); border: 1px solid var(--border-color, #2a2f45);
                border-radius: 10px; padding: 0.6rem 0.8rem; margin-bottom: 0.4rem; font-size: 0.82rem;">
                <span style="color: {color}; font-weight: 800; font-family: 'JetBrains Mono', monospace;">{score}</span>
                <span style="color: var(--text-secondary, #94a3b8);"> · {lang} · {date} {ts}</span><br/>
                <span style="color: var(--text-muted, #64748b); font-size: 0.75rem;">{snippet}…</span>
            </div>
            """, unsafe_allow_html=True)
        if len(sidebar_history) > 10:
            st.caption(f"+ {len(sidebar_history) - 10} more reviews…")
        if st.button("🗑️ Clear All History", use_container_width=True):
            clear_history()
            st.rerun()
    else:
        st.caption("No reviews yet. Run your first review!")

    st.markdown("---")

    # About section
    with st.expander("ℹ️ About"):
        st.markdown("""
        **AI Code Review Assistant** v2.0

        Built with:
        - 🐍 Python
        - 🦜 LangChain
        - ⚡ Groq (Free Tier)
        - 🎨 Streamlit

        **Models:** Llama 3.3, Mixtral, Gemma 2
        **Cost:** 100% Free

        *BMSCE XCEL Hackathon — Code Crusaders*
        """)


# ─── Main Header ─────────────────────────────────────────────────────────────

st.markdown("""
<div class="main-header">
    <h1>🔍 AI Code Review Assistant</h1>
    <p>Intelligent code analysis powered by AI — Find bugs, vulnerabilities & learn best practices</p>
</div>
""", unsafe_allow_html=True)


# ─── Sample Loading Callbacks ────────────────────────────────────────────────
# These must run BEFORE the text_area widget is instantiated

def _load_sample(filename: str):
    """Callback to load sample code into session state before widget renders."""
    samples_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "samples")
    sample_path = os.path.join(samples_dir, filename)
    if os.path.exists(sample_path):
        with open(sample_path, "r", encoding="utf-8") as f:
            st.session_state["code_paste"] = f.read()


# Pre-render: if GitHub code was fetched on a previous run, load it into the widget
if st.session_state.get("_github_code"):
    st.session_state["code_paste"] = st.session_state.pop("_github_code")


# ─── Code Input ──────────────────────────────────────────────────────────────

input_tab, upload_tab, github_tab, sample_tab = st.tabs(["📝 Paste Code", "📁 Upload File", "🐙 GitHub Import", "📦 Sample Code"])

code_input = ""

with input_tab:
    code_input = st.text_area(
        "Paste your code here",
        height=350,
        placeholder="# Paste your code here...\n\ndef example():\n    pass",
        key="code_paste",
    )

with upload_tab:
    uploaded_file = st.file_uploader(
        "Upload a source code file",
        type=["py", "js", "ts", "java", "cpp", "c", "cs", "go", "rs", "rb", "php", "swift", "kt", "sql", "html", "css", "sh"],
        help="Supports 15+ programming languages",
    )
    if uploaded_file:
        code_input = uploaded_file.read().decode("utf-8", errors="replace")
        detected_lang = detect_language(uploaded_file.name)
        if detected_lang != "Unknown":
            language = detected_lang
        st.code(code_input, language=language.lower().split()[0])

with github_tab:
    st.markdown("**Import code directly from any public GitHub repository**")
    github_url = st.text_input(
        "GitHub URL",
        placeholder="https://github.com/owner/repo/blob/main/path/to/file.py",
        help="Paste a GitHub file URL, raw URL, or repo URL to browse files",
    )

    if github_url:
        # Only fetch if URL changed since last fetch
        cached_url = st.session_state.get("_github_cached_url", "")
        cached_result = st.session_state.get("_github_cached_result", None)

        if github_url != cached_url or cached_result is None:
            with st.spinner("🔄 Fetching from GitHub..."):
                result = fetch_from_url(github_url)
            st.session_state["_github_cached_url"] = github_url
            st.session_state["_github_cached_result"] = result
        else:
            result = cached_result

        if result.get("success"):
            # It's a directory listing — let user pick a file
            if result.get("type") == "directory":
                st.markdown(f"**📂 Repository:** `{result.get('repo', '')}` — Branch: `{result.get('branch', 'main')}`")
                current_path = result.get("current_path", "")
                if current_path:
                    st.markdown(f"**📁 Path:** `{current_path}`")

                dirs = result.get("dirs", [])
                files = result.get("files", [])

                if dirs:
                    st.markdown("##### 📁 Folders")
                    dir_cols = st.columns(min(len(dirs), 4))
                    for i, d in enumerate(dirs[:12]):
                        with dir_cols[i % min(len(dirs), 4)]:
                            st.markdown(f"📂 `{d['name']}/`")

                if files:
                    st.markdown("##### 📄 Code Files")
                    selected_file = st.selectbox(
                        "Select a file to review",
                        options=[f["path"] for f in files],
                        format_func=lambda x: f"📄 {x.split('/')[-1]}  ({x})",
                    )
                    if selected_file and st.button("📥 Load Selected File", use_container_width=True):
                        parsed = parse_github_url(github_url)
                        if parsed:
                            file_result = fetch_file_content(
                                parsed["owner"], parsed["repo"],
                                selected_file, parsed.get("branch", "main"),
                            )
                            if file_result.get("success"):
                                code_input = file_result["content"]
                                st.session_state["_github_code"] = code_input
                                detected_lang = detect_language(file_result.get("filename", ""))
                                if detected_lang != "Unknown":
                                    language = detected_lang
                                st.success(f"✅ Loaded `{file_result.get('filename', '')}` ({len(code_input)} chars) — switch to **Paste Code** tab to review!")
                                st.rerun()
                            else:
                                st.error(file_result.get("error", "Failed to load file."))
                else:
                    st.info("No supported code files found in this directory.")

            # It's a single file — load directly (no rerun loop since we cache)
            else:
                # Only auto-load once per URL
                loaded_url = st.session_state.get("_github_loaded_url", "")
                if github_url != loaded_url:
                    code_input = result["content"]
                    st.session_state["_github_code"] = code_input
                    st.session_state["_github_loaded_url"] = github_url
                    st.rerun()
                else:
                    code_input = result["content"]
                    filename = result.get("filename", "")
                    repo_name = result.get("repo", "")
                    st.success(f"✅ Loaded `{filename}` from `{repo_name}` ({result.get('size', 0)} chars) — code is in the **Paste Code** tab!")
                    st.code(code_input[:3000] + ("\n..." if len(code_input) > 3000 else ""), language=language.lower().split()[0])
        else:
            st.error(f"❌ {result.get('error', 'Failed to fetch from GitHub.')}")
    else:
        # Clear cache when URL is removed
        st.session_state.pop("_github_cached_url", None)
        st.session_state.pop("_github_cached_result", None)
        st.session_state.pop("_github_loaded_url", None)
        st.markdown("""
        **Supported URL formats:**
        - `https://github.com/owner/repo/blob/main/file.py` — Direct file
        - `https://raw.githubusercontent.com/owner/repo/main/file.py` — Raw file
        - `https://github.com/owner/repo` — Browse repository files
        """)

with sample_tab:
    sample_col1, sample_col2 = st.columns(2)
    with sample_col1:
        st.button(
            "🐛 Load Bad Code Sample",
            use_container_width=True,
            on_click=_load_sample,
            args=("sample_bad.py",),
        )

    with sample_col2:
        st.button(
            "✅ Load Good Code Sample",
            use_container_width=True,
            on_click=_load_sample,
            args=("sample_good.py",),
        )


# ─── Review Button ───────────────────────────────────────────────────────────

st.markdown("")
col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    review_clicked = st.button(
        "🚀 Run AI Code Review",
        use_container_width=True,
        type="primary",
        disabled=not code_input or not api_key,
    )

if not api_key and code_input:
    st.warning("⚠️ Please enter your **Groq API key** in the sidebar to run reviews. It's FREE!")

if not code_input and api_key:
    st.info("📝 Paste code, upload a file, or load a sample to get started.")


# ─── Run Review ──────────────────────────────────────────────────────────────

if review_clicked and code_input and api_key:

    # Clear previous results
    st.session_state["last_review"] = None

    # Progress indicators
    progress_bar = st.progress(0, text="🔄 Initializing AI engine...")
    start_time = time.time()

    try:
        # Step 1: Static Analysis
        progress_bar.progress(15, text="📊 Running static analysis...")
        analyzer = CodeAnalyzer(code_input, language)
        metrics = analyzer.get_metrics()
        static_issues = analyzer.get_static_issues()
        functions_summary = analyzer.get_functions_summary()

        # Step 2: LLM Review
        progress_bar.progress(25, text=f"🤖 Analyzing with {selected_model}...")
        engine = CodeReviewEngine(api_key=api_key, model_name=selected_model)

        review = engine.review_code(code_input, language)

        # Step 3: Generate Optimized Code
        progress_bar.progress(65, text="✨ Generating optimized code...")
        optimized_code = engine.optimize_code(code_input, language)

        progress_bar.progress(95, text="📄 Finalizing report...")
        elapsed = round(time.time() - start_time, 2)
        progress_bar.progress(100, text=f"✅ Review complete in {elapsed}s")
        time.sleep(0.5)
        progress_bar.empty()

        # ─── Save to Review History (SQLite) ────────────────────────
        history_entry = {
            "timestamp": datetime.now().strftime("%I:%M %p"),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "score": review.get("overall_score", review.get("security_score", 0) * 10 if "Security" in review_mode else 0),
            "language": language,
            "model": selected_model,
            "mode": review_mode,
            "issues_count": len(review.get("issues", review.get("vulnerabilities", []))),
            "summary": review.get("summary", ""),
            "code_snippet": code_input,
            "elapsed": elapsed,
            "review": review,
            "metrics": metrics,
            "optimized_code": optimized_code,
        }
        save_review(history_entry)

        # Store in session_state so results persist across reruns (e.g. radio clicks)
        st.session_state["last_review"] = {
            "review": review,
            "metrics": metrics,
            "static_issues": static_issues,
            "functions_summary": functions_summary,
            "optimized_code": optimized_code,
            "code_input": code_input,
            "language": language,
            "review_mode": review_mode,
            "selected_model": selected_model,
            "elapsed": elapsed,
        }

        # Check for parse errors
        if review.get("parse_error"):
            st.error("⚠️ Failed to parse AI response. Please try again.")
            with st.expander("Raw Response"):
                st.code(review.get("raw_response", ""))
            st.stop()

        # ─── Results Display ───────────────────────────────────
        # Results are stored in session_state and displayed below
        pass

    except Exception as e:
        progress_bar.empty()
        st.error(f"❌ An error occurred: {str(e)}")
        with st.expander("Error Details"):
            st.code(str(e))


# ─── Display Results (from session_state) ───────────────────────────────

if st.session_state.get("last_review"):
    lr = st.session_state["last_review"]
    review = lr["review"]
    metrics = lr["metrics"]
    static_issues = lr["static_issues"]
    functions_summary = lr["functions_summary"]
    optimized_code = lr["optimized_code"]
    code_input_display = lr["code_input"]
    language_display = lr["language"]
    review_mode_display = lr["review_mode"]
    selected_model_display = lr["selected_model"]
    elapsed = lr["elapsed"]

    st.markdown("---")
    
    # Toggle for chat
    header_col, toggle_col = st.columns([3, 1])
    with header_col:
        st.markdown("## 📊 Review Results")
    with toggle_col:
        st.markdown("<br>", unsafe_allow_html=True)
        show_chat = st.toggle("💬 Open AI Chat", value=st.session_state.get("show_chat", False), key="show_chat")
        
    if show_chat:
        main_col, chat_col = st.columns([7, 3], gap="large")
    else:
        main_col = st.container()
        chat_col = None

    with main_col:
        
        # Top-level metrics row
        overall_score = review.get("overall_score", 0)
        issues = review.get("issues", [])
        
        severity_counts = count_by_severity(issues) if issues else {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
        
        # Score gradient
        if overall_score >= 80:
            score_color = "#10b981"
            score_bg = "rgba(16,185,129,0.08)"
            score_border = "rgba(16,185,129,0.3)"
            grade = "A"
        elif overall_score >= 60:
            score_color = "#3b82f6"
            score_bg = "rgba(59,130,246,0.08)"
            score_border = "rgba(59,130,246,0.3)"
            grade = "B"
        elif overall_score >= 40:
            score_color = "#f59e0b"
            score_bg = "rgba(245,158,11,0.08)"
            score_border = "rgba(245,158,11,0.3)"
            grade = "C"
        else:
            score_color = "#ef4444"
            score_bg = "rgba(239,68,68,0.08)"
            score_border = "rgba(239,68,68,0.3)"
            grade = "D"
        
        # --- Score + Summary Row ---
        score_col, summary_col = st.columns([1, 2])
        
        with score_col:
            display_score = overall_score
        
            st.markdown(f"""
            <div class="score-container">
                <div class="score-circle" style="
                    background: {score_bg};
                    border: 3px solid {score_border};
                ">
                    <div class="score-number" style="color: {score_color};">{display_score}</div>
                    <div class="score-label">out of 100</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with summary_col:
            st.markdown(f"### 📝 Summary")
            st.markdown(review.get("summary", "No summary available."))
            st.markdown(f"**⏱️ Analysis Time:** {elapsed}s &nbsp; | &nbsp; **🤖 Model:** {selected_model_display} &nbsp; | &nbsp; **📋 Grade:** {grade}")
        
        # --- Severity Count Metrics ---
        st.markdown("")
        c1, c2, c3, c4, c5 = st.columns(5)
        
        with c1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: {score_color};">{display_score}</div>
                <div class="metric-label">Quality Score</div>
            </div>
            """, unsafe_allow_html=True)
        
        with c2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: #ff4444;">{severity_counts.get("Critical", 0)}</div>
                <div class="metric-label">🔴 Critical</div>
            </div>
            """, unsafe_allow_html=True)
        
        with c3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: #ff8c00;">{severity_counts.get("High", 0)}</div>
                <div class="metric-label">🟠 High</div>
            </div>
            """, unsafe_allow_html=True)
        
        with c4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: #ffd700;">{severity_counts.get("Medium", 0)}</div>
                <div class="metric-label">🟡 Medium</div>
            </div>
            """, unsafe_allow_html=True)
        
        with c5:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: #44bb44;">{severity_counts.get("Low", 0)}</div>
                <div class="metric-label">🟢 Low</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("")
        
        # --- Quality Metrics Bars ---
        ai_metrics = review.get("metrics", {})
        if ai_metrics:
            st.markdown("### 📈 Quality Metrics")
            metric_cols = st.columns(5)
            metric_items = [
                ("Readability", "readability", "#6366f1"),
                ("Maintainability", "maintainability", "#a855f7"),
                ("Security", "security", "#ef4444"),
                ("Performance", "performance", "#f59e0b"),
                ("Best Practices", "best_practices", "#10b981"),
            ]
            for col, (label, key, color) in zip(metric_cols, metric_items):
                val = ai_metrics.get(key, 0)
                pct = val * 10
                with col:
                    st.markdown(f"""
                    <div class="metric-card" style="padding: 1rem;">
                        <div class="metric-value" style="color: {color}; font-size: 1.8rem;">{val}/10</div>
                        <div class="metric-label">{label}</div>
                        <div class="quality-bar">
                            <div class="quality-fill" style="width: {pct}%; background: {color};"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
            st.markdown("")
        
        # --- Tabs ---
        lang_lower = language_display.lower().split()[0]
        issues_tab, optimized_tab, static_tab, strengths_tab, report_tab = st.tabs([
            f"🐛 Issues ({len(issues)})",
            "✅ Optimized Code",
            f"📊 Static Analysis ({metrics.get('static_issues', 0)})",
            f"✨ Strengths",
            "📄 Download Report",
        ])
        
        with issues_tab:
            if not issues:
                st.success("🎉 No issues found! Your code looks great.")
            else:
                sorted_issues = sort_issues_by_severity(issues)
        
                # Filter controls
                filter_col1, filter_col2 = st.columns(2)
                with filter_col1:
                    sev_filter = st.multiselect(
                        "Filter by Severity",
                        ["Critical", "High", "Medium", "Low"],
                        default=["Critical", "High", "Medium", "Low"],
                    )
                with filter_col2:
                    cats = list(set(i.get("category", "Other") for i in issues))
                    cat_filter = st.multiselect(
                        "Filter by Category",
                        cats,
                        default=cats,
                    )
        
                filtered = [
                    i for i in sorted_issues
                    if i.get("severity", "Low") in sev_filter
                    and i.get("category", "Other") in cat_filter
                ]
        
                for idx, issue in enumerate(filtered):
                    sev = issue.get("severity", "Low")
                    cat = issue.get("category", "Other")
                    title = issue.get("title", "Issue")
                    cat_emoji = CATEGORY_EMOJI.get(cat, "📋")
        
                    with st.expander(
                        f"{SEVERITY_EMOJI.get(sev, '⚪')} [{sev}] {cat_emoji} {title}  —  {issue.get('line_reference', '')}",
                        expanded=(sev in ("Critical", "High")),
                    ):
                        st.markdown(f"**📝 Description:** {issue.get('description', 'N/A')}")
                        st.markdown("")
        
                        prob_code = issue.get("problematic_code")
                        if prob_code:
                            st.markdown("**❌ Problematic Code:**")
                            st.code(prob_code, language=lang_lower)
        
                        fix_code = issue.get("suggested_fix", "")
                        explanation = issue.get("explanation", "")
                        reference = issue.get("learning_reference", "")
        
                        if fix_code or explanation:
                            st.markdown("""
                            <div class="learn-fix-panel">
                                <div class="learn-fix-title">✅ Learn & Fix — Best Practice Solution</div>
                            </div>
                            """, unsafe_allow_html=True)
        
                            if fix_code:
                                st.markdown("**✅ Best Practice Code:**")
                                st.code(fix_code, language=lang_lower)
        
                            if explanation:
                                st.markdown(f"**📖 Why This Is Better:** {explanation}")
        
                            if reference:
                                st.markdown(f"**🔗 Learn More:** {reference}")
        
        with static_tab:
            st.markdown("### 📊 Code Metrics (Static Analysis)")
            st.markdown("*These metrics are computed locally without AI — instant results.*")
        
            sm1, sm2, sm3, sm4 = st.columns(4)
            with sm1:
                st.metric("Total Lines", metrics["total_lines"])
            with sm2:
                st.metric("Functions", metrics["function_count"])
            with sm3:
                st.metric("Classes", metrics["class_count"])
            with sm4:
                st.metric("Complexity", metrics["cyclomatic_complexity"])
        
            sm5, sm6, sm7, sm8 = st.columns(4)
            with sm5:
                st.metric("Non-Empty Lines", metrics["non_empty_lines"])
            with sm6:
                st.metric("Comment Lines", metrics["comment_lines"])
            with sm7:
                st.metric("Comment Ratio", f"{metrics['comment_ratio']}%")
            with sm8:
                st.metric("Imports", metrics["import_count"])
        
            if static_issues:
                st.markdown("### ⚠️ Static Analysis Issues")
                for si in static_issues:
                    severity = si.get("severity", "Low")
                    emoji = SEVERITY_EMOJI.get(severity, "⚪")
                    st.markdown(
                        f"- {emoji} **[{severity}]** Line {si.get('line', '?')}: "
                        f"{si.get('message', 'N/A')} ({si.get('type', '')})"
                    )
        
            if functions_summary:
                st.markdown("### 📦 Functions Detected")
                for fn in functions_summary:
                    body_lines = fn.get("body_lines", 0)
                    warn = " ⚠️ Long function!" if body_lines > 50 else ""
                    st.markdown(
                        f"- `{fn['name']}()` — Line {fn['line']}, "
                        f"{fn['args']} args, {body_lines} lines{warn}"
                    )
        
        with strengths_tab:
            strengths = review.get("strengths", [])
        
            if strengths:
                st.markdown("### ✨ What's Good About Your Code")
                for s in strengths:
                    st.markdown(f"""
                    <div class="strength-item">
                        <span>💪</span> {s}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No specific strengths identified in this review.")
        
        with optimized_tab:
            st.markdown("### ✅ Optimized Code")
            st.markdown("*AI-generated best-practice version of your code with all issues fixed.*")
        
            if optimized_code:
                # Sub-tabs: Diff View vs Full Code
                diff_sub, full_sub = st.tabs(["🔄 Diff View", "📋 Full Code"])
        
                with diff_sub:
                    # Nested tabs: Unified vs Split (no rerun, unlike radio)
                    unified_view, split_view = st.tabs(["Unified", "Split"])
                    with unified_view:
                        diff_html = generate_diff_html(code_input_display, optimized_code)
                        st.markdown(diff_html, unsafe_allow_html=True)
                    with split_view:
                        split_html = generate_split_diff_html(code_input_display, optimized_code)
                        st.markdown(split_html, unsafe_allow_html=True)
        
                with full_sub:
                    st.code(optimized_code, language=lang_lower)
        
                # Download button for optimized code
                lang_ext_map = {
                    "Python": ".py", "JavaScript": ".js", "TypeScript": ".ts",
                    "Java": ".java", "C++": ".cpp", "C": ".c", "C#": ".cs",
                    "Go": ".go", "Rust": ".rs", "Ruby": ".rb", "PHP": ".php",
                }
                ext = lang_ext_map.get(language_display, ".txt")
                st.download_button(
                    label="📥 Download Optimized Code",
                    data=optimized_code,
                    file_name=f"optimized_code{ext}",
                    mime="text/plain",
                    use_container_width=True,
                )
            else:
                st.warning("Could not generate optimized code. Please try again.")
        
        with report_tab:
            st.markdown("### 📄 Download Full Report")
            report_md = generate_markdown_report(review, language_display, code_input_display)
            st.download_button(
                label="📥 Download Markdown Report",
                data=report_md,
                file_name="code_review_report.md",
                mime="text/markdown",
                use_container_width=True,
            )
            with st.expander("Preview Report"):
                st.markdown(report_md)
        
        
    if chat_col:
        with chat_col:
            # ─── AI Chat Follow-up ──────────────────────────────────────────────────
            st.markdown("---")
            
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown("## 💬 AI Chat")
            with c2:
                if st.session_state.get("chat_messages"):
                    if st.button("🗑️ Clear", key="clear_chat", use_container_width=True):
                        st.session_state["chat_messages"] = []
                        st.rerun()

            st.markdown("*Ask follow-up questions about your code or the review results.*")

            # Initialize chat history
            if "chat_messages" not in st.session_state:
                st.session_state["chat_messages"] = []

            # Scrollable container for messages
            chat_container = st.container(height=500)
            
            with chat_container:
                # Suggested prompts
                if not st.session_state["chat_messages"]:
                    st.markdown("**💡 Try asking:**")
                    suggest_cols = st.columns(1)
                    suggestions = [
                        "How do I fix the most critical issue?",
                        "Explain the security concerns",
                        "Can you refactor this to be more readable?",
                    ]
                    for i, suggestion in enumerate(suggestions):
                        if st.button(suggestion, key=f"suggest_{i}", use_container_width=True):
                            st.session_state["chat_messages"].append({"role": "user", "content": suggestion})
                            st.rerun()

                # Display chat history
                for msg in st.session_state["chat_messages"]:
                    with st.chat_message(msg["role"]):
                        st.markdown(msg["content"])

                # Generate AI response inline inside the scrollable container
                if (st.session_state["chat_messages"]
                    and st.session_state["chat_messages"][-1]["role"] == "user"):
                    with st.chat_message("assistant"):
                        with st.spinner("🤖 Thinking..."):
                            try:
                                chat_engine = CodeReviewEngine(api_key=api_key, model_name=selected_model_display)
                                review_summary = review.get("summary", "No summary available.")
                                ai_response = chat_engine.chat(
                                    messages=st.session_state["chat_messages"],
                                    code=code_input_display,
                                    review_summary=review_summary,
                                    language=language_display,
                                )
                            except Exception as e:
                                ai_response = f"⚠️ Could not get a response: {str(e)[:200]}"
                
                        st.markdown(ai_response)
                        st.session_state["chat_messages"].append({"role": "assistant", "content": ai_response})

            # Chat input sits OUTSIDE the scrollable container, pinned at the bottom
            if user_question := st.chat_input("Ask about your code or the review..."):
                st.session_state["chat_messages"].append({"role": "user", "content": user_question})
                st.rerun()
            
            
# ─── Review History Dashboard (Persistent — SQLite) ─────────────────────────

db_history = get_all_reviews()
if db_history:
    st.markdown("---")
    st.markdown("## 📊 Review History Dashboard")
    stats = get_stats()
    st.markdown(f"*{stats['total']} review(s) — persisted across sessions*")

    # ── Summary Stats ─────────────────────────────────────────────────
    hs1, hs2, hs3, hs4 = st.columns(4)
    with hs1:
        st.metric("Total Reviews", stats["total"])
    with hs2:
        st.metric("Avg Score", f"{stats['avg_score']}/100")
    with hs3:
        st.metric("Best Score", f"{stats['best_score']}/100")
    with hs4:
        st.metric("Total Issues Found", stats["total_issues"])

    # ── Past Reviews Table ────────────────────────────────────────────
    st.markdown("### 📋 Past Reviews")
    for entry in db_history:
        score = entry.get("score", 0)
        if score >= 80:
            grade = "A"
        elif score >= 60:
            grade = "B"
        elif score >= 40:
            grade = "C"
        else:
            grade = "D"

        review_id = entry.get("id", "?")
        with st.expander(
            f"📝 Review #{review_id}  —  Score: {score}/100 ({grade})  ·  "
            f"{entry.get('language', '?')}  ·  {entry.get('date', '')} {entry.get('timestamp', '')}",
            expanded=False,
        ):
            rc1, rc2, rc3, rc4 = st.columns(4)
            with rc1:
                st.metric("Score", f"{score}/100")
            with rc2:
                st.metric("Issues", entry.get("issues_count", 0))
            with rc3:
                st.metric("Model", entry.get("model", "?"))
            with rc4:
                st.metric("Time", f"{entry.get('elapsed', 0)}s")

            st.markdown(f"**Summary:** {entry.get('summary', 'N/A')}")
            st.markdown(f"**Mode:** {entry.get('mode', 'N/A')}")

            with st.expander("View Code Submitted"):
                st.code(entry.get("code_snippet", ""), language=entry.get("language", "python").lower().split()[0])

            if entry.get("optimized_code"):
                with st.expander("View Optimized Code"):
                    st.code(entry.get("optimized_code", ""), language=entry.get("language", "python").lower().split()[0])


# ─── Footer ──────────────────────────────────────────────────────────────────

st.markdown("""
<div class="footer">
    Built with ❤️ by <strong>Code Crusaders</strong> | BMSCE XCEL Hackathon 2026 |
    Powered by <strong>LangChain</strong> + <strong>Groq</strong> + <strong>Streamlit</strong>
</div>
""", unsafe_allow_html=True)

import re

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

header_match = re.search(r'    st\.markdown\("---"\)\n    st\.markdown\("## 📊 Review Results"\)\n', content)
chat_start_match = re.search(r'    # ─── AI Chat Follow-up ──.*?\n', content)
history_match = re.search(r'\n# ─── Review History Dashboard', content)

if not (header_match and chat_start_match and history_match):
    print("Could not find matching sections")
    import sys; sys.exit(1)

results_block = content[header_match.end():chat_start_match.start()]
chat_block = content[chat_start_match.start():history_match.start()]

new_layout = """    st.markdown("---")
    
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
"""

indented_results = "\n".join(["        " + line[4:] if line.startswith("    ") else "        " + line for line in results_block.split("\n")])

new_chat_layout = """
    if chat_col:
        with chat_col:
"""
indented_chat = "\n".join(["            " + line[4:] if line.startswith("    ") else "            " + line for line in chat_block.split("\n")])

new_content = content[:header_match.start()] + new_layout + indented_results + new_chat_layout + indented_chat + content[history_match.start():]

with open("app.py", "w", encoding="utf-8") as f:
    f.write(new_content)

print("Refactored successfully")

"""Browser chat UI for the telecom agent. Run: streamlit run app.py"""
import streamlit as st
from agent import agent

st.set_page_config(page_title="Telecom Support Agent", page_icon="📡")
st.title("📡 Telecom Support Agent")
st.caption("Answers from the FAQ, the telecom guide and past support tickets.")

if "history" not in st.session_state:
    st.session_state.history = []   # list of {"role", "content", "tools"}

# Replay the conversation so far
for m in st.session_state.history:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if m.get("tools"):
            st.caption("🔧 Tools used: " + ", ".join(m["tools"]))

if question := st.chat_input("Ask about plans, billing, issues or a ticket ID..."):
    st.session_state.history.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            messages = [(m["role"], m["content"]) for m in st.session_state.history]
            result = agent.invoke({"messages": messages})
        answer = result["messages"][-1].content
        tools = [tc["name"] for m in result["messages"]
                 for tc in (getattr(m, "tool_calls", None) or [])]
        st.markdown(answer)
        if tools:
            st.caption("🔧 Tools used: " + ", ".join(tools))

    st.session_state.history.append(
        {"role": "assistant", "content": answer, "tools": tools})

with st.sidebar:
    st.header("Try asking")
    st.write("- How do I recharge my plan?")
    st.write("- My internet stopped after switching to 4G")
    st.write("- What happened in ticket TK-002?")
    if st.button("Clear chat"):
        st.session_state.history = []
        st.rerun()

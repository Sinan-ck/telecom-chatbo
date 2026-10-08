"""Telecom support agent. Run: python agent.py"""
from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from tools import ALL_TOOLS

SYSTEM_PROMPT = """You are a telecom customer support agent.

Tool rules:
- General questions (plans, billing, recharge, roaming): use search_faq first.
- Detailed troubleshooting or procedures: use search_guide.
- 'Has this happened before' or similar problems: use search_similar_tickets.
- If the user gives a ticket ID like TK-001: use lookup_ticket.

Answer rules:
- Answer only from tool results. If nothing relevant is found, say you don't know.
- Be concise. Never apologise and never mention earlier responses.
- End with the source in this form: (Source: FAQ 14), (Source: Guide page 3)
  or (Source: Ticket TK-002), using the exact id or page number from the tool result."""

agent = create_agent(
    model=ChatOllama(model="llama3.2:3b", temperature=0),
    tools=ALL_TOOLS,
    system_prompt=SYSTEM_PROMPT,
)

def main():
    history = []
    print("Telecom agent ready. Type 'exit' to quit.")
    while True:
        q = input("\nYou: ").strip()
        if q.lower() in {"exit", "quit"}:
            break
        history.append(("user", q))
        result = agent.invoke({"messages": history})
        for m in result["messages"]:
            for tc in getattr(m, "tool_calls", None) or []:
                print(f"  [tool called: {tc['name']} {tc['args']}]")
        answer = result["messages"][-1].content
        history.append(("assistant", answer))
        print(f"\nAgent: {answer}")

if __name__ == "__main__":
    main()

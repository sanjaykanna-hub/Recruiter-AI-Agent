
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import InMemorySaver

from api.tools import (
    list_jobs,
    get_job_details,
    list_job_applicants,
    get_application_details,
    rank_candidates,
    evaluate_application,
)


# --------------------------------------------------
# 1. Load environment variables
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(ENV_FILE, override=False)

API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

if not API_KEY:
    raise RuntimeError(
        "GOOGLE_API_KEY is missing. Check the .env file in your project root."
    )


# --------------------------------------------------
# 2. Initialize Gemini
# --------------------------------------------------

model = ChatGoogleGenerativeAI(
    model=MODEL_NAME,
    google_api_key=API_KEY,
    temperature=0,
)

# Register all recruiter tools with Gemini.
tools = [
    list_jobs,
    get_job_details,
    list_job_applicants,
    get_application_details,
    rank_candidates,
    evaluate_application,
]

model_with_tools = model.bind_tools(tools)


# --------------------------------------------------
# 3. Define the assistant node
# --------------------------------------------------

def assistant_node(state: MessagesState):
    """Let Gemini answer or request a tool call."""

    response = model_with_tools.invoke(state["messages"])

    return {"messages": [response]}


# --------------------------------------------------
# 4. Build the LangGraph workflow
# --------------------------------------------------

builder = StateGraph(MessagesState)

builder.add_node("assistant", assistant_node)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "assistant")

# Route to the tools when Gemini requests them.
# Otherwise, finish the current response.
builder.add_conditional_edges("assistant", tools_condition)

# Return tool results to the assistant for a final response.
builder.add_edge("tools", "assistant")


# --------------------------------------------------
# 5. Add conversation memory
# --------------------------------------------------

memory = InMemorySaver()

agent = builder.compile(checkpointer=memory)


# --------------------------------------------------
# 6. Public function called by api/main.py
# --------------------------------------------------

def run_agent(message: str, thread_id: str = "default") -> dict:
    """
    Execute the recruiter agent.

    Reusing a thread_id retains conversation context while
    this Python process remains running.
    """

    if not message or not message.strip():
        raise ValueError("Message cannot be empty.")

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": message.strip(),
                }
            ]
        },
        config={
            "configurable": {
                "thread_id": thread_id,
            }
        },
    )

    return result

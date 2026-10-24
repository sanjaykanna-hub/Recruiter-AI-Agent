
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
        "GOOGLE_API_KEY is missing. Check the .env file "
        "in your project root."
    )


# --------------------------------------------------
# 2. Initialize Gemini
# --------------------------------------------------

model = ChatGoogleGenerativeAI(
    model=MODEL_NAME,
    google_api_key=API_KEY,
    temperature=0,
)

# Register recruitment tools
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
    """Let Gemini answer or request a recruitment tool."""

    response = model_with_tools.invoke(state["messages"])

    return {"messages": [response]}


# --------------------------------------------------
# 4. Build the LangGraph workflow
# --------------------------------------------------

builder = StateGraph(MessagesState)

builder.add_node("assistant", assistant_node)
builder.add_node("tools", ToolNode(tools))

# Start with the assistant
builder.add_edge(START, "assistant")

# If Gemini requests a tool, execute it.
# Otherwise, finish the response.
builder.add_conditional_edges(
    "assistant",
    tools_condition,
)

# Return tool results to the assistant
builder.add_edge("tools", "assistant")


# --------------------------------------------------
# 5. Add conversation memory
# --------------------------------------------------

memory = InMemorySaver()

agent = builder.compile(checkpointer=memory)


# --------------------------------------------------
# 6. Run the recruiter agent
# --------------------------------------------------

def run_agent(
    message: str,
    thread_id: str = "default",
) -> dict:
    """
    Run the agent with conversation memory.

    Reuse the same thread_id for follow-up questions.
    Use a different thread_id for a separate conversation.
    """

    if not message or not message.strip():
        raise ValueError("Message cannot be empty.")

    if not thread_id or not thread_id.strip():
        raise ValueError("Thread ID cannot be empty.")

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
            },
            "recursion_limit": 12,
        },
    )

    return result

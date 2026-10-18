
import logging
import inspect
import uuid
from typing import Optional, Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Load environment variables before importing the agent.
load_dotenv()

# Configure server-side logging.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)

logger = logging.getLogger(__name__)

# Import the existing LangGraph agent.
from api.agent import run_agent


app = FastAPI(
    title="Recruiter AI Agent API",
    description="Agentic AI API for recruiter and candidate workflows.",
    version="1.0.0",
)


# -----------------------------
# Request and response schemas
# -----------------------------

class AgentRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        description="The instruction or question for the AI agent.",
    )
    thread_id: Optional[str] = Field(
        default=None,
        description="Conversation ID used to maintain conversation context.",
    )


class AgentResponse(BaseModel):
    response: str
    thread_id: str


# -----------------------------
# Helpers
# -----------------------------

def extract_response(result):
    """Extract clean text from a LangGraph agent result."""

    if isinstance(result, str):
        return result

    if isinstance(result, dict):
        messages = result.get("messages", [])

        if not messages:
            response = result.get("response", "")
            return str(response)

        last_message = messages[-1]
        content = (
            last_message.get("content", "")
            if isinstance(last_message, dict)
            else getattr(last_message, "content", "")
        )

        # Gemini may return content as a list of text blocks.
        if isinstance(content, list):
            text_parts = []

            for block in content:
                if isinstance(block, dict):
                    if block.get("type") == "text":
                        text_parts.append(block.get("text", ""))
                elif isinstance(block, str):
                    text_parts.append(block)

            return "\n".join(part for part in text_parts if part).strip()

        if isinstance(content, str):
            return content

        return str(content)

    return str(result)


# -----------------------------
# Basic endpoints
# -----------------------------

@app.get("/")
def home():
    return {
        "message": "Recruiter AI Agent API is running.",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Recruiter AI Agent API",
    }


# -----------------------------
# Agent chat endpoint
# -----------------------------

@app.post("/agent/chat", response_model=AgentResponse)
async def chat_with_agent(request: AgentRequest):
    message = request.message.strip()

    if not message:
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty.",
        )

    # Give each new conversation a unique ID.
    thread_id = request.thread_id or str(uuid.uuid4())

    try:
        logger.info(
            "Agent request received. Thread ID: %s",
            thread_id,
        )

        # run_agent may be synchronous or asynchronous.
        result = run_agent(message, thread_id)

        if inspect.isawaitable(result):
            result = await result

        response_text = extract_response(result)

        logger.info(
            "Agent request completed. Thread ID: %s",
            thread_id,
        )

        return AgentResponse(
            response=response_text,
            thread_id=thread_id,
        )

    except HTTPException:
        raise

    except Exception as exc:
        # The traceback is logged in the terminal, not returned to the client.
        logger.exception(
            "Agent request failed. Thread ID: %s",
            thread_id,
        )

        raise HTTPException(
            status_code=502,
            detail=(
                "The agent could not complete the request. "
                "Check the FastAPI terminal logs for the underlying error."
            ),
        ) from exc

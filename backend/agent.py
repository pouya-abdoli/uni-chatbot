import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain.agents import create_agent
from prompts import build_system_prompt

# from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

import queries as q

load_dotenv()

# Wrap each function from queries.py using @tool so the LLM can call them.
TOOLS = [
    tool(f)
    for f in [
        q.course_info,
        q.course_instructors,
        q.instructor_courses,
        q.list_courses,
        q.count_courses,
        q.prerequisites,
        q.corequisites,
        q.can_take_together,
        q.required_by,
        q.courses_without_prereq,
        q.courses_with_prereq_and_coreq,
        q.coreq_pairs,
        q.prereq_pairs,
        q.course_details
    ]
]

# Instantiate the agent with the Gemini model
# agent = create_agent(
#     model=ChatGoogleGenerativeAI(
#         model=os.getenv("MODEL_NAME", "gemini-3.8-flash"), temperature=0
#     ),
#     tools=TOOLS,
#     system_prompt=SYSTEM_PROMPT,
# )

agent = create_agent(
    model=ChatOpenAI(
        model="nvidia/nemotron-3-ultra-550b-a55b:free",
        openai_api_base="https://openrouter.ai/api/v1",
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        temperature=0,
    ),
    tools=TOOLS,
    system_prompt=build_system_prompt(),
)


# Chat interface
def ask(message, history=None):
    """Processes a user message and returns the AI's response.

    Args:
        message: The user's input string
        history: Previous conversation turns: [{"role": ..., "content": ...}, ...]

    Yields:
        str: one text chunk of the assistant's answer, as the model produces it
    """
    # Prevent mutable default argument issues
    if history is None:
        history = []

    # Stream per-chunk events as the agent runs; each event is an LLM output chunk with metadata about its source node.
    for chunk, meta in agent.stream(
        {"messages": history + [{"role": "user", "content": message}]},
        stream_mode="messages",
    ):
        # Forward only text from the final `model` node, skipping tool messages and empty chunks.
        if meta["langgraph_node"] == "model" and chunk.text:
            yield chunk.text

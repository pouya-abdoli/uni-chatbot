import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI

import queries as q

load_dotenv()

# Wrap each function from queries.py using @tool
TOOLS = [
    tool(f)
    for f in [
        q.search_courses,
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
    ]
]

# Define the AI's persona, contraints, and operational workflow
SYSTEM_PROMPT = """تو دستیار دانشجویان رشته مهندسی کامپیوتر هستی. فارسی، کوتاه و ساده جواب بده.

قوانین:
1. اطلاعات را فقط از ابزارها بگیر. حدس نزن.
2. وقتی دانشجو اسم درسی را می‌نویسد، اول ابزار search_courses را صدا بزن تا کد درس را بگیری. بعد کد را به ابزارهای دیگر بده.
3. «حل تمرین» و «آزمایشگاه» درس‌های جدا هستند. اگر چند درس پیدا شد و مطمئن نیستی، از دانشجو بپرس.
4. اگر درسی پیدا نشد، بگو چنین درسی پیدا نشد.
5. پیش‌نیاز یعنی باید قبلاً پاس شده باشد. هم‌نیاز یعنی در همان ترم گرفته می‌شود و می‌شود هر دو را با هم برداشت.
6. اگر ابزارها جواب را ندارند (مثل شرایط انتخاب واحد)، بگو فعلاً نمی‌دانم و از آموزش بپرسد."""

# Instantiate the agent with the Gemini model
agent = create_agent(
    model=ChatGoogleGenerativeAI(
        model=os.getenv("MODEL_NAME", "gemini-3.8-flash"), temperature=0
    ),
    tools=TOOLS,
    system_prompt=SYSTEM_PROMPT,
)


# Chat interface
def ask(message, history=None):
    """Processes a user message and returns the AI's response.

    Args:
        message: The user's input string.
        history: List of previous conversation dicts (role, content).
    """
    # Prevent mutable default argument issues
    if history is None:
        history = []
    result = agent.invoke(
        {"messages": history + [{"role": "user", "content": message}]}
    )
    # Extract and return only the final text response from the agent
    return result["messages"][-1].text

import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain.agents import create_agent

# from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

import queries as q

load_dotenv()

# Wrap each function from queries.py using @tool so the LLM can call them.
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

# Define agent's persona, rules, and workflow (Persian, tuned for CS students).
SYSTEM_PROMPT = """تو دستیار دانشجویان رشته مهندسی کامپیوتر هستی. فارسی، کوتاه و ساده جواب بده.

## قوانین بسیار مهم (حتماً رعایت کن):
1. اطلاعات را **فقط** از ابزارها (Tools) بگیر. هرگز از خودت چیزی نساز یا حدس نزن.
2. **هرگز** کدهای JSON، نام ابزارها یا ساختارهای برنامه‌نویسی را در جواب نهایی به کاربر نشان نده. فقط جواب نهایی و محاوره‌ای را بنویس.
3. وقتی دانشجو اسم یک درس را می‌گوید، **اول** باید ابزار `search_courses` را صدا بزنی تا کد آن درس را پیدا کنی. **سپس** از آن کد برای ابزارهای دیگر استفاده کن.
4. «حل تمرین» و «آزمایشگاه» درس‌های جداگانه‌ای هستند. اگر اسم درس مبهم بود یا چند نتیجه پیدا شد، از دانشجو بپرس منظورش کدام است.
5. اگر ابزاری نتیجه‌ای پیدا نکرد، صادقانه بگو «چنین درسی پیدا نشد» و چیزی از خودت درنیاور.
6. پیش‌نیاز یعنی درسی که باید قبلاً پاس شده باشد. هم‌نیاز یعنی درسی که باید در همان ترم با آن برداشته شود.
7. اگر جواب سوالی در ابزارها نبود (مثل شرایط انتخاب واحد یا قوانین آموزش)، بگو «من در مورد این موضوع اطلاعاتی ندارم، لطفاً از آموزش دانشگاه بپرسید».

## لیست دروس موجود در دانشگاه (برای راهنمایی):
- ریاضیات پایه(پیش نیاز دانشگاهی)
- ریاضی عمومی 1
- حل تمرین ریاضی 1
- فیزیک مکانیک (پیش نیاز دانشگاهی)
- فیزیک 1
- حل تمرین فیزیک 1
- مبانی کامپیوتر و برنامه‌سازی
- کارگاه کامپیوتر
- معادلات دیفرانسیل
- مدارهای منطقی
- برنامه‌سازی پیشرفته
- ریاضیات گسسته
- ریاضی‌ عمومی‌ 2
- حل تمرین ریاضی 2
- ساختمان‌های داده
- تحلیل‌ و طراحی سیستم ها
- مدار‌های الکتریکی
- معماری‌ کامپیوتر
- فیزیک 2
- حل تمرین فیزیک 2
- آزمایشگاه مدارهای منطقی و معماری کامپیوتر
- سیستم های عامل
- آمار و احتمال مهندسی
- طراحی الگوریتم‌ها
- نظریه زبان‌ها و ماشین‌ها
- ریاضیات مهندسی
- آزمایشگاه فیزیک 2
- آزمایشگاه سیستم‌های عامل
- اصول طراحی کامپایلر
- ریزپردازنده و زبان اسمبلی
- مهندسی نرم افزار
- هوش مصنوعی و سیستم های خبره
- سیگنال ها و سیستم ها
- زبان‌ تخصصی‌
- شبکه‌های کامپیوتری
- پایگاه‌ داده‌ها
- آزمایشگاه ریزپردازنده
- طراحی زبان های برنامه سازی
- اصول فناوری اطلاعات
- طراحی کامپیوتری سیستمهای دیجیتال
- روش پژوهش و ارائه
- مهندسی‌ اینترنت‌
- کارگاه برنامه نویسی مت لب
- آزمایشگاه شبکه ‌های‌ کامپیوتری‌
- مبانی داده کاوی
- سیستمهای اطلاعات مدیریت
- پیاده سازی سیستم پایگاه داده
- آزمایشگاه مهندسی نرم‌افزار
- آزمایشگاه پایگاه داده
- پروژه نرم افزار
- مبانی بازبابی اطلاعات وجستجوی وب
- کارآموزی"""

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
        model="openrouter/free",
        openai_api_base="https://openrouter.ai/api/v1",
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        temperature=0,
    ),
    tools=TOOLS,
    system_prompt=SYSTEM_PROMPT,
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

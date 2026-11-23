import json
import os

from agents import Agent, Runner, function_tool, set_default_openai_api
from dotenv import load_dotenv

import shop_tools

# טוענים את המשתנים מהקובץ .env (המפתח ושם המודל)
load_dotenv()
MODEL = os.getenv("OPENAI_MODEL")

# ה-SDK עובד כברירת מחדל עם Responses API. שם gpt-4o-mini נתקע בלולאה ומבקש שוב ושוב
# את אותם מחירים. עוברים ל-Chat Completions, כמו ב-agent_api.py, כדי שההשוואה תהיה הוגנת
set_default_openai_api("chat_completions")

QUESTION = "How much do 3 milk and 2 bread cost?"
SYSTEM_PROMPT = "You are a helpful shopping assistant. Answer briefly."  # כמו ב-agent_api.py


# הכלי בשביל ה-SDK: עוטף את get_price מ-shop_tools.py.
# ה-SDK בונה את תיאור הכלי לבד, מהשם, מה-type hints ומה-docstring.
# מקבלת: item - שם המוצר. מחזירה: את המחיר, או הודעה שהמוצר לא נמצא.
@function_tool
def get_price(item: str):
    """Get the price of one item in the shop.

    Args:
        item: Item name, e.g. milk
    """
    return shop_tools.get_price(item)


# הסוכן: הוראות, מודל וכלי. אין כאן לולאה, אין messages ואין JSON שנכתב ביד
agent = Agent(
    name="Shopping assistant",
    instructions=SYSTEM_PROMPT,
    model=MODEL,
    tools=[get_price],
)


# הפונקציה מריצה את הסוכן ומדפיסה מה קרה בכל קריאה למודל.
# מקבלת: question - השאלה של המשתמשת.
# מחזירה: מילון באותו מבנה כמו run_agent ב-agent_api.py.
def run_agent(question):
    # כל הלולאה (קריאה למודל, הרצת כלים, קריאה חוזרת) קורית בתוך השורה הזו
    result = Runner.run_sync(agent, question)

    # משחזרים בדיעבד את הצעדים: raw_responses = תשובה אחת לכל קריאה למודל
    calls = []
    for i, response in enumerate(result.raw_responses, start=1):
        print(f"--- Model call #{i} ---")
        usage = response.usage
        print(f"Tokens: input {usage.input_tokens} / output {usage.output_tokens} / total {usage.total_tokens}")

        # בקשות הכלי שהמודל שלח בקריאה הזו
        tools = []
        for item in response.output:
            if item.type == "function_call":
                args = json.loads(item.arguments)
                request = f"{item.name}(" + ", ".join(f"{k}={v!r}" for k, v in args.items()) + ")"
                print("Tool requested:", request)
                tools.append(request)
        calls.append({"call": i, "tools": tools, "tokens": usage.total_tokens})

    print("Final answer:", result.final_output)

    # סך הטוקנים של כל ההרצה, ה-SDK סוכם אותם בשבילנו
    total = result.context_wrapper.usage
    print(f"Total model calls: {len(calls)}")
    print(f"Total tokens: input {total.input_tokens} / output {total.output_tokens} / total {total.total_tokens}")

    return {
        "answer": result.final_output,
        "calls": calls,
        "num_calls": len(calls),
        "total_tokens": total.total_tokens,
    }


# נקודת הכניסה: מריצה את הסוכן על השאלה הקבועה.
# מקבלת: כלום. מחזירה: כלום.
def main():
    run_agent(QUESTION)


if __name__ == "__main__":
    main()

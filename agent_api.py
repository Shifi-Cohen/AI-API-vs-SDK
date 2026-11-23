import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from shop_tools import get_price

# טוענים את המשתנים מהקובץ .env (המפתח ושם המודל)
load_dotenv()
MODEL = os.getenv("OPENAI_MODEL")

# הלקוח קורא את OPENAI_API_KEY ממשתני הסביבה בעצמו
client = OpenAI()

QUESTION = "How much do 3 milk and 2 bread cost?"
SYSTEM_PROMPT = "You are a helpful shopping assistant. Answer briefly."
MAX_CALLS = 5  # מגבלת ביטחון: לא יותר מ-5 קריאות למודל

# תיאור הכלי ב-JSON, כתוב ביד. כך המודל יודע שיש כלי ואיך לקרוא לו
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_price",
            "description": "Get the price of one item in the shop.",
            "parameters": {
                "type": "object",
                "properties": {
                    "item": {"type": "string", "description": "Item name, e.g. milk"},
                },
                "required": ["item"],
            },
        },
    }
]


# הפונקציה מריצה כלי שהמודל ביקש.
# מקבלת: name - שם הכלי, arguments - הפרמטרים כמחרוזת JSON (כך המודל שולח אותם).
# מחזירה: את התוצאה של הכלי.
def run_tool(name, arguments):
    args = json.loads(arguments)  # מחרוזת JSON -> מילון פייתון
    if name == "get_price":
        return get_price(args["item"])
    return f"Unknown tool: {name}"


# הפונקציה מריצה את הסוכן: הלולאה הידנית מול המודל.
# מקבלת: question - השאלה של המשתמשת.
# מחזירה: מילון עם התשובה, רשימת הקריאות למודל, מספר הקריאות וסך הטוקנים.
def run_agent(question):
    # רשימת ההודעות שאנחנו מנהלים ביד. כל ההיסטוריה נשלחת מחדש בכל קריאה
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]
    calls = []
    answer = None
    total_prompt = total_completion = total_tokens = 0

    while len(calls) < MAX_CALLS:
        # 1. קריאה למודל עם ההודעות ועם תיאור הכלי
        response = client.chat.completions.create(model=MODEL, messages=messages, tools=TOOLS)
        message = response.choices[0].message
        usage = response.usage

        # 2. הדפסת מספר הקריאה והטוקנים שלה, וצבירת הסכום
        print(f"--- Model call #{len(calls) + 1} ---")
        print(f"Tokens: prompt {usage.prompt_tokens} / completion {usage.completion_tokens} / total {usage.total_tokens}")
        total_prompt += usage.prompt_tokens
        total_completion += usage.completion_tokens
        total_tokens += usage.total_tokens
        call = {"call": len(calls) + 1, "tools": [], "tokens": usage.total_tokens}
        calls.append(call)

        # 4. אין בקשת כלי: זו התשובה הסופית, יוצאים מהלולאה
        if not message.tool_calls:
            answer = message.content
            print("Final answer:", answer)
            break

        # 3. המודל ביקש כלים: שומרים את הבקשה שלו בהיסטוריה
        messages.append(message)
        for tool_call in message.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            request = f"{name}(" + ", ".join(f"{k}={v!r}" for k, v in args.items()) + ")"
            print("Tool requested:", request)
            call["tools"].append(request)

            result = run_tool(name, tool_call.function.arguments)
            print("Tool result:", result)

            # מחזירים למודל את התוצאה, מקושרת לבקשה לפי tool_call_id
            messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": str(result)})

    print(f"Total model calls: {len(calls)}")
    print(f"Total tokens: prompt {total_prompt} / completion {total_completion} / total {total_tokens}")

    return {"answer": answer, "calls": calls, "num_calls": len(calls), "total_tokens": total_tokens}


# נקודת הכניסה: מריצה את הסוכן על השאלה הקבועה.
# מקבלת: כלום. מחזירה: כלום.
def main():
    run_agent(QUESTION)


if __name__ == "__main__":
    main()

# מילון המחירים של החנות: שם המוצר (באותיות קטנות) -> מחיר
PRICES = {
    "milk": 1.50,
    "bread": 2.00,
    "eggs": 3.20,
    "apple": 0.80,
    "cheese": 4.50,
    "banana": 0.60,
    "tomato": 0.90,
    "cucumber": 0.70,
    "butter": 3.80,
    "yogurt": 1.20,
    "rice": 2.50,
    "pasta": 1.90,
    "coffee": 6.50,
    "sugar": 1.60,
    "chicken": 8.90,
}


# הפונקציה מחזירה את המחיר של מוצר אחד.
# מקבלת: item - שם המוצר (מחרוזת, לא משנה אם באותיות גדולות או עם רווחים).
# מחזירה: את המחיר (float) אם המוצר קיים, אחרת מחרוזת שאומרת שהמוצר לא נמצא.
def get_price(item: str):
    # מנרמלים את הקלט: מורידים רווחים ומעבירים לאותיות קטנות
    name = item.strip().lower()

    if name in PRICES:
        return PRICES[name]

    # המוצר לא קיים. את רשימת המוצרים המלאה מציג כפתור "דף המוצרים" בממשק (app.py)
    return f"Item '{name}' not found"

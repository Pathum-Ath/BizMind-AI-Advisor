"""
utils.py
─────────────────────────────────────────────────────────────
Helper utilities:
  1. extract_context()  – detect business info from user text
  2. analyse_sales()    – BONUS: basic trend analysis
  3. format_prompt()    – quick-action button prompts
  4. validate_api_key() – sanity check for Groq key
─────────────────────────────────────────────────────────────
"""

import re
import random
from typing import Optional


# ──────────────────────────────────────────────────────────────────────────────
# 1. CONTEXT EXTRACTION
# ──────────────────────────────────────────────────────────────────────────────

BUSINESS_KEYWORDS = {
    "Bakery":       ["bakery", "bread", "cake", "pastry", "baking", "biscuit", "confectionery"],
    "Clothing":     ["clothing", "fashion", "apparel", "garment", "textile", "boutique", "dress"],
    "Electronics":  ["electronics", "gadget", "phone", "laptop", "tech", "device", "repair"],
    "Restaurant":   ["restaurant", "food", "cafe", "diner", "eatery", "catering", "takeaway"],
    "Grocery":      ["grocery", "supermarket", "vegetables", "fruits", "produce", "mart"],
    "Salon":        ["salon", "beauty", "hair", "spa", "nails", "cosmetic", "barbershop"],
    "Pharmacy":     ["pharmacy", "medicine", "drugs", "health", "medical", "chemist"],
    "Agriculture":  ["farm", "agriculture", "crops", "livestock", "harvest", "seeds"],
    "Printing":     ["printing", "stationery", "design", "poster", "banner", "signage"],
    "Retail":       ["retail", "shop", "store", "merchandise", "wholesale"],
}

BUDGET_RE = re.compile(
    r'(?:lkr|rs\.?|usd|\$|€|£|rupees?)?\s*([\d,]+(?:\.\d+)?)\s*(?:k\b)?',
    re.IGNORECASE
)

LOCATIONS = [
    "colombo", "kandy", "galle", "jaffna", "negombo", "matara",
    "kurunegala", "anuradhapura", "sri lanka",
    "nairobi", "lagos", "accra", "dar es salaam",
    "london", "new york", "dubai", "singapore", "sydney",
]

CUSTOMER_SEGMENTS = {
    "Young Adults":   ["young", "youth", "gen z", "millennial", "teen", "student", "university"],
    "Families":       ["family", "families", "parents", "children", "kids", "mothers"],
    "Professionals":  ["office", "professional", "corporate", "executive", "business people"],
    "Elderly":        ["senior", "elderly", "old age", "retired", "pensioner"],
    "Tourists":       ["tourist", "visitor", "traveller", "expat", "foreigner"],
    "General Public": ["everyone", "all ages", "general", "mass market"],
}

SALES_SIGNALS = {
    "Declining / Slow": ["slow", "bad", "declining", "low", "poor", "struggling", "weak", "down"],
    "Growing":          ["growing", "good", "great", "increasing", "busy", "up", "rising"],
    "Stable":           ["stable", "steady", "ok", "okay", "average", "moderate", "flat"],
}


def extract_context(text: str) -> dict:
    updates = {}
    text_lower = text.lower()

    # Detect business type
    for biz_type, keywords in BUSINESS_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            updates["business_type"] = biz_type
            break

    # Detect location
    for loc in LOCATIONS:
        if loc in text_lower:
            updates["location"] = loc.title()
            break

    # Detect budget ✅ FIXED: guard against empty string before float()
    budget_match = BUDGET_RE.search(text)
    if budget_match:
        raw = budget_match.group(1).replace(",", "").strip()
        if raw and float(raw) > 500:
            updates["budget"] = f"{int(float(raw)):,}"

    # Detect customer segment
    for segment, hints in CUSTOMER_SEGMENTS.items():
        if any(h in text_lower for h in hints):
            updates["target_customers"] = segment
            break

    # Detect sales situation
    for situation, signals in SALES_SIGNALS.items():
        if any(s in text_lower for s in signals):
            updates["sales_situation"] = situation
            break

    return updates


# ──────────────────────────────────────────────────────────────────────────────
# 2. SALES TREND ANALYSIS
# ──────────────────────────────────────────────────────────────────────────────

SAMPLE_DATA = {
    "Bakery":      [42000, 45000, 44000, 48000, 50000, 52000],
    "Clothing":    [80000, 75000, 90000, 85000, 95000, 102000],
    "Electronics": [200000, 185000, 220000, 210000, 235000, 255000],
    "Restaurant":  [60000, 65000, 63000, 70000, 72000, 78000],
    "Grocery":     [120000, 118000, 125000, 130000, 128000, 135000],
}

MONTHS = ["November", "December", "January", "February", "March", "April"]


def get_sales_data(business_type: Optional[str] = None) -> dict:
    sales = SAMPLE_DATA.get(business_type, [random.randint(40000, 100000) for _ in range(6)])
    return {"months": MONTHS, "sales": sales}


def analyse_sales(business_type: Optional[str] = None) -> str:
    data   = get_sales_data(business_type)
    sales  = data["sales"]
    months = data["months"]

    changes = [(sales[i] - sales[i-1]) / sales[i-1] * 100 for i in range(1, len(sales))]
    avg     = sum(changes) / len(changes)

    best_i  = sales.index(max(sales))
    worst_i = sales.index(min(sales))

    trend = "📈 Growing"   if avg >  2 else \
            "📉 Declining" if avg < -2 else \
            "➡️ Stable"

    rows = ""
    for i, (m, s) in enumerate(zip(months, sales)):
        chg = f"{changes[i-1]:+.1f}%" if i > 0 else "—"
        rows += f"| {m} | {s:,} | {chg} |\n"

    if avg > 2:
        insight = (
            "Your business is on an upward trajectory! "
            "Now is the ideal time to increase production capacity, "
            "invest in marketing, and consider expanding your product range."
        )
    elif avg < -2:
        insight = (
            f"Sales dipped in {months[worst_i]}. Investigate whether this was due to "
            "seasonality, stock issues, pricing, or reduced marketing. "
            "A targeted promotional campaign in the next 2 weeks could help reverse the trend."
        )
    else:
        insight = (
            "Sales are steady but flat. To break out of this plateau, "
            "try introducing a new product line, running a limited-time promotion, "
            "or focusing on upselling to existing customers."
        )

    report = f"""### 📊 Sales Trend Report *(Sample Data — Last 6 Months)*

| Month | Sales (LKR) | MoM Change |
|-------|-------------|------------|
{rows}
**Overall Trend:** {trend} &nbsp;|&nbsp; **Avg Monthly Change:** {avg:+.1f}%

🏆 **Best Month:** {months[best_i]} &nbsp;({sales[best_i]:,} LKR)
⚠️ **Weakest Month:** {months[worst_i]} &nbsp;({sales[worst_i]:,} LKR)

💡 **Insight:** {insight}
"""
    return report


# ──────────────────────────────────────────────────────────────────────────────
# 3. QUICK-ACTION PROMPT BUILDER
# ──────────────────────────────────────────────────────────────────────────────

def format_prompt(topic: str, business_type: str = "") -> str:
    biz = f" for my {business_type.lower()} business" if business_type else ""

    prompts = {
        "production": (
            f"What products should I focus on producing{biz}? "
            "How much should I produce each week? "
            "Please give specific recommendations with clear reasoning."
        ),
        "marketing": (
            f"Create a complete marketing strategy{biz}. "
            "Which channels should I use, what campaigns would work best, "
            "and how should I allocate my budget across them?"
        ),
        "sales": (
            f"How can I improve my sales{biz}? "
            "Give me 5 specific, actionable tactics I can start this week "
            "to increase revenue and customer retention."
        ),
        "full_plan": (
            f"Give me a complete 30-day business growth plan{biz}. "
            "Cover production targets, marketing activities, sales goals, "
            "and key milestones for each week."
        ),
    }
    return prompts.get(topic, f"Give me actionable business advice{biz}.")


# ──────────────────────────────────────────────────────────────────────────────
# 4. VALIDATION
# ──────────────────────────────────────────────────────────────────────────────

def validate_api_key(key: str) -> bool:
    """Basic check that the string looks like a real Groq API key."""
    return isinstance(key, str) and key.startswith("gsk_") and len(key) > 20
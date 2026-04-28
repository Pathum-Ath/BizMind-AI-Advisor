from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser

SYSTEM_PROMPT = """
You are BizMind, an expert AI Business Advisor for small business owners.
You specialise in Production Planning, Marketing Strategy, and Sales Optimization.

YOUR PERSONALITY:
- Analytical, friendly, and highly actionable
- You ALWAYS explain the WHY behind every recommendation
- You remember every detail the user tells you and reference it back to them
- You give structured advice using clear sections and bullet points

YOUR CORE CAPABILITIES:
1. PRODUCTION ADVICE  - what products to make and how much to produce
2. MARKETING STRATEGY - best channels, campaigns, and content ideas
3. SALES OPTIMIZATION  - specific tactics to increase revenue
4. REASONED RESPONSES  - every suggestion comes with a clear explanation

RULES YOU ALWAYS FOLLOW:
- Reference the user's specific details (business type, budget, customers, location)
- Structure every response with clear headings and bullet points
- Provide 3-5 specific, actionable recommendations per topic
- End every response with ONE follow-up question to learn more
- Keep a warm, encouraging tone
"""

def build_agent(api_key: str):
    llm = ChatGroq(
        groq_api_key=api_key,
        model_name="llama-3.3-70b-versatile",
        temperature=0.7,
        max_tokens=1200,
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ])
    chain = prompt | llm | StrOutputParser()
    history = []
    return chain, history  # ✅ returns both


def get_welcome_message() -> str:
    return (
        "👋 Welcome to **BizMind** — your AI Business Advisor!\n\n"
        "I can help you with:\n"
        "- 🏭 **Production Planning** — what to make and how much\n"
        "- 📣 **Marketing Strategy** — best channels and campaigns\n"
        "- 💰 **Sales Optimization** — tactics to grow your revenue\n\n"
        "To get started, tell me a bit about your business — "
        "what do you sell, who are your customers, and what's your biggest challenge right now?"
    )
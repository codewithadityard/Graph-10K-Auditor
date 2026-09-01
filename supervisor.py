import os
import instructor
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import Literal
from state import AgentState
from dotenv import load_dotenv
load_dotenv()


class Supervisor(BaseModel):
    reasoning: str = Field(
        description="Explain step-by-step why the query belongs to the selected destination."
    )
    decision: Literal["legal_rag", "web_search", "sql_db"] = Field(
        description="Choose 'legal_rag' for document questions, 'sql_db' for database/metrics math, or 'web_search' for external/live data."
    )

def route_query(state: AgentState) -> dict:
    query = state["user_query"]
    
    prompt = f"""
You are an enterprise supervisor routing system for an AI audit pipeline. 
Analyze the user query and route it to EXACTLY ONE of the following nodes:

### 1. 'sql_db' (Structured Data & Financial Math)
- USE WHEN: The query asks for exact numerical metrics, balance sheet floats, financial math, aggregate calculations, or explicitly mentions database tables/rows.
- KEYWORDS: "revenue", "net income", "margin", "calculate", "total assets", "database", "table".
- DO NOT USE WHEN: The user asks for qualitative narrative, policy summaries, or risk explanations.

### 2. 'legal_rag' (Unstructured Text & Document Analysis)
- USE WHEN: The query asks to read, explain, summarize, or extract qualitative narrative from the uploaded SEC 10-K filing or PDF.
- KEYWORDS: "explain what", "summarize", "risk factors", "climate risk", "Item 1A", "read the document".
- DO NOT USE WHEN: The user asks to calculate a numerical ratio or query database tables.

### 3. 'web_search' (External & Live Data)
- USE WHEN: The query requires real-time information, today's market prices, or current news beyond the static 10-K report.
- KEYWORDS: "current stock price", "news today", "latest market data", "trading price right now".
- DO NOT USE WHEN: The answer exists within the uploaded 10-K report or internal SQL database.

### SYMMETRICAL HARD GUARDRAILS:
1. If the user asks about the filing, risks, or document contents -> MUST choose 'legal_rag'.
2. If the user asks for financial numbers or calculations -> MUST choose 'sql_db'.
3. If the user asks for live outside events or stock prices -> MUST choose 'web_search'.

[USER QUERY]: {query}
"""

    client = instructor.from_openai(
        OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1"
        )
    )

    supervision = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        response_model=Supervisor,
        temperature=0.0,  # Zero temperature for deterministic routing
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    print(f"The Reasoning: {supervision.reasoning}")
    print(f"The Decision: {supervision.decision}")

    return {"route_destination": supervision.decision}
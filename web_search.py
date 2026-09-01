from langchain_community.tools import DuckDuckGoSearchRun
from state import AgentState
from client import ollama_base
from langchain_community.utilities import SQLDatabase
import re

def web_search(state: AgentState) -> dict:
    query = state["user_query"]
    search_tool = DuckDuckGoSearchRun()
    
    try:
        search_results = search_tool.invoke(query)
        
        prompt = f"""
        You are a helpful assistant. Read the following web search data and answer the user query accurately.
        
        [USER QUERY]: {query}
        [WEB SEARCH RESULTS]: {search_results}
        """
        
        print("-> Directing web synthesis to Local Ollama Instance (Zero Rate Limits)...")
        
        response = ollama_base.chat.completions.create(
            model="llama3.1", 
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        answer = response.choices[0].message.content
        print(f"The final answer is {answer}")
        
        return {
            "current_draft": answer,
            "is_relevant": "yes",          
            "audit_status": "Approved"      
        }

    except Exception as e:
        print(f"Not able to retrieve information from the website. Error: {e}")
        return {"current_draft": "I'm sorry, the web search failed."}

def sql_agent(state: AgentState) -> dict:
    query = state["user_query"]
    
    try:
        # 1. Connect to DB and dynamically pull schema and sample rows
        db = SQLDatabase.from_uri("sqlite:///company_records.db")
        sql_schema = db.get_table_info()
        
        # 2. Hardened prompt for local models
        sql_prompt = f"""
        You are an expert SQL generator for SQLite. Write a valid SQLite query to answer the user's question based strictly on the provided schema.
        
        CRITICAL RULES:
        1. Return ONLY the raw SQL query.
        2. Do not include any explanations, greetings, or conversational text.
        3. Only query tables and columns that exist in the schema below.
        
        [USER QUERY]: {query}
        [DATABASE SCHEMA]: 
        {sql_schema}
        """
        
        sql_response = ollama_base.chat.completions.create(
            model="llama3.1",
            temperature=0.0, # Force deterministic output
            messages=[{"role": "user", "content": sql_prompt}]
        )
        
        generated_text = sql_response.choices[0].message.content.strip()
            
        # 3. Resilient SQL Extraction
        # Look for everything between SELECT/WITH and the first semicolon
        sql_match = re.search(r"((?:SELECT|WITH)\b.*?;)", generated_text, re.IGNORECASE | re.DOTALL)
        
        if sql_match:
            clean_sql = sql_match.group(1).strip()
        else:
            # Fallback if no semicolon is used
            clean_sql = generated_text.replace("```sql", "").replace("```", "").strip()

        print(f"-> Executing SQL Query: {clean_sql}")

        # 4. Execute the SQL
        raw_results = db.run(clean_sql)

        # 5. Synthesize back to English
        english_prompt = f"""
        You are a financial analyst. Convert the raw database results into a clear, concise English answer to the user's question.

        [USER QUESTION]: {query}
        [SQL EXECUTED]: {clean_sql}
        [RAW DATABASE RESULTS]: {raw_results}
        """
        
        answer_response = ollama_base.chat.completions.create(
            model="llama3.1",
            temperature=0.3,
            messages=[{"role": "user", "content": english_prompt}]
        )
        
        answer = answer_response.choices[0].message.content.strip()
        print(f"The final answer is: {answer}")

        return {
            "current_draft": answer,
            "is_relevant": "yes",
            "audit_status": "Approved"
        }

    except Exception as e:
        print(f"SQL Agent Failed. Error: {e}")
        return {"current_draft": "I'm sorry, I encountered an error while querying the database."}
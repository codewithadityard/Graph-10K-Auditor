# 🏦 Graph-10K-Auditor: Autonomous Multi-Agent Financial Pipeline

An enterprise-grade, autonomous AI agent architecture designed to audit massive SEC 10-K filings without numerical hallucinations. Built with **LangGraph**, **Gemini**, **Instructor**, and **Llama 3.1**.

## 🚀 The Problem It Solves
Standard RAG pipelines fail when tasked with enterprise financial analysis because they treat quantitative balance sheets and qualitative risk narratives identically. Dumping unstructured financial tables into an LLM context window leads to arithmetic errors and ungrounded answers. 

**Graph-10K-Auditor** solves this by decoupling numerical computation to a deterministic SQL engine while reserving LLMs strictly for reasoning, synthesis, and self-correcting text validation.

## 🧠 Core Architecture

The system is powered by a **Symmetrical Tri-Route Supervisor** utilizing Pydantic structured outputs (`Literal`) to dynamically route incoming queries into three deterministic execution pathways:

1. 🗄️ **Structured SQL (`sql_db`):** Translates natural language into verified SQLite queries for deterministic balance sheet metrics (e.g., net revenue, total assets).
2. 📄 **Unstructured Document RAG (`legal_rag`):** Combines FAISS vector retrieval with Cross-Encoder re-ranking to extract qualitative legal narratives and Item 1A risk disclosures.
3. 🌐 **Live Web Search (`web_search`):** Recognizes the temporal boundaries of static filings to fetch real-time market data and live trading prices.

### 🛡️ Self-Reflective Hallucination Critic
Draft responses in the RAG route are audited sentence-by-sentence against source context chunks. If unsupported claims or omissions are detected, the system refutes the draft and forces the generator to self-correct before presenting a verified output.

---

## 💻 Execution Traces

### Route 1: Deterministic SQL Extraction

> Enter your legal question: 
What was the exact amount of total net revenue and total assets reported by JPMorgan Chase at the end of 2025?

⏳ Processing... (Routing through LangGraph State Machine)
[REASONING] The user requests specific financial figures... categorizing as financial math.
[DECISION] -> Route to: sql_db

✅ VERIFIED OUTPUT :

Based on the raw database results, the exact amount of total net revenue and total assets reported by JPMorgan Chase at the end of 2025 is:
* Total net revenue: $182,447,000,000
* Total assets: $4,424,900,000,000

📊 Metrics: 0 Graph Loops | Final Audit: Approved | Context Relevant: Yes


### Route 2: Self-Correcting RAG Validation

> Enter your legal question: 
Based on the jpmorgan_sec_10k_report.pdf, what specific physical and transition climate change risks does the firm identify?

⏳ Processing... (Routing through LangGraph State Machine)
[DECISION]: -> Route to: legal_rag

--- [NODE] EXECUTING STRUCTURAL RAG ENGINE ---
[SEARCH & RERANK]: Vector matched 10 blocks -> Cross-Encoder kept 1 highly relevant chunk.
[RELEVANCE]: True (Context explicitly mentions physical/transition risks).

--- [NODE] EXECUTING GENERATOR & CRITIC ---
[AUDIT]: Status = Refuted (Discrepancies found, looping back)
[CORRECTION]: Self-correction loop triggered due to hallucination.
[AUDIT]: Status = Approved (Every sentence perfectly aligned with context).


✅ VERIFIED OUTPUT:

JPMorgan Chase identifies specific physical and transition climate change risks. Physical risks include the increased frequency or severity of acute weather events and shifting climate patterns. Transition risks include evolving regulatory requirements...

📊 Metrics: 1 Graph Loop | Final Audit: Approved | Context Relevant: Yes

### Route 3: web Search 

> Enter your legal question: 
What is the live trading price of JPM stock today, and what is the latest market news regarding their new Apple Card portfolio?

⏳ Processing... (Routing through LangGraph State Machine)

[REASONING] 
The user requests the current trading price of JPM stock and the latest market news about their new Apple Card portfolio, which requires real-time external data not present in the uploaded 10-K or internal database. Therefore, the appropriate node is web_search.

[DECISION] 
-> Route to: web_search

[EXECUTING WEB SEARCH] 
-> Directing web synthesis to Local Ollama Instance (Zero Rate Limits)...


✅ VERIFIED OUTPUT

The current live trading price of JPM stock today is $361.09, and the latest market news regarding their new Apple Card portfolio is not mentioned in the search results. However, the search results do mention that analysts remain cautiously optimistic about JPM's future growth amidst rising expenses and market risks, and that technical and fundamental signals align bullish.


📊 Metrics: 0 Graph Loops | Final Audit: Approved | Context Relevant: yes

🛠️ Installation & Setup
Clone the repository:

Bash
git clone [https://github.com/codewithadityard/Graph-10K-Auditor.git](https://github.com/codewithadityard/Graph-10K-Auditor.git)
cd Graph-10K-Auditor
Create a virtual environment & install dependencies:

Bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
Set up Environment Variables:
Create a .env file in the root directory and add your API keys:

Code snippet
GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here
Run the System:
Initialize the database, index the documents, and start the LangGraph agent:

Bash
python indexing.py
python main.py

⚙️ Tech Stack:

1. Orchestration: LangGraph, LangChain

2.Models: Gemini 2.5 Flash, Llama 3.1 (via Groq)

3.Structured Outputs: Instructor, Pydantic

4.Retrieval: FAISS, SentenceTransformers, Cross-Encoders

5.Data Parsing: PyMuPDF, SQLite3


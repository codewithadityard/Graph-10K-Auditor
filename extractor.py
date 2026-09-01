import sqlite3
from PyPDF2 import PdfReader
from pydantic import BaseModel, Field
from client import gemini_client  # Your instructor-wrapped client

# 1. Define the shape of SEC 10-K financial data
class FinancialData(BaseModel):
    company_name: str = Field(
        description="Name of the reporting financial institution or company (e.g., 'JPMorgan Chase & Co.')."
    )
    fiscal_year: int = Field(
        description="The primary fiscal year reported in the document (e.g., 2023, 2024, or 2025)."
    )
    total_revenue: float = Field(
        description="Total net revenue / total interest and noninterest revenue in USD float. Convert billions/millions to full figures (e.g. $158.1 Billion -> 158100000000.0). Output 0.0 if not found."
    )
    net_income: float = Field(
        description="Net income / net profit in USD float. Convert to full numerical value. Output 0.0 if not found."
    )
    total_assets: float = Field(
        description="Total consolidated assets in USD float. Output 0.0 if not found."
    )
    operating_expenses: float = Field(
        description="Total noninterest expense or operating expense in USD float. Output 0.0 if not found."
    )
    summary_notes: str = Field(
        description="A concise 1-2 sentence summary of the overall financial performance for the year."
    )

import re
from PyPDF2 import PdfReader

def extract_text_from_pdf(pdf_path: str) -> str:
    """Intelligently searches for the financial tables using Regex to handle PDF line breaks."""
    reader = PdfReader(pdf_path)
    start_page = 0
    
    print(f"-> Scanning {len(reader.pages)} pages for financial statements...")
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            # Flatten the text to destroy hidden line breaks and double spaces
            clean_text = text.replace('\n', ' ').replace('  ', ' ')
            
            # Look for the Item 8 header or the Income Statement title
            match_found = re.search(r"Item 8\.\s*Financial Statements", clean_text, re.IGNORECASE) or \
                          re.search(r"Consolidated Statements of Income", clean_text, re.IGNORECASE)
            
            # Require the match to be AFTER page 20 to avoid tripping on the Table of Contents
            if match_found and i > 20: 
                start_page = max(0, i - 1)
                print(f"-> Target section located around page {i}!")
                break
                
    end_page = min(len(reader.pages), start_page + 25)
    print(f"-> Smart Filter: Extracting pages {start_page} to {end_page}...")
    
    targeted_text = ""
    for i in range(start_page, end_page):
        page_text = reader.pages[i].extract_text()
        if page_text:
            targeted_text += page_text + "\n"
            
    return targeted_text


def ingest_financial_report(pdf_path: str):
    print(f"Processing 10-K document: {pdf_path}")
    
    # 2. Extract raw text from the ENTIRE document
    raw_text = extract_text_from_pdf(pdf_path)
    print("-> Full text extracted. Sending to Gemini 2.5 Flash...")

    # 3. Instruct Gemini to extract full numeric financial metrics
    prompt = f"""
    You are an expert financial auditor. Read the following SEC Form 10-K text and extract the core consolidated financial figures.
    Ensure all monetary numbers are converted to full float values in USD (for example, convert $150 Million to 150000000.0 and $3.8 Trillion to 3800000000000.0).
    If a figure is not explicitly found, output 0.0.
    
    [SEC 10-K REPORT TEXT]:
    {raw_text}
    """

    extracted_data = gemini_client.chat.completions.create(
        model="gemini-2.5-flash",
        response_model=FinancialData,
        messages=[{"role": "user", "content": prompt}]
    )

    print(f"\n-> Extraction Complete!")
    print(f"   Company:       {extracted_data.company_name}")
    print(f"   Fiscal Year:   {extracted_data.fiscal_year}")
    print(f"   Total Revenue: ${extracted_data.total_revenue:,.2f}")
    print(f"   Net Income:    ${extracted_data.net_income:,.2f}")
    print(f"   Total Assets:  ${extracted_data.total_assets:,.2f}")

    # 4. Insert real extracted data into the 'financials' table
    conn = sqlite3.connect("company_records.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO financials (
            company_name, fiscal_year, report_type, total_revenue, net_income, total_assets, operating_expenses, summary_notes
        ) VALUES (?, ?, '10-K', ?, ?, ?, ?, ?)
    """, (
        extracted_data.company_name,
        extracted_data.fiscal_year,
        extracted_data.total_revenue,
        extracted_data.net_income,
        extracted_data.total_assets,
        extracted_data.operating_expenses,
        extracted_data.summary_notes
    ))
    
    conn.commit()
    conn.close()
    print("\n 10-K financial metrics successfully saved to 'financials' table!")

if __name__ == "__main__":
    target_pdf = "data/jpmorgan_sec_10k_report.pdf" 
    ingest_financial_report(target_pdf)
import sqlite3

def init_database():
    # Connects to the local SQLite file.
    conn = sqlite3.connect("company_records.db")
    cursor = conn.cursor()

    # 1. Drop the old mock contracts table to cleanly remove vendor data
    cursor.execute("DROP TABLE IF EXISTS contracts")
    
    # 2. Drop the financials table (optional: ensures a fresh start if you run this multiple times)
    cursor.execute("DROP TABLE IF EXISTS financials")

    # 3. Create the new financials table for 10-K metrics
    cursor.execute("""
        CREATE TABLE financials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            fiscal_year INTEGER NOT NULL,
            report_type TEXT DEFAULT '10-K',
            total_revenue REAL,
            net_income REAL,
            total_assets REAL,
            operating_expenses REAL,
            summary_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print("Successfully initialized 'company_records.db' with the new 'financials' table!")

if __name__ == "__main__":
    init_database()
import sqlite3

def create_rules_db():
    conn = sqlite3.connect("loan_rules.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS loan_rules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        loan_type TEXT NOT NULL,
        field TEXT NOT NULL,
        operator TEXT NOT NULL,
        value TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()

def insert_sample_rules():
    rules = [
        ("personal", "creditScore", ">=", "700"),
        ("personal", "monthlyIncome", ">=", "30000"),
        ("personal", "age", "between", "21,60"),
        ("personal", "existingLoans", "<=", "2"),
        ("home", "creditScore", ">=", "750"),
        ("home", "monthlyIncome", ">=", "50000"),
        ("home", "age", "between", "25,65"),
        ("home", "propertyValue", ">=", "1000000"),
        ("auto", "creditScore", ">=", "680"),
        ("auto", "monthlyIncome", ">=", "25000"),
        ("auto", "age", "between", "21,60"),
        ("auto", "vehicleType", "in", "car,bike,scooter"),
        ("education", "age", "between", "18,35"),
        ("education", "courseType", "in", "graduate,postgraduate,phd"),
        ("education", "institutionAccredited", "==", "True"),
        ("msme", "businessAge", ">=", "2"),
        ("msme", "monthlyRevenue", ">=", "100000"),
        ("msme", "gstRegistered", "==", "True")
    ]
    conn = sqlite3.connect("loan_rules.db")
    cursor = conn.cursor()
    cursor.executemany("""
    INSERT INTO loan_rules (loan_type, field, operator, value)
    VALUES (?, ?, ?, ?)
    """, rules)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_rules_db()
    insert_sample_rules()
    print("✅ Database setup complete.")
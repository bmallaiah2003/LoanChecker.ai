import sqlite3

def fetch_loan_types():
    conn = sqlite3.connect("loan_rules.db")
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT loan_type FROM loan_rules")
    types = [row[0] for row in cursor.fetchall()]
    conn.close()
    return types

def fetch_rules(loan_type):
    conn = sqlite3.connect("loan_rules.db")
    cursor = conn.cursor()
    cursor.execute("SELECT field, operator, value FROM loan_rules WHERE loan_type = ?", (loan_type,))
    rules = cursor.fetchall()
    conn.close()
    return rules

def evaluate_applicant(rules, applicant_data):
    failed_rules = []
    for field, operator, value in rules:
        user_val = applicant_data.get(field)

        if operator == "between":
            low, high = map(int, value.split(","))
            if not (low <= user_val <= high):
                failed_rules.append(f"{field} must be between {low} and {high}")
        elif operator == "in":
            options = value.split(",")
            if str(user_val).lower() not in [opt.lower() for opt in options]:
                failed_rules.append(f"{field} must be one of {options}")
        elif operator == "==":
            if str(user_val).lower() != value.lower():
                failed_rules.append(f"{field} must be {value}")
        else:
            if not eval(f"{user_val} {operator} {value}"):
                failed_rules.append(f"{field} must be {operator} {value}")

    return failed_rules
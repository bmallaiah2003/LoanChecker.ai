import streamlit as st
import httpx
import random
import re
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from rule_engine import fetch_loan_types, fetch_rules, evaluate_applicant

# --- LangChain LLM setup ---
client = httpx.Client(verify=False)
llm = ChatOpenAI(
    base_url="https://genailab.tcs.in/",
    model="azure/genailab-maas-gpt-4o",
    api_key="sk-irfbmk7aqUX42L6SctMf2Q",
    http_client=client
)

prompt_template = PromptTemplate(
    input_variables=["loan_type", "result", "reasons"],
    template="""
You are a loan eligibility assistant. A user applied for a {loan_type} loan.
The result was: {result}

Explain the decision in simple terms. If the user is not eligible, list the reasons: {reasons}
"""
)

chain = LLMChain(llm=llm, prompt=prompt_template)

# --- Streamlit UI ---
st.set_page_config(page_title="Loan Eligibility Checker", layout="wide")
st.markdown("<h1 style='text-align: center; color: navy;'>🏦 Loan Eligibility Checker</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Welcome to our secure loan eligibility checker. Please fill in your details below.</p>", unsafe_allow_html=True)
st.divider()

# Step 1: Loan Type Selection
with st.container():
    st.subheader("📌 Select Loan Type")
    loan_types = fetch_loan_types()
    selected_loan = st.selectbox("Choose a loan product", loan_types)

# Step 2: Applicant Details
rules = fetch_rules(selected_loan)
required_fields = [rule[0] for rule in rules]

st.subheader("👤 Applicant Information")
applicant_data = {}

col1, col2 = st.columns(2)

for i, field in enumerate(required_fields):
    unique_key = f"{selected_loan}_{field}"
    target_col = col1 if i % 2 == 0 else col2

    with target_col:
        if field == "creditScore":
            mobile_number = st.text_input("📱 Mobile Number", key=unique_key)
            if mobile_number:
                if re.fullmatch(r"[6-9]\d{9}", mobile_number):
                    generated_score = random.randint(300, 900)
                    st.success("✅ Valid Mobile Number")
                    st.info(f"🔢 Generated Credit Score: {generated_score}")
                    applicant_data["creditScore"] = generated_score
                else:
                    st.error("❌ Invalid mobile number. Please enter a 10-digit Indian number starting with 6-9.")
                    applicant_data["creditScore"] = 0
            else:
                applicant_data["creditScore"] = 0
        elif field in ["institutionAccredited", "gstRegistered"]:
            applicant_data[field] = st.checkbox(field, key=unique_key)
        elif field in ["vehicleType", "courseType"]:
            applicant_data[field] = st.text_input(field, key=unique_key)
        else:
            applicant_data[field] = st.number_input(field, value=0, key=unique_key)

# Step 3: Document Uploads
required_documents = {
    "personal": ["Payslips", "Aadhar Card", "PAN Card"],
    "home": ["Payslips", "Property Document", "Aadhar Card", "PAN Card"],
    "auto": ["Aadhar Card", "Vehicle Quotation"]
}

st.subheader("📁 Upload Required Documents")
doc_list = required_documents.get(selected_loan.lower(), [])
uploaded_docs = {}

doc_cols = st.columns(len(doc_list))

for i, doc in enumerate(doc_list):
    with doc_cols[i]:
        uploaded_docs[doc] = st.file_uploader(
            f"{doc}",
            type=["pdf", "jpg", "jpeg", "png"],
            key=f"{selected_loan}_{doc.replace(' ', '_')}"
        )

if all(uploaded_docs.values()):
    st.success("✅ All required documents uploaded.")
else:
    st.warning("⚠️ Please upload all required documents before proceeding.")

# Step 4: Eligibility Check
st.divider()
st.subheader("📊 Eligibility Result")

if st.button("Check Eligibility"):
    if not all(uploaded_docs.values()):
        st.error("❌ Please upload all required documents before checking eligibility.")
    elif applicant_data.get("creditScore", 0) == 0:
        st.error("❌ Please enter a valid mobile number to generate credit score.")
    else:
        with st.spinner("🤖 AI is evaluating your loan eligibility..."):
            failed = evaluate_applicant(rules, applicant_data)
            result = "Eligible" if not failed else "Not Eligible"
            reasons = "None" if not failed else "\n".join(failed)

            explanation = chain.run({
                "loan_type": selected_loan,
                "result": result,
                "reasons": reasons
            })

        if not failed:
            st.success(f"✅ You are eligible for a {selected_loan.title()} loan.")
        else:
            st.error(f"❌ You are not eligible for a {selected_loan.title()} loan.")

        st.markdown("### 🤖 AI Explanation")
        st.info(explanation)
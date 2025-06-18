import streamlit as st
import pandas as pd
import csv
from datetime import datetime
import os

DOUBTS_FILE = "doubts.csv"
ADMIN_PASSWORD = st.secrets.get("admin_password", "")

# Initialize doubts CSV if not exists
def init_doubts_csv():
    if not os.path.exists(DOUBTS_FILE):
        with open(DOUBTS_FILE, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Timestamp', 'Name', 'Phone', 'Doubt'])

def save_doubt(name, phone, doubt):
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(DOUBTS_FILE, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, name, phone, doubt])
        return True
    except Exception as e:
        st.error(f"Error saving doubt: {e}")
        return False

def load_doubts():
    if os.path.exists(DOUBTS_FILE):
        return pd.read_csv(DOUBTS_FILE)
    return pd.DataFrame(columns=['Timestamp', 'Name', 'Phone', 'Doubt'])

init_doubts_csv()

st.set_page_config(
    page_title="Intern Doubts - Matrusri",
    page_icon="❓",
    layout="wide"
)

st.title("❓ Intern Doubts & Queries")
st.markdown("---")

st.header("🙋‍♂️ Submit Your Doubt/Query")
with st.form("doubt_form"):
    name = st.text_input("Name *", max_chars=50)
    phone = st.text_input("Phone Number *", max_chars=15, placeholder="e.g. 9876543210")
    doubt = st.text_area("Your Doubt/Query *", height=120)
    submit = st.form_submit_button("Send Doubt")

if submit:
    if name.strip() and phone.strip() and doubt.strip():
        if save_doubt(name.strip(), phone.strip(), doubt.strip()):
            st.success("✅ Your doubt has been submitted! A TechLead will respond soon.")
            st.balloons()
    else:
        st.error("❌ Please fill in all fields.")

st.markdown("---")

with st.expander("🔐 TechLead/Techead Panel (Restricted)", expanded=False):
    admin_input = st.text_input("Enter Admin Password", type="password")
    if admin_input == ADMIN_PASSWORD:
        st.success("🛡️ Access granted. Viewing all submitted doubts.")
        doubts_df = load_doubts()
        if not doubts_df.empty:
            for _, row in doubts_df.sort_values('Timestamp', ascending=False).iterrows():
                with st.container():
                    st.markdown(f"**👤 {row['Name']}** | 📞 {row['Phone']}")
                    st.caption(f"🕒 {row['Timestamp']}")
                    st.markdown(f"**Doubt:** {row['Doubt']}")
                st.markdown("---")
        else:
            st.info("No doubts submitted yet.")
    elif admin_input != "":
        st.error("❌ Incorrect password.")

st.markdown("---")
st.markdown("**From a MECS TechLead** | Built with ❤️ using Streamlit") 
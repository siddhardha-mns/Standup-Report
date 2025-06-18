import streamlit as st
import pandas as pd
import csv
from datetime import datetime
import os

DOUBTS_FILE = "doubts.csv"
RESOLVED_DOUBTS_FILE = "resolved_doubts.csv"
ADMIN_PASSWORD = st.secrets.get("admin_password", "")

# Initialize doubts CSV if not exists
def init_doubts_csv():
    if not os.path.exists(DOUBTS_FILE):
        with open(DOUBTS_FILE, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Timestamp', 'Name', 'Phone', 'Doubt'])
    if not os.path.exists(RESOLVED_DOUBTS_FILE):
        with open(RESOLVED_DOUBTS_FILE, 'w', newline='', encoding='utf-8') as file:
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

def load_resolved_doubts():
    if os.path.exists(RESOLVED_DOUBTS_FILE):
        return pd.read_csv(RESOLVED_DOUBTS_FILE)
    return pd.DataFrame(columns=['Timestamp', 'Name', 'Phone', 'Doubt'])

def resolve_doubt(timestamp):
    try:
        doubts_df = load_doubts()
        resolved_df = load_resolved_doubts()
        doubt_row = doubts_df[doubts_df['Timestamp'] == timestamp]
        if not doubt_row.empty:
            # Append to resolved
            resolved_df = pd.concat([resolved_df, doubt_row], ignore_index=True)
            resolved_df.to_csv(RESOLVED_DOUBTS_FILE, index=False)
            # Remove from active
            doubts_df = doubts_df[doubts_df['Timestamp'] != timestamp]
            doubts_df.to_csv(DOUBTS_FILE, index=False)
            return True
        return False
    except Exception as e:
        st.error(f"Error resolving doubt: {e}")
        return False

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
        resolved_df = load_resolved_doubts()
        if not doubts_df.empty:
            st.markdown("### 🟡 Active Doubts")
            for _, row in doubts_df.sort_values('Timestamp', ascending=False).iterrows():
                with st.container():
                    st.markdown(f"**👤 {row['Name']}** | 📞 {row['Phone']}")
                    st.caption(f"🕒 {row['Timestamp']}")
                    st.markdown(f"**Doubt:** {row['Doubt']}")
                    if st.button(f"✅ Mark as Resolved", key=f"resolve_{row['Timestamp']}"):
                        if resolve_doubt(row['Timestamp']):
                            st.success("Doubt marked as resolved!")
                            st.rerun()
                st.markdown("---")
        else:
            st.info("No active doubts submitted yet.")
        st.markdown("### 🟢 Resolved Doubts")
        if not resolved_df.empty:
            for _, row in resolved_df.sort_values('Timestamp', ascending=False).iterrows():
                with st.container():
                    st.markdown(f"**👤 {row['Name']}** | 📞 {row['Phone']}")
                    st.caption(f"🕒 {row['Timestamp']}")
                    st.markdown(f"**Doubt:** {row['Doubt']}")
                st.markdown("---")
            # Download button for resolved doubts
            csv_data = resolved_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Resolved Doubts as CSV",
                data=csv_data,
                file_name=f"resolved_doubts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No doubts have been marked as resolved yet.")
    elif admin_input != "":
        st.error("❌ Incorrect password.")

st.markdown("---")
st.markdown("**From a MECS TechLead** | Built with ❤️ using Streamlit") 
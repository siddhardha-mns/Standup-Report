import streamlit as st
import pandas as pd
import csv
from datetime import datetime
import os

DOUBTS_FILE = "doubts.csv"
RESOLVED_DOUBTS_FILE = "resolved_doubts.csv"
ASSIGNMENTS_FILE = "assignments.csv"
TECHLEADS = [
    {"name": "srikar", "secret": "techlead_srikar_pw"},
    {"name": "hasini", "secret": "techlead_hasini_pw"},
    {"name": "shiva", "secret": "techlead_shiva_pw"},
    {"name": "puneeth", "secret": "techlead_puneeth_pw"},
    {"name": "satwik", "secret": "techlead_satwik_pw"},
    {"name": "kartik", "secret": "techlead_kartik_pw"},
]
ADMIN_PASSWORD = st.secrets.get("admin_password", "")
ADMIN_TASK_PASSWORD = st.secrets.get("admin_task_password", "")

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

def init_assignments_csv():
    if not os.path.exists(ASSIGNMENTS_FILE):
        with open(ASSIGNMENTS_FILE, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Timestamp', 'Assigned By', 'TechLead', 'Task'])

def save_assignment(admin, techlead, task):
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(ASSIGNMENTS_FILE, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, admin, techlead, task])
        return True
    except Exception as e:
        st.error(f"Error saving assignment: {e}")
        return False

def load_assignments():
    if os.path.exists(ASSIGNMENTS_FILE):
        return pd.read_csv(ASSIGNMENTS_FILE)
    return pd.DataFrame(columns=['Timestamp', 'Assigned By', 'TechLead', 'Task'])

init_doubts_csv()
init_assignments_csv()

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
            # Clear all resolved doubts button
            if st.button("🗑️ Clear All Resolved Doubts"):
                try:
                    with open(RESOLVED_DOUBTS_FILE, 'w', newline='', encoding='utf-8') as file:
                        writer = csv.writer(file)
                        writer.writerow(['Timestamp', 'Name', 'Phone', 'Doubt'])
                    st.success("All resolved doubts have been cleared.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to clear resolved doubts: {e}")
        else:
            st.info("No doubts have been marked as resolved yet.")
    elif admin_input != "":
        st.error("❌ Incorrect password.")

st.markdown("---")

with st.expander("🛡️ Admin Task Assignment Panel (Separate Password)", expanded=False):
    admin_task_input = st.text_input("Enter Admin Task Password", type="password", key="admin_task_pw")
    if admin_task_input == ADMIN_TASK_PASSWORD:
        st.success("Admin access granted. Assign tasks to TechLeads.")
        techlead_names = [t["name"] for t in TECHLEADS]
        task = st.text_area("Task to assign", key="assign_task")
        techlead = st.selectbox("Assign to TechLead", techlead_names, key="assign_techlead")
        if st.button("Assign Task"):
            if task.strip():
                if save_assignment("admin", techlead, task.strip()):
                    st.success(f"Task assigned to {techlead}!")
            else:
                st.error("Please enter a task.")
        st.markdown("---")
        st.markdown("### All Assignments")
        assignments_df = load_assignments()
        if not assignments_df.empty:
            for _, row in assignments_df.sort_values('Timestamp', ascending=False).iterrows():
                st.write(f"[{row['Timestamp']}] {row['TechLead']}: {row['Task']}")
        else:
            st.info("No assignments yet.")
    elif admin_task_input != "":
        st.error("❌ Incorrect password.")

with st.expander("👨‍💻 TechLead Task Panel (Individual Login)", expanded=False):
    techlead_user = st.selectbox("Select TechLead", [t["name"] for t in TECHLEADS], key="techlead_user")
    techlead_pw = st.text_input("Enter TechLead Password", type="password", key="techlead_pw")
    # Get the correct password from secrets
    correct_pw = st.secrets.get(f"techlead_{techlead_user}_pw", "")
    if techlead_pw == correct_pw and techlead_pw != "":
        st.success(f"Welcome, {techlead_user}! Here are your assigned tasks:")
        assignments_df = load_assignments()
        if not assignments_df.empty:
            my_tasks = assignments_df[assignments_df['TechLead'] == techlead_user]
            if not my_tasks.empty:
                for _, row in my_tasks.sort_values('Timestamp', ascending=False).iterrows():
                    st.write(f"[{row['Timestamp']}] {row['Task']}")
            else:
                st.info("No tasks assigned to you yet.")
        else:
            st.info("No assignments yet.")
    elif techlead_pw != "":
        st.error("❌ Incorrect password.")

st.markdown("---")
st.markdown("**From a MECS TechLead** | Built with ❤️ using Streamlit") 
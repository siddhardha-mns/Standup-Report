import streamlit as st
import pandas as pd
import csv
from datetime import datetime
import os

# -----------------------------
# CONFIGURATION
# -----------------------------
st.set_page_config(
    page_title="Matrusri Daily Standup Reports",
    page_icon="📝",
    layout="wide"
)

CSV_FILE = "standup_reports.csv"
ADMIN_PASSWORD = st.secrets.get("admin_password", "")

# -----------------------------
# CSV Initialization
# -----------------------------
def init_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Timestamp', 'GitLab Username', 'Standup Report'])

def load_reports():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    return pd.DataFrame(columns=['Timestamp', 'GitLab Username', 'Standup Report'])

def save_report(username, report):
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(CSV_FILE, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, username, report])
        return True
    except Exception as e:
        st.error(f"Error saving report: {e}")
        return False

# -----------------------------
# Initialize
# -----------------------------
init_csv()

# -----------------------------
# TITLE
# -----------------------------
st.title("📝 Matrusri Daily Standup Reports")
st.markdown("---")

# -----------------------------
# INSTRUCTIONS
# -----------------------------
with st.expander("📋 Instructions for First-Time Users", expanded=False):
    st.markdown("""
    **How to use:**
    1. Enter your GitLab username
    2. Fill in your standup report (yesterday’s tasks, today’s tasks, blockers)
    3. Click Submit
    4. View all reports below
    """)

# -----------------------------
# FORM
# -----------------------------
st.header("📤 Submit Your Daily Standup Report")

col1, col2 = st.columns([1, 2])
with col1:
    username = st.text_input("GitLab Username *", placeholder="Enter GitLab username")
report_text = st.text_area(
    "Daily Standup Report *",
    height=150,
    placeholder="Yesterday: ...\nToday: ...\nBlockers: ..."
)

if st.button("🚀 Submit Report", type="primary"):
    if username.strip() and report_text.strip():
        if save_report(username.strip(), report_text.strip()):
            st.success(f"✅ Report submitted successfully for {username}!")
            st.balloons()
            st.rerun()
    else:
        st.error("❌ Please fill in both GitLab username and report text.")

st.markdown("---")

# -----------------------------
# VIEW REPORTS
# -----------------------------
st.header("📊 All Submitted Reports")

reports_df = load_reports()

if not reports_df.empty:
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        search_username = st.text_input("🔍 Filter by username", placeholder="e.g. johndoe")
    with col2:
        sort_order = st.selectbox("📅 Sort by", ["Newest First", "Oldest First"])
    with col3:
        show_count = st.selectbox("📄 Show entries", [10, 25, 50, "All"])

    filtered_df = reports_df.copy()
    if search_username:
        filtered_df = filtered_df[filtered_df['GitLab Username'].str.contains(search_username, case=False, na=False)]

    if sort_order == "Newest First":
        filtered_df = filtered_df.sort_values('Timestamp', ascending=False)
    else:
        filtered_df = filtered_df.sort_values('Timestamp', ascending=True)

    if show_count != "All":
        filtered_df = filtered_df.head(int(show_count))

    st.info(f"📈 Showing {len(filtered_df)} of {len(reports_df)} total reports")

    for _, row in filtered_df.iterrows():
        with st.container():
            c1, c2 = st.columns([1, 4])
            with c1:
                st.markdown(f"**👤 {row['GitLab Username']}**")
                st.caption(f"🕒 {row['Timestamp']}")
            with c2:
                st.markdown("**Report:**")
                st.write(row['Standup Report'])
        st.markdown("---")
else:
    st.info("📭 No reports submitted yet.")

# -----------------------------
# ADMIN PANEL
# -----------------------------
with st.expander("🔐 Admin Panel (Restricted)", expanded=False):
    admin_input = st.text_input("Enter Admin Password", type="password")
    if admin_input == ADMIN_PASSWORD:
        st.success("🛡️ Access granted.")

        csv_data = reports_df.to_csv(index=False)
        st.download_button(
            label="📥 Download All Reports as CSV",
            data=csv_data,
            file_name=f"standup_reports_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

        st.markdown("### ⚠️ Clear All Reports")
        if st.button("🗑️ Clear All Reports", type="secondary"):
            try:
                # Reinitialize the CSV with just headers
                with open(CSV_FILE, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(['Timestamp', 'GitLab Username', 'Standup Report'])
                st.success("✅ All reports have been cleared.")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Failed to clear reports: {e}")

    elif admin_input != "":
        st.error("❌ Incorrect password.")


# -----------------------------
# FOOTER
# -----------------------------
st.markdown("---")
st.markdown("**From a MECS TechLead** | Built with ❤️ using Streamlit")

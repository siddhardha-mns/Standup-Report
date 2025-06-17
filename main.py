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
            writer.writerow(['Timestamp', 'Date', 'GitLab Username', 'Standup Report'])

def load_reports():
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        # Handle backward compatibility - add Date column if it doesn't exist
        if 'Date' not in df.columns:
            df['Date'] = pd.to_datetime(df['Timestamp']).dt.date
            # Save the updated CSV with Date column
            df.to_csv(CSV_FILE, index=False)
        return df
    return pd.DataFrame(columns=['Timestamp', 'Date', 'GitLab Username', 'Standup Report'])

def has_submitted_today(username):
    """Check if username has already submitted a report today"""
    reports_df = load_reports()
    if reports_df.empty:
        return False
    
    today = datetime.now().date()
    # Convert Date column to date objects for comparison
    reports_df['Date'] = pd.to_datetime(reports_df['Date']).dt.date
    
    # Check if user has submitted today
    user_today = reports_df[
        (reports_df['GitLab Username'].str.lower() == username.lower()) & 
        (reports_df['Date'] == today)
    ]
    
    return not user_today.empty

def save_report(username, report):
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        date = datetime.now().date()
        
        with open(CSV_FILE, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, date, username, report])
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
    2. Fill in your standup report (yesterday's tasks, today's tasks, blockers)
    3. Click Submit (Note: You can only submit **one report per day**)
    4. View all reports below
    
    **Important:** Each user can only submit one standup report per day. If you need to make changes, please contact an admin.
    """)

# -----------------------------
# FORM
# -----------------------------
st.header("📤 Submit Your Daily Standup Report")

col1, col2 = st.columns([1, 2])
with col1:
    username = st.text_input("GitLab Username *", placeholder="Enter GitLab username")

# Check if user has already submitted today
if username.strip():
    if has_submitted_today(username.strip()):
        st.warning(f"⚠️ **{username}** has already submitted a report today ({datetime.now().strftime('%Y-%m-%d')}). You can only submit one report per day.")
        st.info("💡 If you need to update your report, please contact an admin.")
        report_disabled = True
    else:
        st.success(f"✅ **{username}** can submit a report for today.")
        report_disabled = False
else:
    report_disabled = False

report_text = st.text_area(
    "Daily Standup Report *",
    height=150,
    placeholder="Yesterday: ...\nToday: ...\nBlockers: ...",
    disabled=report_disabled
)

submit_button = st.button("🚀 Submit Report", type="primary", disabled=report_disabled)

if submit_button:
    if username.strip() and report_text.strip():
        # Double-check before saving (in case of race conditions)
        if has_submitted_today(username.strip()):
            st.error("❌ You have already submitted a report today!")
        else:
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

        st.markdown("### 📊 Daily Submission Stats")
        if not reports_df.empty:
            # Convert Date column for stats
            reports_df['Date'] = pd.to_datetime(reports_df['Date']).dt.date
            today = datetime.now().date()
            
            today_reports = reports_df[reports_df['Date'] == today]
            st.metric("Reports Submitted Today", len(today_reports))
            
            if not today_reports.empty:
                st.markdown("**Today's Submissions:**")
                for _, row in today_reports.iterrows():
                    st.write(f"- {row['GitLab Username']} at {row['Timestamp']}")

        st.markdown("### ⚠️ Clear All Reports")
        if st.button("🗑️ Clear All Reports", type="secondary"):
            try:
                # Reinitialize the CSV with just headers (including Date column)
                with open(CSV_FILE, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(['Timestamp', 'Date', 'GitLab Username', 'Standup Report'])
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

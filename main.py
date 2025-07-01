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
    layout="wide",
    initial_sidebar_state="expanded"
)

CSV_FILE = "standup_reports.csv"
DOUBTS_FILE = "doubts.csv"
ADMIN_PASSWORD = st.secrets.get("admin_password", "")

# Team options
TEAMS = [
    "Team Alpha",
    "Team Beta", 
    "Team Gamma",
    "Team Delta",
    "Team Epsilon",
    "Team Zeta",
    "Team Eta",
    "Team Theta",
    "Team Iota",
    "Team Kappa"
]

# -----------------------------
# CSV Initialization
# -----------------------------
def init_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Timestamp', 'Date', 'Team', 'GitLab Username', 'Standup Report', 'Comment'])
    else:
        # Add Team and Comment columns if missing
        df = pd.read_csv(CSV_FILE)
        if 'Team' not in df.columns:
            df.insert(2, 'Team', 'Not Specified')  # Insert Team column after Date
            df.to_csv(CSV_FILE, index=False)
        if 'Comment' not in df.columns:
            df['Comment'] = 'Check back later to view comment 📝'
            df.to_csv(CSV_FILE, index=False)
    
    # Doubts file
    if not os.path.exists(DOUBTS_FILE):
        with open(DOUBTS_FILE, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Timestamp', 'Name', 'Phone', 'Doubt'])

def load_reports():
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        # Handle backward compatibility - add Date/Team/Comment columns if missing
        if 'Date' not in df.columns:
            try:
                df['Date'] = pd.to_datetime(df['Timestamp']).dt.strftime('%Y-%m-%d')
                df.to_csv(CSV_FILE, index=False)
            except Exception as e:
                df['Date'] = datetime.now().strftime('%Y-%m-%d')
                df.to_csv(CSV_FILE, index=False)
        if 'Team' not in df.columns:
            df.insert(2, 'Team', 'Not Specified')
            df.to_csv(CSV_FILE, index=False)
        if 'Comment' not in df.columns:
            df['Comment'] = 'Check back later to view admins reply'
            df.to_csv(CSV_FILE, index=False)
        return df
    return pd.DataFrame(columns=['Timestamp', 'Date', 'Team', 'GitLab Username', 'Standup Report', 'Comment'])

def has_submitted_today(username):
    """Check if username has already submitted a report today"""
    try:
        reports_df = load_reports()
        if reports_df.empty:
            return False
        
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        # Filter for this user and today
        user_reports_today = reports_df[
            (reports_df['GitLab Username'].str.strip().str.lower() == username.lower()) & 
            (reports_df['Date'].astype(str).str.contains(today_str))
        ]
        
        return not user_reports_today.empty
        
    except Exception as e:
        st.error(f"Error checking submissions: {e}")
        # If there's any error, allow submission (fail safe)
        return False

def save_report(username, team, report):
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        date = datetime.now().strftime("%Y-%m-%d")
        with open(CSV_FILE, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, date, team, username, report, 'Check back later to view comment 📝'])
        return True
    except Exception as e:
        st.error(f"Error saving report: {e}")
        return False

def save_comment(timestamp, comment):
    try:
        df = pd.read_csv(CSV_FILE)
        df.loc[df['Timestamp'] == timestamp, 'Comment'] = comment
        df.to_csv(CSV_FILE, index=False)
        return True
    except Exception as e:
        st.error(f"Error saving comment: {e}")
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
# SIDEBAR (Custom)
# -----------------------------
st.sidebar.markdown("""
# 📝 **Standup App**
---
**Navigate:**
- 📝 **Standup Reports** (Home)
- ❓ **Intern Doubts** (Sidebar → Intern Doubts & Queries)

---
""")

# -----------------------------
# INSTRUCTIONS
# -----------------------------
with st.expander("📋 Instructions for First-Time Users", expanded=False):
    st.markdown("""
    **How to use:**
    1. Select your team from the dropdown
    2. Enter your GitLab username
    3. Fill in your standup report (yesterday's tasks, today's tasks, blockers)
    4. Click Submit (Note: You can only submit **one report per day**)
    5. View all reports below
    
    **Important:** Each user can only submit one standup report per day. If you need to make changes, please contact an admin.
    """)

# -----------------------------
# FORM
# -----------------------------
st.header("📤 Submit Your Daily Standup Report")

col1, col2 = st.columns([1, 1])
with col1:
    selected_team = st.selectbox("Select Your Team *", TEAMS, index=0)
with col2:
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
            if save_report(username.strip(), selected_team, report_text.strip()):
                st.success(f"✅ Report submitted successfully for {username} from {selected_team}!")
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
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    with col1:
        search_username = st.text_input("🔍 Filter by username", placeholder="e.g. johndoe")
    with col2:
        team_filter = st.selectbox("🏷️ Filter by team", ["All Teams"] + TEAMS)
    with col3:
        sort_order = st.selectbox("📅 Sort by", ["Newest First", "Oldest First"])
    with col4:
        show_count = st.selectbox("📄 Show entries", [10, 25, 50, "All"])

    filtered_df = reports_df.copy()
    
    # Apply username filter
    if search_username:
        filtered_df = filtered_df[filtered_df['GitLab Username'].str.contains(search_username, case=False, na=False)]
    
    # Apply team filter
    if team_filter != "All Teams":
        filtered_df = filtered_df[filtered_df['Team'] == team_filter]

    if sort_order == "Newest First":
        filtered_df = filtered_df.sort_values('Timestamp', ascending=False)
    else:
        filtered_df = filtered_df.sort_values('Timestamp', ascending=True)

    if show_count != "All":
        filtered_df = filtered_df.head(int(show_count))

    st.info(f"📈 Showing {len(filtered_df)} of {len(reports_df)} total reports")

    # Display team statistics
    if not reports_df.empty:
        st.subheader("📊 Team Statistics")
        team_counts = reports_df['Team'].value_counts()
        col1, col2 = st.columns([2, 1])
        with col1:
            st.bar_chart(team_counts)
        with col2:
            st.write("**Reports by Team:**")
            for team, count in team_counts.items():
                st.write(f"• {team}: {count}")

    st.markdown("---")

    for _, row in filtered_df.iterrows():
        with st.container():
            c1, c2 = st.columns([1, 4])
            with c1:
                st.markdown(f"**👤 {row['GitLab Username']}**")
                st.markdown(f"**🏷️ {row.get('Team', 'Not Specified')}**")
                st.caption(f"🕒 {row['Timestamp']}")
            with c2:
                st.markdown("**Report:**")
                st.write(row['Standup Report'])
                if row.get('Comment', ''):
                    st.markdown(f"**💬 Admin Comment:** {row['Comment']}")
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
            try:
                # Safely convert Date column for stats
                def safe_date_convert(date_val):
                    try:
                        if pd.isna(date_val):
                            return None
                        if isinstance(date_val, datetime.date):
                            return date_val
                        return pd.to_datetime(str(date_val)).date()
                    except:
                        return None
                
                reports_df['Date_parsed'] = reports_df['Date'].apply(safe_date_convert)
                today = datetime.now().date()
                
                today_reports = reports_df[reports_df['Date_parsed'] == today]
                st.metric("Reports Submitted Today", len(today_reports))
                
                # Team-wise breakdown for today
                if not today_reports.empty:
                    st.markdown("**Today's Submissions by Team:**")
                    today_team_counts = today_reports['Team'].value_counts()
                    for team, count in today_team_counts.items():
                        st.write(f"• {team}: {count}")
                    
                    st.markdown("**Today's Individual Submissions:**")
                    for _, row in today_reports.iterrows():
                        st.write(f"- {row['GitLab Username']} ({row['Team']}) at {row['Timestamp']}")
            except Exception as e:
                st.warning("Could not load daily stats due to date parsing issues.")

        st.markdown("### 📝 Add/Edit Comments to Reports")
        if not reports_df.empty:
            # Add team filter for admin comments
            admin_team_filter = st.selectbox("Filter by team for comments", ["All Teams"] + TEAMS, key="admin_team_filter")
            admin_filtered_df = reports_df.copy()
            if admin_team_filter != "All Teams":
                admin_filtered_df = admin_filtered_df[admin_filtered_df['Team'] == admin_team_filter]
            
            for idx, row in admin_filtered_df.iterrows():
                with st.expander(f"{row['GitLab Username']} ({row.get('Team', 'Not Specified')}) at {row['Timestamp']}"):
                    st.write(row['Standup Report'])
                    comment = st.text_area(f"Admin Comment for {row['GitLab Username']} ({row['Timestamp']})", value=row.get('Comment', ''), key=f"comment_{row['Timestamp']}")
                    if st.button(f"Save Comment", key=f"save_{row['Timestamp']}"):
                        if save_comment(row['Timestamp'], comment):
                            st.success("Comment saved!")
                            st.rerun()

        st.markdown("### ⚠️ Clear All Reports")
        if st.button("🗑️ Clear All Reports", type="secondary"):
            try:
                # Reinitialize the CSV with just headers (including Team column)
                with open(CSV_FILE, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(['Timestamp', 'Date', 'Team', 'GitLab Username', 'Standup Report', 'Comment'])
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

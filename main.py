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
ADMIN_PASSWORD = st.secrets.get("admin_password", "admin123")  # Default password for demo

# Team options
TEAMS = [
    "Team 1",
    "Team 2", 
    "Team 3",
    "Team 4",
    "Team 5",
    "Team 6",
    "Team 7",
    "Team 8",
    "Team 9",
    "Team 10"
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

def get_user_reports(username):
    """Get all reports for a specific user"""
    reports_df = load_reports()
    if reports_df.empty:
        return pd.DataFrame()
    
    user_reports = reports_df[
        reports_df['GitLab Username'].str.strip().str.lower() == username.lower()
    ].sort_values('Timestamp', ascending=False)
    
    return user_reports

# -----------------------------
# Initialize
# -----------------------------
init_csv()

# Initialize session state for admin access
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False

# -----------------------------
# SIDEBAR
# -----------------------------
with st.sidebar:
    st.markdown("# 📝 **Standup App**")
    st.markdown("---")
    
    # Navigation
    st.markdown("**Navigate:**")
    st.markdown("- 📝 **Standup Reports** (Main)")
    st.markdown("- ❓ **Intern Doubts & Queries**")
    st.markdown("---")
    
    # Admin Panel in Sidebar
    st.markdown("## 🔐 **Admin Panel**")
    
    if not st.session_state.is_admin:
        admin_password = st.text_input("Admin Password", type="password", key="admin_login")
        if st.button("🔓 Login as Admin"):
            if admin_password == ADMIN_PASSWORD:
                st.session_state.is_admin = True
                st.success("✅ Admin access granted!")
                st.rerun()
            else:
                st.error("❌ Incorrect password")
    else:
        st.success("🛡️ Admin Mode Active")
        
        if st.button("🔒 Logout Admin"):
            st.session_state.is_admin = False
            st.rerun()
        
        st.markdown("---")
        
        # Admin features
        reports_df = load_reports()
        
        if not reports_df.empty:
            # Download reports
            csv_data = reports_df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv_data,
                file_name=f"standup_reports_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
            
            # Quick stats
            st.markdown("### 📊 Quick Stats")
            total_reports = len(reports_df)
            today_reports = len(reports_df[reports_df['Date'] == datetime.now().strftime('%Y-%m-%d')])
            unique_users = reports_df['GitLab Username'].nunique()
            
            st.metric("Total Reports", total_reports)
            st.metric("Today's Reports", today_reports)
            st.metric("Active Users", unique_users)
            
            # Clear all reports
            st.markdown("---")
            if st.button("🗑️ Clear All Reports", type="secondary"):
                try:
                    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as file:
                        writer = csv.writer(file)
                        writer.writerow(['Timestamp', 'Date', 'Team', 'GitLab Username', 'Standup Report', 'Comment'])
                    st.success("✅ All reports cleared!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Failed to clear: {e}")

# -----------------------------
# MAIN CONTENT
# -----------------------------
st.title("📝 Matrusri Daily Standup Reports")
st.markdown("---")

# Instructions
with st.expander("📋 Instructions for First-Time Users", expanded=False):
    st.markdown("""
    **How to use:**
    1. Select your team from the dropdown
    2. Enter your GitLab username
    3. Fill in your standup report (yesterday's tasks, today's tasks, blockers)
    4. Click Submit (Note: You can only submit **one report per day**)
    5. View your previous reports below
    
    **Privacy Note:** You can only see your own standup reports. All reports are available to admins for review and feedback.
    """)

# -----------------------------
# FORM SECTION
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
    placeholder="Yesterday: What did I accomplish?\nToday: What will I work on?\nBlockers: What obstacles are impeding my progress?",
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
# USER'S REPORTS SECTION (Non-Admin View)
# -----------------------------
if not st.session_state.is_admin:
    st.header("📋 Your Previous Reports")
    
    if username.strip():
        user_reports = get_user_reports(username.strip())
        
        if not user_reports.empty:
            st.info(f"📈 Showing {len(user_reports)} reports for {username}")
            
            for _, row in user_reports.iterrows():
                with st.container():
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        st.markdown(f"**🏷️ {row.get('Team', 'Not Specified')}**")
                        st.caption(f"🕒 {row['Timestamp']}")
                    with col2:
                        st.markdown("**Your Report:**")
                        st.write(row['Standup Report'])
                        if row.get('Comment', '') and row.get('Comment', '') != 'Check back later to view comment 📝':
                            st.markdown(f"**💬 Admin Feedback:** {row['Comment']}")
                        else:
                            st.caption("⏳ Waiting for admin feedback...")
                st.markdown("---")
        else:
            st.info("📭 No previous reports found. Submit your first report above!")
    else:
        st.info("👆 Enter your GitLab username above to view your previous reports.")

# -----------------------------
# ADMIN VIEW - ALL REPORTS
# -----------------------------
elif st.session_state.is_admin:
    st.header("🛡️ Admin View - All Submitted Reports")
    
    reports_df = load_reports()
    
    if not reports_df.empty:
        # Filters for admin
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
        
        # Apply filters
        if search_username:
            filtered_df = filtered_df[filtered_df['GitLab Username'].str.contains(search_username, case=False, na=False)]
        
        if team_filter != "All Teams":
            filtered_df = filtered_df[filtered_df['Team'] == team_filter]

        if sort_order == "Newest First":
            filtered_df = filtered_df.sort_values('Timestamp', ascending=False)
        else:
            filtered_df = filtered_df.sort_values('Timestamp', ascending=True)

        if show_count != "All":
            filtered_df = filtered_df.head(int(show_count))

        st.info(f"📈 Showing {len(filtered_df)} of {len(reports_df)} total reports")

        # Team Statistics
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

        # Display reports with comment functionality
        st.subheader("📝 Reports & Comments")
        
        for _, row in filtered_df.iterrows():
            with st.expander(f"👤 {row['GitLab Username']} ({row.get('Team', 'Not Specified')}) - {row['Timestamp']}"):
                st.markdown("**Report:**")
                st.write(row['Standup Report'])
                
                st.markdown("**Admin Comment:**")
                comment_key = f"comment_{row['Timestamp']}"
                current_comment = row.get('Comment', '')
                if current_comment == 'Check back later to view comment 📝':
                    current_comment = ''
                
                new_comment = st.text_area(
                    "Add/Edit Comment", 
                    value=current_comment, 
                    key=comment_key,
                    height=100
                )
                
                if st.button(f"💾 Save Comment", key=f"save_{row['Timestamp']}"):
                    if save_comment(row['Timestamp'], new_comment):
                        st.success("✅ Comment saved!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to save comment")
    else:
        st.info("📭 No reports submitted yet.")

# -----------------------------
# FOOTER
# -----------------------------
st.markdown("---")
st.markdown("**From a MECS TechLead** | Built with ❤️ using Streamlit")

import streamlit as st
import pandas as pd
import datetime
import os

# 1. Page Configuration
st.set_page_config(page_title="Agency CRM | WriteWise", page_icon="📊", layout="wide")

# 2. Modern SaaS CSS
st.markdown("""
    <style>
    div[data-testid="metric-container"] { background-color: #ffffff; border: 1px solid #e2e8f0; padding: 15px 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-left: 5px solid #3b82f6; }
    .crm-title { font-size: 2.5rem; font-weight: 800; color: #0f172a; margin-bottom: 0px; }
    .crm-subtitle { color: #64748b; font-size: 1.1rem; margin-bottom: 30px; }
    </style>
""", unsafe_allow_html=True)

# 3. UNIVERSAL DATABASE SETUP (Google Sheets + CSV Fallback)
# IMPORTANT: Agar aapki app Google Sheets use karti hai, toh is section ko edit karein.
# Nahi toh yeh automatically CSV use kar lega!

# --- OPTION A: Google Sheets (UN-COMMENT lines below if USING GOOGLE SHEETS) ---
# import gspread
# from google.oauth2 import service_account
# 
# try:
#     credentials = service_account.Credentials.from_service_account_info(
#         st.secrets["gcp_service_account"],
#         scopes=["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
#     )
#     gc = gspread.authorize(credentials)
#     SHEET_NAME = "WriteWise Orders" # <-- Aapki sheet ka naam yahan daalein
#     worksheet = gc.open(SHEET_NAME).sheet1
#     DB_SOURCE = "Google Sheets"
# except Exception as e:
#     st.warning(f"⚠️ Could not connect to Google Sheets: {e}. Using Local CSV as fallback.")
#     DB_SOURCE = "CSV"

# --- OPTION B: CSV (Default - Agar Google Sheets nahi hai toh yeh use hoga) ---
# Yahan tak comment karein agar Google Sheets use kar rahe hain
DB_FILE = "agency_tasks_db.csv"
DB_SOURCE = "CSV"

def load_data():
    if DB_SOURCE == "Google Sheets":
        try:
            data = worksheet.get_all_records()
            return pd.DataFrame(data)
        except:
            return pd.DataFrame(columns=["Task ID", "Date", "Client Name", "Service", "Writer Assigned", "Status", "Is Revision?", "Revenue ($)", "Writer Cost ($)", "Deadline"])
    else: # CSV
        if os.path.exists(DB_FILE):
            return pd.read_csv(DB_FILE)
        else:
            df = pd.DataFrame(columns=[
                "Task ID", "Date", "Client Name", "Service", "Writer Assigned", 
                "Status", "Is Revision?", "Revenue ($)", "Writer Cost ($)", "Deadline"
            ])
            df.to_csv(DB_FILE, index=False)
            return df

def save_data(df):
    if DB_SOURCE == "Google Sheets":
        try:
            worksheet.clear()
            worksheet.update([df.columns.values.tolist()] + df.values.tolist())
        except Exception as e:
            st.error(f"❌ Failed to save to Google Sheets: {e}")
    else: # CSV
        df.to_csv(DB_FILE, index=False)

# 4. Simple Login System
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.markdown("<h1 style='text-align: center; color: #1e3c72; margin-top: 100px;'>WriteWise Admin CRM 🔒</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        with st.form("login_form"):
            password = st.text_input("Enter Admin Password", type="password")
            submit = st.form_submit_button("Access Dashboard", use_container_width=True)
            
            if submit:
                if password == "admin123": # <-- CHANGE THIS PASSWORD!
                    st.session_state["logged_in"] = True
                    st.rerun()
                else:
                    st.error("❌ Incorrect Password!")
    st.stop()

# ==========================================
# INSIDE THE CRM (IF LOGGED IN)
# ==========================================

# Sidebar Navigation
st.sidebar.markdown("## 📊 WriteWise CRM")
st.sidebar.markdown("Welcome, **Admin**")
page = st.sidebar.radio("Navigation Menu", ["🏠 Dashboard & Analytics", "📝 Task Manager", "📅 Monthly Reports"])

st.sidebar.markdown("---")
if st.sidebar.button("🚪 Logout"):
    st.session_state["logged_in"] = False
    st.rerun()

# Load Data
df = load_data()

# ------------------------------------------
# PAGE 1: DASHBOARD & ANALYTICS
# ------------------------------------------
if page == "🏠 Dashboard & Analytics":
    st.markdown("<h1 class='crm-title'>Agency Overview</h1>", unsafe_allow_html=True)
    st.markdown("<p class='crm-subtitle'>Real-time tracking of your agency's performance.</p>", unsafe_allow_html=True)
    
    if df.empty:
        st.info("No tasks added yet. Go to 'Task Manager' to add your first task.")
    else:
        df['Revenue ($)'] = pd.to_numeric(df['Revenue ($)'], errors='coerce')
        df['Writer Cost ($)'] = pd.to_numeric(df['Writer Cost ($)'], errors='coerce')
        
        total_tasks = len(df)
        total_revenue = df["Revenue ($)"].sum()
        total_cost = df["Writer Cost ($)"].sum()
        net_profit = total_revenue - total_cost
        
        pending_tasks = len(df[df["Status"].isin(["Pending", "In Progress", "In Review"])])
        total_revisions = len(df[df["Is Revision?"] == "Yes"])

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Revenue", f"${total_revenue:,.2f}")
        c2.metric("Net Profit", f"${net_profit:,.2f}")
        c3.metric("Active/Pending Tasks", pending_tasks)
        c4.metric("Total Revisions", total_revisions)
        
        st.write("---")
        st.subheader("Recent Activity")
        st.dataframe(df.tail(5).iloc[::-1], use_container_width=True, hide_index=True)

# ------------------------------------------
# PAGE 2: TASK MANAGER (Add & Edit)
# ------------------------------------------
elif page == "📝 Task Manager":
    st.markdown("<h1 class='crm-title'>Task Manager</h1>", unsafe_allow_html=True)
    st.markdown("<p class='crm-subtitle'>Assign tasks, update statuses, and manage your writers.</p>", unsafe_allow_html=True)

    with st.expander("➕ Add New Task", expanded=False):
        with st.form("add_task_form", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                client = st.text_input("Client Name *")
                service = st.selectbox("Service Type", ["Content Writing", "Academic", "Copywriting", "Resume", "Other"])
            with col2:
                writer = st.selectbox("Assign Writer", ["Unassigned", "Sarah Jenkins", "Dr. Robert Chen", "Elena Rodriguez", "David Alaba", "James Sterling"])
                deadline = st.date_input("Deadline")
            with col3:
                revenue = st.number_input("Revenue Charged to Client ($)", min_value=0.0, step=10.0)
                cost = st.number_input("Cost Paid to Writer ($)", min_value=0.0, step=10.0)
            
            is_rev = st.radio("Is this a Revision?", ["No", "Yes"], horizontal=True)
            
            if st.form_submit_button("Save Task"):
                if client == "":
                    st.error("Client Name is required!")
                else:
                    new_task_id = f"WW-{datetime.datetime.now().strftime('%Y%m%d%H%M')}"
                    new_row = pd.DataFrame([{
                        "Task ID": new_task_id,
                        "Date": datetime.date.today().strftime("%Y-%m-%d"),
                        "Client Name": client,
                        "Service": service,
                        "Writer Assigned": writer,
                        "Status": "Pending",
                        "Is Revision?": is_rev,
                        "Revenue ($)": revenue,
                        "Writer Cost ($)": cost,
                        "Deadline": deadline.strftime("%Y-%m-%d")
                    }])
                    df = pd.concat([df, new_row], ignore_index=True)
                    save_data(df)
                    st.success("✅ Task Added Successfully!")
                    st.rerun()

    st.write("---")
    st.subheader("Live Task Editor")
    st.write("You can directly click on the table below to change 'Status', 'Writer', or 'Deadline'.")
    
    if not df.empty:
        edited_df = st.data_editor(
            df,
            use_container_width=True,
            num_rows="dynamic",
            column_config={
                "Status": st.column_config.SelectboxColumn("Status", options=["Pending", "In Progress", "In Review", "Completed", "Cancelled"], required=True),
                "Is Revision?": st.column_config.SelectboxColumn("Is Revision?", options=["No", "Yes"])
            },
            hide_index=True
        )
        
        if st.button("💾 Save Table Changes", type="primary"):
            save_data(edited_df)
            st.success("Database updated successfully!")
    else:
        st.info("No tasks available to edit.")

# ------------------------------------------
# PAGE 3: MONTHLY REPORTS
# ------------------------------------------
elif page == "📅 Monthly Reports":
    st.markdown("<h1 class='crm-title'>Monthly Generation Report</h1>", unsafe_allow_html=True)
    st.markdown("<p class='crm-subtitle'>Analyze your monthly performance, revisions, and profits.</p>", unsafe_allow_html=True)

    if df.empty:
        st.warning("No data available to generate reports.")
    else:
        df['Date'] = pd.to_datetime(df['Date'])
        col1, col2 = st.columns(2)
        with col1:
            years = df['Date'].dt.year.unique()
            selected_year = st.selectbox("Select Year", sorted(years, reverse=True))
        with col2:
            month_names = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
            selected_month_name = st.selectbox("Select Month", month_names)
            selected_month_num = month_names.index(selected_month_name) + 1

        if st.button("📊 Generate Report", type="primary"):
            mask = (df['Date'].dt.year == selected_year) & (df['Date'].dt.month == selected_month_num)
            report_df = df[mask]
            
            st.write("---")
            st.markdown(f"### Report for {selected_month_name} {selected_year}")
            
            if report_df.empty:
                st.info(f"No tasks recorded in {selected_month_name} {selected_year}.")
            else:
                total_tasks_month = len(report_df)
                new_tasks = len(report_df[report_df["Is Revision?"] == "No"])
                rev_tasks = len(report_df[report_df["Is Revision?"] == "Yes"])
                
                rev_revenue = pd.to_numeric(report_df["Revenue ($)"], errors='coerce').sum()
                rev_cost = pd.to_numeric(report_df["Writer Cost ($)"], errors='coerce').sum()
                rev_profit = rev_revenue - rev_cost

                r1, r2, r3 = st.columns(3)
                r1.metric("Fresh Tasks", new_tasks)
                r2.metric("Revisions", rev_tasks, delta=f"{(rev_tasks/total_tasks_month)*100:.1f}%", delta_color="inverse")
                r3.metric("Monthly Profit", f"${rev_profit:,.2f}")
                
                st.write("")
                st.markdown("#### Detailed Data")
                display_df = report_df.copy()
                display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d')
                st.dataframe(display_df, use_container_width=True, hide_index=True)
                
                csv = display_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label=f"📥 Download {selected_month_name} Report (CSV)",
                    data=csv,
                    file_name=f"WriteWise_Report_{selected_month_name}_{selected_year}.csv",
                    mime="text/csv"
                )

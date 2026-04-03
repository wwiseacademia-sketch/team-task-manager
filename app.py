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

# ==========================================
# 🛑 DATA CONNECTION SETTINGS
# ==========================================
# Yahan par apni purani CSV file ka naam likhein (Agar CSV thi)
DB_FILE = "agency_tasks_db.csv" 

def load_data():
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
    df.to_csv(DB_FILE, index=False)

# ==========================================
# INSIDE THE CRM (NO PASSWORD)
# ==========================================

# Sidebar Navigation
st.sidebar.markdown("## 📊 WriteWise CRM")
page = st.sidebar.radio("Navigation Menu", ["🏠 Dashboard & Analytics", "📝 Task Manager", "📅 Monthly Reports"])

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
        # Convert to numeric to avoid errors
        df['Revenue ($)'] = pd.to_numeric(df['Revenue ($)'], errors='coerce').fillna(0)
        df['Writer Cost ($)'] = pd.to_numeric(df['Writer Cost ($)'], errors='coerce').fillna(0)
        
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
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        
        col1, col2 = st.columns(2)
        with col1:
            years = df['Date'].dt.year.dropna().unique()
            if len(years) > 0:
                selected_year = st.selectbox("Select Year", sorted(years, reverse=True))
            else:
                selected_year = datetime.date.today().year
                st.selectbox("Select Year", [selected_year])
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

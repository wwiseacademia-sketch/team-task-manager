import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="WriteWise Pro CRM", 
    layout="wide", 
    page_icon="⚡",
    initial_sidebar_state="expanded"
)

# --- 2. ULTRA-PREMIUM CSS STYLING ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    /* General Body */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        background-color: #f8fafc;
        color: #0f172a;
    }

    /* Top Dashboard Title */
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #1e3a8a, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
        padding-bottom: 0;
    }

    /* Pending Payments Widget (Sidebar & Main) */
    .money-card {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 10px 20px rgba(15, 23, 42, 0.15);
        text-align: center;
        border-bottom: 4px solid #f59e0b;
        margin-bottom: 20px;
    }
    .money-label { font-size: 0.85rem; font-weight: 600; letter-spacing: 1px; color: #94a3b8; text-transform: uppercase;}
    .money-value { font-size: 2rem; font-weight: 800; margin-top: 5px; color: #f59e0b; }

    /* Assignment Badges */
    .assign-box {
        background: #eff6ff; border-left: 5px solid #3b82f6; padding: 15px 20px;
        border-radius: 8px; color: #1e3a8a; font-weight: 700; margin-bottom: 20px;
        box-shadow: 0 2px 5px rgba(59, 130, 246, 0.05); font-size: 1.1rem;
    }
    .rev-box {
        background: #fff7ed; border-left: 5px solid #f97316; padding: 15px 20px;
        border-radius: 8px; color: #7c2d12; font-weight: 700; margin-bottom: 20px;
        box-shadow: 0 2px 5px rgba(249, 115, 22, 0.05); font-size: 1.1rem;
    }

    /* Metric Cards Customization */
    div[data-testid="metric-container"] {
        background-color: #ffffff; border: 1px solid #e2e8f0; padding: 15px; 
        border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.02); 
        border-top: 4px solid #3b82f6;
    }

    /* Primary Buttons */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: white; font-weight: 700; border-radius: 8px; border: none;
        padding: 0.6rem 0; box-shadow: 0 4px 10px rgba(37, 99, 235, 0.2);
        transition: all 0.3s;
    }
    div.stButton > button[kind="primary"]:hover {
        transform: translateY(-2px); box-shadow: 0 6px 15px rgba(37, 99, 235, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# --- 3. BACKEND LOGIC (UNTOUCHED) ---
NEW_TASK_ORDER = ["Muhammad Imran", "Mazhar Abbas", "Muhammad Ahmad"]
REVISION_ORDER = ["Muhammad Ahmad", "Mazhar Abbas", "Muhammad Imran"]

conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    req = ["Task / File", "Type", "Assigned To", "Time", "Work Category", "Amount", "Payment Status", "Priority"]
    try:
        df = conn.read(ttl=0)
        for col in req:
            if col not in df.columns: df[col] = "" if col != "Amount" else 0
        df['Type'] = df['Type'].astype(str).str.strip()
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
        return df[req].dropna(how="all")
    except: 
        return pd.DataFrame(columns=req)

df = get_data()

# Auto-Assign Calculation
new_idx = len(df[df["Type"] == "New Task"]) % 3
rev_idx = len(df[df["Type"] == "Revision"]) % 3
current_writer_new = NEW_TASK_ORDER[new_idx]
current_writer_rev = REVISION_ORDER[rev_idx]

# --- 4. SIDEBAR NAVIGATION & WIDGETS ---
with st.sidebar:
    st.markdown("<h2 style='color: #1e3a8a; font-weight: 800;'>WriteWise Pro ⚡</h2>", unsafe_allow_html=True)
    st.caption("Agency Management CRM v3.0")
    st.write("---")
    
    # Universal Pending Widget in Sidebar
    if not df.empty:
        pending = df[df['Payment Status'] == 'Pending']['Amount'].sum()
        st.markdown(f"""
        <div class="money-card">
            <div class="money-label">Pending Payments</div>
            <div class="money-value">Rs {pending:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.write("---")
    page = st.radio("Main Menu", ["🚀 Task Assignment", "📊 Performance Analytics", "📂 Manage Database", "📅 Monthly Reports"])

# --- 5. MAIN PAGES ---

# ==========================================
# PAGE 1: TASK ASSIGNMENT
# ==========================================
if page == "🚀 Task Assignment":
    st.markdown("<h1 class='main-title'>Dispatch Console</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b; margin-bottom: 30px;'>Upload files and auto-assign tasks to the next available writer.</p>", unsafe_allow_html=True)

    c_form, c_info = st.columns([2, 1]) 

    with c_form:
        with st.container(border=True):
            st.markdown("### 📝 Create New Entry")
            mode = st.radio("Task Type", ["New Task", "Revision"], horizontal=True)
            st.write("")
            
            if mode == "New Task":
                st.markdown(f"""
                <div class="assign-box">
                    <span>🎯 NEXT IN LINE:</span> &nbsp; <u>{current_writer_new}</u>
                </div>
                """, unsafe_allow_html=True)
                
                u_file = st.file_uploader("Upload Client File", key="n_file")
                col1, col2 = st.columns(2)
                cat = col1.selectbox("Work Category", ["Assignment", "Article", "Copywriting", "Other"], key="cat")
                priority = col2.select_slider("Priority Level", ["Normal", "High", "Urgent"], value="Normal")
                
                col3, col4 = st.columns(2)
                amount = col3.number_input("PKR Amount Charged", step=500, value=0)
                pay_status = col4.selectbox("Payment Status", ["Pending", "Received"], key="pay")
                
                st.write("")
                if st.button("Confirm & Assign Task", type="primary", use_container_width=True):
                    if u_file:
                        ts = datetime.now().strftime("%d-%b-%Y %H:%M")
                        new_row = pd.DataFrame([{
                            "Task / File": u_file.name, "Type": "New Task", "Assigned To": current_writer_new,
                            "Time": ts, "Work Category": cat, "Amount": amount, 
                            "Payment Status": pay_status, "Priority": priority
                        }])
                        conn.update(data=pd.concat([df, new_row], ignore_index=True))
                        st.cache_data.clear()
                        st.success(f"✅ Task successfully assigned to {current_writer_new}!")
                        st.rerun()
                    else:
                        st.error("⚠️ Please upload a file to proceed.")
            
            else: # Revision
                st.markdown(f"""
                <div class="rev-box">
                    <span>⚠️ REVISION FOR:</span> &nbsp; <u>{current_writer_rev}</u>
                </div>
                """, unsafe_allow_html=True)
                
                r_file = st.file_uploader("Upload Revision File", key="r_file")
                st.info("💡 Note: Revisions are marked as non-billable (Amount = 0).")
                
                st.write("")
                if st.button("Send Revision to Writer", type="primary", use_container_width=True):
                    if r_file:
                        ts = datetime.now().strftime("%d-%b-%Y %H:%M")
                        new_row = pd.DataFrame([{
                            "Task / File": r_file.name, "Type": "Revision", "Assigned To": current_writer_rev,
                            "Time": ts, "Work Category": "Revision", "Amount": 0, 
                            "Payment Status": "N/A", "Priority": "High"
                        }])
                        conn.update(data=pd.concat([df, new_row], ignore_index=True))
                        st.cache_data.clear()
                        st.success(f"✅ Revision sent to {current_writer_rev}!")
                        st.rerun()
                    else:
                        st.error("⚠️ Please upload the revision file.")

    # Quick Info Sidebar Panel
    with c_info:
        st.markdown("#### 💡 Rotation Rules")
        with st.container(border=True):
            st.markdown("**New Tasks:**<br>1️⃣ Imran<br>2️⃣ Mazhar<br>3️⃣ Ahmad", unsafe_allow_html=True)
            st.divider()
            st.markdown("**Revisions:**<br>1️⃣ Ahmad<br>2️⃣ Mazhar<br>3️⃣ Imran", unsafe_allow_html=True)
            st.caption("System automatically routes to the correct writer based on queue.")

# ==========================================
# PAGE 2: PERFORMANCE ANALYTICS
# ==========================================
elif page == "📊 Performance Analytics":
    st.markdown("<h1 class='main-title'>Agency Analytics</h1>", unsafe_allow_html=True)
    st.write("")
    
    if not df.empty:
        # ALTAIR BAR CHART (Professional Look)
        chart_data = df.groupby(['Assigned To', 'Type']).size().reset_index(name='Count')
        chart = alt.Chart(chart_data).mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5).encode(
            x=alt.X('Assigned To', axis=alt.Axis(labelAngle=0, title="Writers")),
            y=alt.Y('Count', title="Total Tasks"),
            color=alt.Color('Type', scale=alt.Scale(domain=['New Task', 'Revision'], range=['#3b82f6', '#f97316'])),
            tooltip=['Assigned To', 'Type', 'Count']
        ).properties(height=350).configure_axis(grid=False).configure_view(strokeWidth=0)
        
        with st.container(border=True):
            st.altair_chart(chart, use_container_width=True)
        
        st.markdown("### 👨‍💻 Writer Breakdown")
        c_d1, c_d2, c_d3 = st.columns(3)
        cols = [c_d1, c_d2, c_d3]
        
        for i, writer in enumerate(NEW_TASK_ORDER):
            n_count = len(df[(df['Assigned To'] == writer) & (df['Type'] == 'New Task')])
            r_count = len(df[(df['Assigned To'] == writer) & (df['Type'] == 'Revision')])
            total_rev = df[(df['Assigned To'] == writer)]['Amount'].sum()
            
            with cols[i]:
                st.markdown(f"""
                <div style="background: white; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px rgba(0,0,0,0.02);">
                    <h4 style="margin:0; color:#1e3a8a; font-weight:800;">{writer}</h4>
                    <hr style="margin:10px 0; border-top:1px solid #f1f5f9;">
                    <div style="display:flex; justify-content:space-between; margin-bottom: 5px;">
                        <span style="color:#64748b;">Fresh Tasks:</span> <b style="color:#3b82f6;">{n_count}</b>
                    </div>
                    <div style="display:flex; justify-content:space-between; margin-bottom: 5px;">
                        <span style="color:#64748b;">Revisions:</span> <b style="color:#f97316;">{r_count}</b>
                    </div>
                    <div style="display:flex; justify-content:space-between; margin-top: 10px; padding-top: 10px; border-top: 1px dashed #e2e8f0;">
                        <span style="color:#0f172a; font-weight: 700;">Revenue Gen:</span> <b style="color:#10b981;">Rs {total_rev:,.0f}</b>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No data available for analytics yet.")
        
    st.write("")
    if st.button("🔄 Refresh Database"):
        st.cache_data.clear()
        st.rerun()

# ==========================================
# PAGE 3: MANAGE DATABASE
# ==========================================
elif page == "📂 Manage Database":
    st.markdown("<h1 class='main-title'>Database Records</h1>", unsafe_allow_html=True)
    st.write("")

    c_s, c_b = st.columns([3, 1])
    search = c_s.text_input("🔍 Search Records", placeholder="Enter filename or writer name...")

    if not df.empty:
        view_df = df.iloc[::-1].copy()
        if search:
            view_df = view_df[
                view_df['Task / File'].str.contains(search, case=False, na=False) | 
                view_df['Assigned To'].str.contains(search, case=False, na=False)
            ]
        
        st.dataframe(
            view_df, height=350, use_container_width=True, hide_index=True,
            column_order=["Time", "Task / File", "Type", "Assigned To", "Amount", "Payment Status"],
            column_config={
                "Amount": st.column_config.NumberColumn("PKR", format="Rs %d"),
                "Payment Status": st.column_config.TextColumn("Status")
            }
        )
        
        st.write("---")
        # EDIT / DELETE PANEL
        with st.container(border=True):
            st.markdown("#### 🛠️ Modification Panel")
            all_tasks = df.iloc[::-1]
            t_map = {f"{r['Task / File']} ({r['Assigned To']} - {r['Type']})": i for i, r in all_tasks.iterrows()}
            sel_task = st.selectbox("Select a Record to Edit/Delete", list(t_map.keys()))
            idx = t_map[sel_task]
            
            ec1, ec2 = st.columns(2)
            e_amt = ec1.number_input("Edit PKR Amount", value=int(df.at[idx, "Amount"]), step=500)
            
            cur_stat = df.at[idx, "Payment Status"]
            opts = ["Pending", "Received", "N/A"]
            s_idx = opts.index(cur_stat) if cur_stat in opts else 0
            e_stat = ec2.selectbox("Edit Payment Status", opts, index=s_idx)
            
            if st.button("💾 Save Changes", type="primary"):
                df.at[idx, "Amount"] = e_amt
                df.at[idx, "Payment Status"] = e_stat
                conn.update(data=df)
                st.cache_data.clear()
                st.success("✅ Record updated successfully.")
                st.rerun()
                
            st.divider()
            with st.form("del_form"):
                st.markdown("<span style='color: #ef4444; font-weight: bold;'>⚠️ Danger Zone: Delete Record</span>", unsafe_allow_html=True)
                col_p, col_btn = st.columns([3, 1])
                d_pass = col_p.text_input("Enter Admin Password to Delete", type="password", placeholder="Password is 1234")
                
                if col_btn.form_submit_button("Delete Permanently"):
                    if d_pass == "1234":
                        df = df.drop(idx)
                        conn.update(data=df)
                        st.cache_data.clear()
                        st.success("✅ Deleted successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Incorrect Password")
    else:
        st.info("Database is empty.")

# ==========================================
# PAGE 4: MONTHLY REPORTS (NEW FEATURE!)
# ==========================================
elif page == "📅 Monthly Reports":
    st.markdown("<h1 class='main-title'>Monthly Financial & Work Report</h1>", unsafe_allow_html=True)
    st.write("")

    if df.empty:
        st.warning("No data available to generate reports.")
    else:
        # Convert Time column to datetime objects
        # Safely parse the custom date format "%d-%b-%Y %H:%M"
        df['ParsedTime'] = pd.to_datetime(df['Time'], format="%d-%b-%Y %H:%M", errors='coerce')
        
        col1, col2 = st.columns(2)
        with col1:
            years = df['ParsedTime'].dt.year.dropna().unique()
            if len(years) > 0:
                selected_year = st.selectbox("Select Year", sorted([int(y) for y in years], reverse=True))
            else:
                selected_year = datetime.now().year
                st.selectbox("Select Year", [selected_year])
        with col2:
            month_names = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
            selected_month_name = st.selectbox("Select Month", month_names, index=datetime.now().month - 1)
            selected_month_num = month_names.index(selected_month_name) + 1

        if st.button("📊 Generate Report", type="primary"):
            # Filter Data
            mask = (df['ParsedTime'].dt.year == selected_year) & (df['ParsedTime'].dt.month == selected_month_num)
            report_df = df[mask]
            
            st.write("---")
            st.markdown(f"### 📋 Report Summary for {selected_month_name} {selected_year}")
            
            if report_df.empty:
                st.info(f"No tasks were recorded in {selected_month_name} {selected_year}.")
            else:
                # Calculations
                new_tasks = len(report_df[report_df["Type"] == "New Task"])
                rev_tasks = len(report_df[report_df["Type"] == "Revision"])
                total_rev = report_df["Amount"].sum()
                pending_rev = report_df[report_df["Payment Status"] == "Pending"]["Amount"].sum()
                received_rev = report_df[report_df["Payment Status"] == "Received"]["Amount"].sum()

                # Visuals
                r1, r2, r3, r4 = st.columns(4)
                r1.metric("Fresh Tasks", new_tasks)
                r2.metric("Revisions", rev_tasks)
                r3.metric("Total Revenue Billed", f"Rs {total_rev:,.0f}")
                r4.metric("Payments Received", f"Rs {received_rev:,.0f}", delta=f"Pending: Rs {pending_rev:,.0f}", delta_color="inverse")
                
                st.write("")
                st.markdown("#### Detailed Data Log")
                # Drop the parsed time column before displaying
                display_df = report_df.drop(columns=['ParsedTime'])
                st.dataframe(display_df, use_container_width=True, hide_index=True)
                
                # Download Button
                csv = display_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label=f"📥 Download {selected_month_name} Report (CSV)",
                    data=csv,
                    file_name=f"WriteWise_Report_{selected_month_name}_{selected_year}.csv",
                    mime="text/csv"
                )

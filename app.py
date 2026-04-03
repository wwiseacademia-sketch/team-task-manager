import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="WriteWise CRM", 
    layout="wide", 
    page_icon="⚡",
    initial_sidebar_state="expanded"
)

# --- 2. ULTRA-PREMIUM MODERN CSS & FONTAWESOME ICONS ---
st.markdown("""
<style>
    /* Import Modern Font & FontAwesome Vector Icons */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');

    /* General Body */
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
        background-color: #f4f7fb;
        color: #0f172a;
    }

    /* Vector Icon Styling */
    .pro-icon {
        margin-right: 12px;
        color: #2563eb;
    }
    .text-gradient {
        background: -webkit-linear-gradient(45deg, #2563eb, #9333ea);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Gradient Main Titles */
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 5px;
        letter-spacing: -1px;
        color: #0f172a;
    }

    /* Hover "Bubble Up" Effect for Native Metrics */
    div[data-testid="metric-container"] {
        background-color: #ffffff; 
        border: 1px solid #e2e8f0; 
        padding: 20px; 
        border-radius: 12px; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.02); 
        border-bottom: 3px solid #3b82f6;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-6px);
        box-shadow: 0 15px 25px rgba(59, 130, 246, 0.12);
        border-bottom: 3px solid #9333ea;
    }

    /* Custom Glass/Modern Cards */
    .modern-card {
        background: white; 
        padding: 25px; 
        border-radius: 16px; 
        border: 1px solid #e2e8f0; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.02);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .modern-card:hover {
        transform: translateY(-6px);
        box-shadow: 0 15px 30px rgba(0,0,0,0.06);
    }

    /* Pending Payments Widget (Sidebar) with Pulse */
    .money-card {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: white; border-radius: 14px; padding: 25px;
        box-shadow: 0 10px 20px rgba(15, 23, 42, 0.15);
        text-align: center; position: relative;
        transition: transform 0.3s ease;
    }
    .money-card:hover { transform: scale(1.02); }
    
    .pulse-dot {
        height: 10px; width: 10px; background-color: #ef4444;
        border-radius: 50%; display: inline-block;
        box-shadow: 0 0 0 0 rgba(239, 68, 68, 1);
        animation: pulse-red 2s infinite; margin-right: 8px;
    }
    @keyframes pulse-red {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
    }
    .money-label { font-size: 0.85rem; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px;}
    .money-value { font-size: 2.2rem; font-weight: 800; margin-top: 5px; color: #facc15; }

    /* Assignment Badges */
    .assign-box {
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        border-left: 4px solid #2563eb; padding: 20px; border-radius: 10px; 
        color: #1e3a8a; font-weight: 700; margin-bottom: 20px; font-size: 1.1rem;
        transition: all 0.3s ease;
    }
    .assign-box:hover { transform: translateX(4px); box-shadow: 0 5px 15px rgba(37,99,235,0.1); }
    
    .rev-box {
        background: linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%);
        border-left: 4px solid #ea580c; padding: 20px; border-radius: 10px; 
        color: #9a3412; font-weight: 700; margin-bottom: 20px; font-size: 1.1rem;
        transition: all 0.3s ease;
    }
    .rev-box:hover { transform: translateX(4px); box-shadow: 0 5px 15px rgba(234,88,12,0.1); }

    /* Primary Buttons (Bubble Up) */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #2563eb 0%, #7e22ce 100%);
        color: white; font-weight: 600; border-radius: 8px; border: none;
        padding: 0.6rem 0; box-shadow: 0 4px 10px rgba(37, 99, 235, 0.2);
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    div.stButton > button[kind="primary"]:hover {
        transform: translateY(-4px); box-shadow: 0 8px 20px rgba(126, 34, 206, 0.3);
    }
    
    /* Dataframe Header styling */
    .col-header {
        font-size: 1.2rem; font-weight: 700; color: #1e293b; 
        margin-bottom: 15px; padding-bottom: 10px; border-bottom: 2px dashed #cbd5e1;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. DYNAMIC GREETING LOGIC ---
current_hour = datetime.now().hour
if current_hour < 12: greeting = "<i class='fa-regular fa-sun'></i> Good Morning"
elif 12 <= current_hour < 18: greeting = "<i class='fa-solid fa-cloud-sun'></i> Good Afternoon"
else: greeting = "<i class='fa-regular fa-moon'></i> Good Evening"

# --- 4. BACKEND LOGIC (UNTOUCHED) ---
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

# --- 5. SIDEBAR NAVIGATION & WIDGETS ---
with st.sidebar:
    st.markdown("<h2 style='color: #1e3a8a; font-weight: 800;'><i class='fa-solid fa-bolt text-gradient'></i> WriteWise Pro</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: #64748b; font-weight: 500; font-size: 1.1rem;'>{greeting}, Admin</p>", unsafe_allow_html=True)
    st.write("---")
    
    # Pulsing Pending Widget
    if not df.empty:
        pending = df[df['Payment Status'] == 'Pending']['Amount'].sum()
        st.markdown(f"""
        <div class="money-card">
            <div class="money-label"><span class="pulse-dot"></span> <i class="fa-solid fa-wallet"></i> Pending Dues</div>
            <div class="money-value">Rs {pending:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.write("---")
    # Using sleek geometric unicode for native Streamlit widget
    page = st.radio("Main Menu", ["✦ Task Assignment", "✦ Performance Analytics", "✦ Monthly Reports", "✦ Manage Database"])

# --- 6. MAIN PAGES ---

# ==========================================
# PAGE 1: TASK ASSIGNMENT
# ==========================================
if page == "✦ Task Assignment":
    st.markdown("<h1 class='main-title'><i class='fa-solid fa-paper-plane pro-icon text-gradient'></i> Dispatch Console</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b; margin-bottom: 30px; font-size: 1.1rem;'>Smart routing system for seamless task distribution.</p>", unsafe_allow_html=True)

    c_form, c_info = st.columns([2.5, 1]) 

    with c_form:
        with st.container(border=True):
            st.markdown("### <i class='fa-solid fa-file-signature' style='color:#3b82f6; margin-right:8px;'></i> Create New Entry", unsafe_allow_html=True)
            mode = st.radio("Task Type", ["New Task", "Revision"], horizontal=True, label_visibility="collapsed")
            st.write("")
            
            if mode == "New Task":
                st.markdown(f"""
                <div class="assign-box">
                    <span style="color:#64748b; font-size:0.85rem; text-transform:uppercase;"><i class="fa-solid fa-user-check"></i> Next Writer in Queue</span><br>
                    <span style="font-weight: 800; font-size: 1.3rem;">{current_writer_new}</span>
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
                if st.button("✓ Confirm & Assign Task", type="primary", use_container_width=True):
                    if u_file:
                        ts = datetime.now().strftime("%d-%b-%Y %H:%M")
                        new_row = pd.DataFrame([{
                            "Task / File": u_file.name, "Type": "New Task", "Assigned To": current_writer_new,
                            "Time": ts, "Work Category": cat, "Amount": amount, 
                            "Payment Status": pay_status, "Priority": priority
                        }])
                        conn.update(data=pd.concat([df, new_row], ignore_index=True))
                        st.cache_data.clear()
                        st.success(f"Task successfully assigned to {current_writer_new}!")
                        st.rerun()
                    else:
                        st.error("Please upload a file to proceed.")
            
            else: # Revision
                st.markdown(f"""
                <div class="rev-box">
                    <span style="color:#ea580c; font-size:0.85rem; text-transform:uppercase;"><i class="fa-solid fa-rotate-left"></i> Revision Routing To</span><br>
                    <span style="font-weight: 800; font-size: 1.3rem;">{current_writer_rev}</span>
                </div>
                """, unsafe_allow_html=True)
                
                r_file = st.file_uploader("Upload Revision File", key="r_file")
                st.info("Note: Revisions are automatically marked as non-billable.")
                
                st.write("")
                if st.button("↻ Send Revision", type="primary", use_container_width=True):
                    if r_file:
                        ts = datetime.now().strftime("%d-%b-%Y %H:%M")
                        new_row = pd.DataFrame([{
                            "Task / File": r_file.name, "Type": "Revision", "Assigned To": current_writer_rev,
                            "Time": ts, "Work Category": "Revision", "Amount": 0, 
                            "Payment Status": "N/A", "Priority": "High"
                        }])
                        conn.update(data=pd.concat([df, new_row], ignore_index=True))
                        st.cache_data.clear()
                        st.success(f"Revision sent to {current_writer_rev}!")
                        st.rerun()
                    else:
                        st.error("Please upload the revision file.")

    with c_info:
        st.markdown("#### <i class='fa-solid fa-network-wired' style='color:#64748b; margin-right:8px;'></i> System Rules", unsafe_allow_html=True)
        st.markdown("""
        <div class='modern-card' style='padding: 20px;'>
            <div style='color: #2563eb; font-weight: 700; margin-bottom: 10px;'><i class='fa-solid fa-arrow-down-1-9'></i> Fresh Sequence</div>
            <div style='color: #475569; font-weight: 400; line-height: 1.8;'>
                1. Muhammad Imran<br>2. Mazhar Abbas<br>3. Muhammad Ahmad
            </div>
            <hr style='border-color: #e2e8f0; margin: 15px 0;'>
            <div style='color: #ea580c; font-weight: 700; margin-bottom: 10px;'><i class='fa-solid fa-arrow-down-1-9'></i> Revision Sequence</div>
            <div style='color: #475569; font-weight: 400; line-height: 1.8;'>
                1. Muhammad Ahmad<br>2. Mazhar Abbas<br>3. Muhammad Imran
            </div>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# PAGE 2: PERFORMANCE ANALYTICS
# ==========================================
elif page == "✦ Performance Analytics":
    st.markdown("<h1 class='main-title'><i class='fa-solid fa-chart-pie pro-icon text-gradient'></i> Agency Analytics</h1>", unsafe_allow_html=True)
    st.write("")
    
    if not df.empty:
        chart_data = df.groupby(['Assigned To', 'Type']).size().reset_index(name='Count')
        chart = alt.Chart(chart_data).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
            x=alt.X('Assigned To', axis=alt.Axis(labelAngle=0, title="Writers")),
            y=alt.Y('Count', title="Total Tasks"),
            color=alt.Color('Type', scale=alt.Scale(domain=['New Task', 'Revision'], range=['#2563eb', '#f97316'])),
            tooltip=['Assigned To', 'Type', 'Count']
        ).properties(height=350).configure_axis(grid=False, labelFontSize=12).configure_view(strokeWidth=0)
        
        with st.container(border=True):
            st.altair_chart(chart, use_container_width=True)
        
        st.markdown("<h3 style='margin-top: 30px; margin-bottom: 20px;'><i class='fa-solid fa-users-viewfinder' style='color:#3b82f6; margin-right:8px;'></i> Writer Breakdown</h3>", unsafe_allow_html=True)
        c_d1, c_d2, c_d3 = st.columns(3)
        cols = [c_d1, c_d2, c_d3]
        
        for i, writer in enumerate(NEW_TASK_ORDER):
            n_count = len(df[(df['Assigned To'] == writer) & (df['Type'] == 'New Task')])
            r_count = len(df[(df['Assigned To'] == writer) & (df['Type'] == 'Revision')])
            total_rev = df[(df['Assigned To'] == writer)]['Amount'].sum()
            
            with cols[i]:
                st.markdown(f"""
                <div class="modern-card">
                    <h4 style="margin:0; color:#0f172a; font-weight:800; font-size: 1.2rem;">{writer}</h4>
                    <hr style="margin:15px 0; border-top:1px solid #f1f5f9;">
                    <div style="display:flex; justify-content:space-between; margin-bottom: 8px; font-size: 1.05rem;">
                        <span style="color:#64748b;">Fresh Tasks</span> <b style="color:#2563eb;">{n_count}</b>
                    </div>
                    <div style="display:flex; justify-content:space-between; margin-bottom: 8px; font-size: 1.05rem;">
                        <span style="color:#64748b;">Revisions</span> <b style="color:#ea580c;">{r_count}</b>
                    </div>
                    <div style="display:flex; justify-content:space-between; margin-top: 15px; padding-top: 15px; border-top: 1px dashed #e2e8f0; font-size: 1.05rem;">
                        <span style="color:#0f172a; font-weight: 700;">Revenue</span> <b style="color:#10b981;">Rs {total_rev:,.0f}</b>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No data available for analytics yet.")

# ==========================================
# PAGE 3: MONTHLY REPORTS 
# ==========================================
elif page == "✦ Monthly Reports":
    st.markdown("<h1 class='main-title'><i class='fa-solid fa-file-invoice-dollar pro-icon text-gradient'></i> Financial Reports</h1>", unsafe_allow_html=True)
    st.write("")

    if df.empty:
        st.warning("No data available to generate reports.")
    else:
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

        if st.button("✓ Generate Report", type="primary"):
            mask = (df['ParsedTime'].dt.year == selected_year) & (df['ParsedTime'].dt.month == selected_month_num)
            report_df = df[mask]
            
            st.write("---")
            
            if report_df.empty:
                st.info(f"No tasks were recorded in {selected_month_name} {selected_year}.")
            else:
                new_tasks = len(report_df[report_df["Type"] == "New Task"])
                rev_tasks = len(report_df[report_df["Type"] == "Revision"])
                total_rev = report_df["Amount"].sum()
                received_rev = report_df[report_df["Payment Status"] == "Received"]["Amount"].sum()

                # Native Streamlit metrics (We rely on our custom CSS to style these nicely)
                r1, r2, r3, r4 = st.columns(4)
                r1.metric("Fresh Tasks", new_tasks)
                r2.metric("Revisions", rev_tasks)
                r3.metric("Total Billed", f"Rs {total_rev:,.0f}")
                r4.metric("Amount Received", f"Rs {received_rev:,.0f}")
                
                st.write("")
                st.markdown("<br>", unsafe_allow_html=True)
                c_new, c_rev = st.columns(2)
                
                with c_new:
                    st.markdown("<div class='col-header'><i class='fa-solid fa-file-circle-plus' style='color:#2563eb; margin-right:8px;'></i> Fresh Tasks Log</div>", unsafe_allow_html=True)
                    new_df = report_df[report_df["Type"] == "New Task"].drop(columns=['ParsedTime', 'Type', 'Work Category', 'Priority'])
                    if not new_df.empty:
                        st.dataframe(new_df, use_container_width=True, hide_index=True)
                    else:
                        st.write("No new tasks this month.")

                with c_rev:
                    st.markdown("<div class='col-header'><i class='fa-solid fa-wrench' style='color:#ea580c; margin-right:8px;'></i> Revisions Log</div>", unsafe_allow_html=True)
                    rev_df = report_df[report_df["Type"] == "Revision"][['Time', 'Task / File', 'Assigned To']]
                    if not rev_df.empty:
                        st.dataframe(rev_df, use_container_width=True, hide_index=True)
                    else:
                        st.write("No revisions this month. Great job!")
                
                st.write("---")
                csv = report_df.drop(columns=['ParsedTime']).to_csv(index=False).encode('utf-8')
                st.download_button(
                    label=f"⤓ Download Full CSV",
                    data=csv,
                    file_name=f"WriteWise_Report_{selected_month_name}_{selected_year}.csv",
                    mime="text/csv"
                )

# ==========================================
# PAGE 4: MANAGE DATABASE
# ==========================================
elif page == "✦ Manage Database":
    st.markdown("<h1 class='main-title'><i class='fa-solid fa-database pro-icon text-gradient'></i> Database Records</h1>", unsafe_allow_html=True)
    st.write("")

    c_s, c_b = st.columns([3, 1])
    search = c_s.text_input("Search Records", placeholder="Search by filename or writer name...")

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
        with st.container(border=True):
            st.markdown("#### <i class='fa-solid fa-sliders' style='color:#64748b; margin-right:8px;'></i> Modification Panel", unsafe_allow_html=True)
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
            
            if st.button("✓ Save Changes", type="primary"):
                df.at[idx, "Amount"] = e_amt
                df.at[idx, "Payment Status"] = e_stat
                conn.update(data=df)
                st.cache_data.clear()
                st.success("Record updated successfully.")
                st.rerun()
                
            st.divider()
            with st.form("del_form"):
                st.markdown("<span style='color: #ef4444; font-weight: 600;'><i class='fa-solid fa-triangle-exclamation'></i> Danger Zone: Delete Record</span>", unsafe_allow_html=True)
                col_p, col_btn = st.columns([3, 1])
                d_pass = col_p.text_input("Enter Admin Password to Delete", type="password", placeholder="Password is 1234")
                
                if col_btn.form_submit_button("Delete Permanently"):
                    if d_pass == "1234":
                        df = df.drop(idx)
                        conn.update(data=df)
                        st.cache_data.clear()
                        st.success("Deleted successfully!")
                        st.rerun()
                    else:
                        st.error("Incorrect Password")
    else:
        st.info("Database is empty.")

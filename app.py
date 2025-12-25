import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="Write Wise Ultimate", layout="wide", page_icon="🚀")

# --- 2. ULTIMATE BLOCK CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #f1f5f9; color: #0f172a; }
    
    .block-container { padding-top: 2rem; padding-bottom: 5rem; }

    /* BLOCK CARDS */
    .dashboard-block {
        background: white; border-radius: 16px; padding: 25px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        margin-bottom: 24px; border: 1px solid #e2e8f0;
        transition: transform 0.2s;
    }
    .dashboard-block:hover { transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); }

    /* COLOR THEMES */
    .theme-blue { border-top: 5px solid #3b82f6; }   /* New Task */
    .theme-orange { border-top: 5px solid #f97316; } /* Revision */
    .theme-green { border-top: 5px solid #22c55e; }  /* Finance */
    .theme-dark { border-top: 5px solid #334155; background: #1e293b; color: white; } /* Data */

    /* HEADERS */
    .blk-header { font-size: 1.25rem; font-weight: 800; margin-bottom: 20px; display: flex; align-items: center; gap: 10px; }
    .txt-blue { color: #1d4ed8; } .txt-orange { color: #c2410c; } .txt-green { color: #15803d; } .txt-white { color: white; }

    /* ASSIGNEE BADGE */
    .assign-badge {
        background: #f8fafc; border: 1px dashed #94a3b8; padding: 10px;
        border-radius: 8px; text-align: center; font-weight: 700; color: #475569;
        margin: 15px 0;
    }

    /* BUTTONS */
    div.stButton > button { width: 100%; border-radius: 8px; font-weight: 600; padding: 12px; }
    
    /* REMOVE WATERMARKS */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 3. DATA & LOGIC ---
NEW_TASK_ORDER = ["Muhammad Imran", "Mazhar Abbas", "Muhammad Ahmad"]
REVISION_ORDER = ["Muhammad Ahmad", "Mazhar Abbas", "Muhammad Imran"]

conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    # Added 'Priority' to required columns
    req = ["Task / File", "Type", "Assigned To", "Time", "Work Category", "Amount", "Payment Status", "Priority"]
    try:
        df = conn.read(ttl=0)
        for col in req:
            if col not in df.columns: df[col] = "" if col != "Amount" else 0
        
        # CLEANING
        df['Type'] = df['Type'].astype(str).str.strip()
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
        
        return df.dropna(how="all")
    except: return pd.DataFrame(columns=req)

df = get_data()

new_idx = len(df[df["Type"] == "New Task"]) % 3
rev_idx = len(df[df["Type"] == "Revision"]) % 3

# --- 4. SIDEBAR ANALYTICS ---
with st.sidebar:
    st.header("📊 Analytics")
    
    if not df.empty:
        # Chart 1: Workload
        st.caption("Tasks per Member")
        chart_data = df['Assigned To'].value_counts().reset_index()
        chart_data.columns = ['Member', 'Count']
        
        c1 = alt.Chart(chart_data).mark_arc(innerRadius=40).encode(
            theta="Count", color=alt.Color("Member", legend=None), tooltip=["Member", "Count"]
        ).properties(height=200)
        st.altair_chart(c1, use_container_width=True)
        
        # Metrics
        st.divider()
        pending = df[df['Payment Status'] == 'Pending']['Amount'].sum()
        received = df[df['Payment Status'] == 'Received']['Amount'].sum()
        
        c_a, c_b = st.columns(2)
        c_a.metric("Received", f"{received/1000:.1f}k")
        c_b.metric("Pending", f"{pending/1000:.1f}k", delta_color="inverse")
        
    st.write("")
    if st.button("🔄 Refresh Data", type="secondary"): st.rerun()

# --- 5. MAIN DASHBOARD ---
st.markdown("""
<div style="margin-bottom:30px;">
    <h1 style="margin:0; font-size:2.2rem;">Write Wise <span style="color:#3b82f6">Ultimate</span></h1>
    <div style="color:#64748b; font-size:1rem;">Task Distribution & Financial Command Center</div>
</div>
""", unsafe_allow_html=True)

# === ROW 1: ASSIGNMENT BLOCKS ===
col1, col2 = st.columns(2)

# [BLOCK 1] NEW TASK (BLUE)
with col1:
    st.markdown("""<div class="dashboard-block theme-blue"><div class="blk-header txt-blue">🚀 New Assignment</div></div>""", unsafe_allow_html=True)
    with st.container():
        u_file = st.file_uploader("Upload New File", key="n_file")
        
        c1a, c1b = st.columns(2)
        cat = c1a.selectbox("Category", ["Assignment", "Article"], key="cat")
        # 🔥 PRIORITY FEATURE
        is_urgent = c1b.checkbox("🔥 High Priority?")
        
        c2a, c2b = st.columns(2)
        pay = c2a.selectbox("Payment", ["Pending", "Received"], key="pay")
        amt = c2b.number_input("Amount (PKR)", step=100, value=0, key="amt")
        
        nxt = NEW_TASK_ORDER[new_idx]
        st.markdown(f'<div class="assign-badge">Assigning To: {nxt}</div>', unsafe_allow_html=True)
        
        if st.button("Confirm & Assign", type="primary"):
            if u_file:
                ts = datetime.now().strftime("%d-%b-%Y %H:%M")
                prio = "High" if is_urgent else "Normal"
                new_row = pd.DataFrame([{
                    "Task / File": u_file.name, "Type": "New Task", "Assigned To": nxt,
                    "Time": ts, "Work Category": cat, "Amount": amt, "Payment Status": pay, "Priority": prio
                }])
                conn.update(data=pd.concat([df, new_row], ignore_index=True))
                st.toast("Task Assigned!", icon="✅")
                st.rerun()
            else: st.error("No file uploaded.")

# [BLOCK 2] REVISION (ORANGE)
with col2:
    st.markdown("""<div class="dashboard-block theme-orange"><div class="blk-header txt-orange">↺ Revision Hub</div></div>""", unsafe_allow_html=True)
    with st.container():
        r_file = st.file_uploader("Upload Revision", key="r_file")
        st.info("ℹ️ Revisions are free of cost. Priority is standard.")
        
        nxt_rev = REVISION_ORDER[rev_idx]
        st.markdown(f'<div class="assign-badge">Revision For: {nxt_rev}</div>', unsafe_allow_html=True)
        
        if st.button("Assign Revision"):
            if r_file:
                ts = datetime.now().strftime("%d-%b-%Y %H:%M")
                new_row = pd.DataFrame([{
                    "Task / File": r_file.name, "Type": "Revision", "Assigned To": nxt_rev,
                    "Time": ts, "Work Category": "Revision", "Amount": 0, "Payment Status": "N/A", "Priority": "Normal"
                }])
                conn.update(data=pd.concat([df, new_row], ignore_index=True))
                st.toast("Revision Sent!", icon="🟠")
                st.rerun()
            else: st.error("No file uploaded.")

# === ROW 2: MANAGEMENT & DATA ===
col3, col4 = st.columns([1, 1.5])

# [BLOCK 3] FINANCE & DELETE (GREEN)
with col3:
    st.markdown("""<div class="dashboard-block theme-green"><div class="blk-header txt-green">⚙️ Task Manager</div></div>""", unsafe_allow_html=True)
    with st.container():
        if not df.empty:
            # STRICT FILTER: ONLY NEW TASKS
            billable = df[df["Type"] == "New Task"].iloc[::-1]
            if not billable.empty:
                t_map = {f"{r['Task / File']} ({r['Assigned To']})": i for i, r in billable.iterrows()}
                sel = st.selectbox("Select Task", list(t_map.keys()))
                idx = t_map[sel]
                
                # Using Tabs for cleaner UI
                tab_pay, tab_del = st.tabs(["💰 Update Payment", "🗑️ Delete Task"])
                
                with tab_pay:
                    st.write("")
                    n_amt = st.number_input("Amount", value=int(df.at[idx, "Amount"]), key="e_amt")
                    n_st = st.selectbox("Status", ["Pending", "Received"], index=0 if df.at[idx, "Payment Status"]=="Pending" else 1, key="e_st")
                    if st.button("Update Info"):
                        df.at[idx, "Amount"] = n_amt
                        df.at[idx, "Payment Status"] = n_st
                        conn.update(data=df)
                        st.success("Updated!")
                        st.rerun()

                with tab_del:
                    st.write("")
                    st.error("Danger Zone")
                    # SAFETY CHECKBOX
                    confirm = st.checkbox("I confirm I want to delete this task permanently.")
                    if st.button("Delete Task", type="secondary", disabled=not confirm):
                        df = df.drop(idx)
                        conn.update(data=df)
                        st.success("Task Deleted!")
                        st.rerun()
            else: st.warning("No billable tasks.")
        else: st.info("No data.")

# [BLOCK 4] SMART DATABASE (DARK)
with col4:
    st.markdown("""<div class="dashboard-block theme-dark"><div class="blk-header txt-white">📋 Smart Database</div></div>""", unsafe_allow_html=True)
    with st.container():
        # 🔍 SMART SEARCH & FILTER
        c_search, c_filter = st.columns([2, 1])
        search_term = c_search.text_input("🔍 Search File or Person", placeholder="Type to search...")
        filter_status = c_filter.multiselect("Filter Status", ["Pending", "Received"])
        
        if not df.empty:
            view_df = df.iloc[::-1].copy()
            
            # Apply Search
            if search_term:
                view_df = view_df[
                    view_df['Task / File'].str.contains(search_term, case=False) | 
                    view_df['Assigned To'].str.contains(search_term, case=False)
                ]
            
            # Apply Filter
            if filter_status:
                view_df = view_df[view_df['Payment Status'].isin(filter_status)]
            
            # Show Data with Priority Flag
            st.dataframe(
                view_df,
                height=400,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Priority": st.column_config.TextColumn("🔥", width="small"),
                    "Task / File": st.column_config.TextColumn("File Name", width="medium"),
                    "Type": st.column_config.TextColumn("Type", width="small"),
                    "Amount": st.column_config.NumberColumn("PKR", format="%d"),
                    "Payment Status": st.column_config.TextColumn("Status", width="small"),
                }
            )
        else: st.write("No records found.")

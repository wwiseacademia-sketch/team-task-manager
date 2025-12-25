import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Write Wise Ultimate", layout="wide", page_icon="🚀")

# --- 2. ULTIMATE CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #1e293b; }
    .stApp { background-color: #f8fafc; }

    /* CARDS */
    .block-card {
        background: white; border-radius: 12px; padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        border: 1px solid #e2e8f0; margin-bottom: 20px;
    }
    
    /* THEMES */
    .theme-blue { border-top: 5px solid #3b82f6; }
    .theme-orange { border-top: 5px solid #f97316; }
    .theme-green { border-top: 5px solid #10b981; }
    .theme-dark { border-top: 5px solid #334155; background: #1e293b; color: white; }

    /* HEADER TEXT */
    .card-header { font-size: 1.1rem; font-weight: 700; margin-bottom: 15px; display: flex; align-items: center; gap: 10px; }
    
    /* BADGES */
    .badge-urgent { background: #fee2e2; color: #dc2626; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: bold; border: 1px solid #fecaca; }
    .badge-normal { background: #f1f5f9; color: #64748b; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; }

    /* METRICS */
    .metric-container { display: flex; justify-content: space-between; text-align: center; }
    .metric-box { background: #f8fafc; padding: 10px; border-radius: 8px; width: 30%; }
    .metric-val { font-size: 1.2rem; font-weight: 700; color: #0f172a; }
    .metric-lbl { font-size: 0.7rem; color: #64748b; text-transform: uppercase; }

    /* HIDE DEFAULT */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 3. DATA & LOGIC ---
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
        return df.dropna(how="all")
    except: return pd.DataFrame(columns=req)

df = get_data()

new_idx = len(df[df["Type"] == "New Task"]) % 3
rev_idx = len(df[df["Type"] == "Revision"]) % 3

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("### 📊 Dashboard Controls")
    
    if not df.empty:
        # VISUAL ANALYTICS
        st.caption("WORK DISTRIBUTION")
        chart_data = df['Assigned To'].value_counts().reset_index()
        chart_data.columns = ['Member', 'Tasks']
        
        c = alt.Chart(chart_data).mark_arc(innerRadius=40).encode(
            theta=alt.Theta("Tasks", stack=True),
            color=alt.Color("Member", legend=None),
            tooltip=["Member", "Tasks"]
        )
        st.altair_chart(c, use_container_width=True)
        
        st.divider()
        st.caption("MONTHLY EARNINGS")
        pending = df[df['Payment Status'] == 'Pending']['Amount'].sum()
        received = df[df['Payment Status'] == 'Received']['Amount'].sum()
        
        col_a, col_b = st.columns(2)
        col_a.metric("Received", f"{received/1000:.1f}k")
        col_b.metric("Pending", f"{pending/1000:.1f}k", delta_color="inverse")

    st.write("")
    if st.button("🔄 Refresh Data", type="primary"): st.rerun()

# --- 5. MAIN LAYOUT ---

# Header Section
st.markdown("""
<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
    <div>
        <h1 style="margin:0; font-size:1.8rem;">Write Wise <span style="color:#3b82f6">Ultimate</span></h1>
        <p style="margin:0; color:#64748b; font-size:0.9rem;">Advanced Task Distribution System</p>
    </div>
    <div style="text-align:right;">
        <span style="background:#dbeafe; color:#1e40af; padding:5px 12px; border-radius:20px; font-weight:600; font-size:0.8rem;">● Live System</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.write("")

# --- ROW 1: TASK ENTRY ---
col1, col2 = st.columns(2)

# [BLOCK 1] NEW TASK
with col1:
    st.markdown('<div class="block-card theme-blue">', unsafe_allow_html=True)
    st.markdown('<div class="card-header">🚀 New Assignment</div>', unsafe_allow_html=True)
    
    u_file = st.file_uploader("Upload File", key="n_file")
    
    c1, c2 = st.columns(2)
    cat = c1.selectbox("Category", ["Assignment", "Article"], key="cat")
    is_urgent = c2.checkbox("🔥 High Priority?")
    
    cc1, cc2 = st.columns(2)
    pay_st = cc1.selectbox("Payment", ["Pending", "Received"], key="pay")
    amt = cc2.number_input("Amount", step=100, value=0, key="amt")
    
    nxt = NEW_TASK_ORDER[new_idx]
    
    st.markdown(f"""
    <div style="background:#eff6ff; padding:10px; border-radius:8px; margin:15px 0; display:flex; justify-content:space-between; align-items:center;">
        <span style="font-size:0.8rem; color:#64748b;">NEXT ASSIGNEE</span>
        <span style="font-weight:700; color:#1e3a8a; font-size:1.1rem;">{nxt}</span>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Confirm & Assign", type="primary"):
        if u_file:
            ts = datetime.now().strftime("%d-%b-%Y %H:%M")
            prio = "High" if is_urgent else "Normal"
            new_row = pd.DataFrame([{
                "Task / File": u_file.name, "Type": "New Task", "Assigned To": nxt,
                "Time": ts, "Work Category": cat, "Amount": amt, "Payment Status": pay_st, "Priority": prio
            }])
            conn.update(data=pd.concat([df, new_row], ignore_index=True))
            st.toast("Task Assigned!", icon="✅")
            st.rerun()
        else: st.error("No file uploaded.")
    st.markdown('</div>', unsafe_allow_html=True)

# [BLOCK 2] REVISION
with col2:
    st.markdown('<div class="block-card theme-orange">', unsafe_allow_html=True)
    st.markdown('<div class="card-header">↺ Revision Hub</div>', unsafe_allow_html=True)
    
    r_file = st.file_uploader("Upload Revision", key="r_file")
    st.caption("ℹ️ Revisions are automatically marked as non-billable.")
    
    nxt_rev = REVISION_ORDER[rev_idx]
    
    st.markdown(f"""
    <div style="background:#fff7ed; padding:10px; border-radius:8px; margin:15px 0; display:flex; justify-content:space-between; align-items:center;">
        <span style="font-size:0.8rem; color:#64748b;">REVISION FOR</span>
        <span style="font-weight:700; color:#9a3412; font-size:1.1rem;">{nxt_rev}</span>
    </div>
    """, unsafe_allow_html=True)
    
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
    st.markdown('</div>', unsafe_allow_html=True)

# --- ROW 2: MANAGEMENT ---
col3, col4 = st.columns([1.2, 2])

# [BLOCK 3] FINANCE & EDIT
with col3:
    st.markdown('<div class="block-card theme-green">', unsafe_allow_html=True)
    st.markdown('<div class="card-header">⚙️ Manager (Edit/Delete)</div>', unsafe_allow_html=True)
    
    if not df.empty:
        # FILTER ONLY NEW TASKS FOR PAYMENT
        billable = df[df["Type"] == "New Task"].iloc[::-1]
        if not billable.empty:
            t_map = {f"{r['Task / File']} ({r['Assigned To']})": i for i, r in billable.iterrows()}
            sel = st.selectbox("Select Task", list(t_map.keys()))
            idx = t_map[sel]
            
            tab_pay, tab_del = st.tabs(["Update", "Delete"])
            
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
                st.warning("⚠️ This will permanently remove the task.")
                if st.button("🗑️ Delete Task", type="secondary"):
                    df = df.drop(idx)
                    conn.update(data=df)
                    st.success("Deleted!")
                    st.rerun()
        else: st.info("No billable tasks.")
    else: st.info("No Data.")
    st.markdown('</div>', unsafe_allow_html=True)

# [BLOCK 4] SMART LOGS
with col4:
    st.markdown('<div class="block-card theme-dark">', unsafe_allow_html=True)
    c_head, c_filt = st.columns([2, 1])
    c_head.markdown('<div style="font-size:1.1rem; font-weight:700; color:white;">📋 Database</div>', unsafe_allow_html=True)
    
    search = c_filt.text_input("🔍 Search...", placeholder="Name or File", label_visibility="collapsed")
    
    if not df.empty:
        # FILTER LOGIC
        view_df = df.iloc[::-1].copy()
        if search:
            view_df = view_df[
                view_df['Task / File'].str.contains(search, case=False) | 
                view_df['Assigned To'].str.contains(search, case=False)
            ]
        
        # Display with Priority Icons
        st.dataframe(
            view_df,
            height=350,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Priority": st.column_config.TextColumn("🔥", width="small"),
                "Task / File": st.column_config.TextColumn("File", width="medium"),
                "Type": st.column_config.TextColumn("Type", width="small"),
                "Amount": st.column_config.NumberColumn("PKR", format="%d"),
                "Payment Status": st.column_config.TextColumn("Pay", width="small"),
            }
        )
    else: st.write("Empty.")
    st.markdown('</div>', unsafe_allow_html=True)

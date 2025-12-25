import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Write Wise Task Distributor", layout="wide", page_icon="✨")

# --- 2. CSS STYLING ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;700&display=swap');
    html, body, [class*="css"] { font-family: 'Outfit', sans-serif; color: #0f172a; }
    .stApp { background-color: #f8fafc; }
    
    .top-nav {
        background: white; padding: 20px 30px; border-radius: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05); display: flex; align-items: center;
        justify-content: space-between; margin-bottom: 25px; border: 1px solid #e2e8f0;
    }
    .top-nav h1 {
        margin: 0; font-size: 1.5rem; font-weight: 700;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .badge { background: #eff6ff; color: #3b82f6; padding: 5px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 600; }
    
    .stat-card {
        background: white; padding: 20px; border-radius: 16px; border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); text-align: center; transition: transform 0.2s;
    }
    .stat-card:hover { transform: translateY(-3px); border-color: #cbd5e1; }
    .stat-num { font-size: 2.2rem; font-weight: 700; color: #1e293b; }
    .stat-label { font-size: 0.9rem; color: #64748b; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; }

    .action-container {
        background: white; border-radius: 20px; padding: 30px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05); border: 1px solid #e2e8f0;
    }

    .hero-assignee {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        padding: 25px; border-radius: 16px; text-align: center; color: white;
        margin: 20px 0; position: relative; overflow: hidden;
    }
    .hero-assignee::before {
        content: ""; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 60%);
        animation: rotate 10s linear infinite;
    }
    @keyframes rotate { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
    .hero-assignee h2 { color: white; margin: 0; font-size: 1.8rem; font-weight: 700; position: relative; z-index: 1; }
    .hero-assignee p { color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem; font-weight: 500; position: relative; z-index: 1; }

    .user-item { display: flex; align-items: center; padding: 10px; margin-bottom: 8px; border-radius: 10px; transition: 0.2s; }
    .user-item.active { background: #eff6ff; border: 1px solid #bfdbfe; }
    .user-item .dot { height: 8px; width: 8px; border-radius: 50%; margin-right: 12px; }
    .dot-active { background: #3b82f6; box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.2); }
    .dot-inactive { background: #cbd5e1; }
    .user-name { font-size: 0.95rem; font-weight: 500; color: #334155; }
    .user-status { font-size: 0.75rem; color: #64748b; margin-left: auto; }

    div.stButton > button {
        background: #0f172a; color: white; border-radius: 12px; border: none; padding: 12px 20px;
        font-weight: 600; width: 100%; transition: all 0.2s;
    }
    div.stButton > button:hover { background: #334155; transform: scale(1.01); }
    
    .summary-box { background: #ecfdf5; padding: 15px; border-radius: 12px; border: 1px solid #a7f3d0; margin-top: 20px; }
    .summary-title { font-weight: bold; color: #065f46; margin-bottom: 10px; display: block; }
    </style>
""", unsafe_allow_html=True)

# --- 3. DATA & LOGIC ---
NEW_TASK_ORDER = ["Muhammad Imran", "Mazhar Abbas", "Muhammad Ahmad"]
REVISION_ORDER = ["Muhammad Ahmad", "Mazhar Abbas", "Muhammad Imran"]

conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    # Make sure these headers match your Google Sheet exactly!
    req = ["Task / File", "Type", "Assigned To", "Time", "Work Category", "Amount", "Payment Status"]
    try:
        df = conn.read(ttl=0)
        # Fill missing columns if they don't exist
        for col in req:
            if col not in df.columns:
                df[col] = "" if col != "Amount" else 0
        
        # Clean Amount Column (remove any non-numeric text if present)
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
        
        return df.dropna(how="all")
    except:
        return pd.DataFrame(columns=req)

df = get_data()

# Round Robin Logic
new_idx = len(df[df["Type"] == "New Task"]) % 3
rev_idx = len(df[df["Type"] == "Revision"]) % 3

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("### 👥 Team Status")
    
    st.caption("NEW TASK CYCLE")
    for i, member in enumerate(NEW_TASK_ORDER):
        is_active = (i == new_idx)
        st.markdown(f"""
        <div class="user-item {'active' if is_active else ''}">
            <div class="dot {'dot-active' if is_active else 'dot-inactive'}"></div>
            <div class="user-name">{member}</div>
            <div class="user-status">{'Next Up' if is_active else 'Waiting'}</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.caption("REVISION CYCLE")
    for i, member in enumerate(REVISION_ORDER):
        is_active = (i == rev_idx)
        st.markdown(f"""
        <div class="user-item {'active' if is_active else ''}">
            <div class="dot {'dot-active' if is_active else 'dot-inactive'}" style="background: {'#f59e0b' if is_active else '#cbd5e1'}"></div>
            <div class="user-name">{member}</div>
            <div class="user-status">{'Next Up' if is_active else 'Waiting'}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # --- MONTHLY REPORT (SMART DATE FIX) ---
    st.markdown("### 📊 Monthly Report")
    if not df.empty:
        try:
            # Smart Date Converter: Handles both "13/12/2024" and "13-Dec-2024"
            df['DateObj'] = pd.to_datetime(df['Time'], errors='coerce', dayfirst=True)
            
            current_month = datetime.now().month
            current_year = datetime.now().year
            
            # Filter for this month
            monthly_df = df[
                (df['DateObj'].dt.month == current_month) & 
                (df['DateObj'].dt.year == current_year)
            ]
            
            total_tasks = len(monthly_df)
            total_rec = monthly_df[monthly_df['Payment Status'] == 'Received']['Amount'].sum()
            total_pen = monthly_df[monthly_df['Payment Status'] == 'Pending']['Amount'].sum()
            
            st.markdown(f"""
            <div class="summary-box">
                <span class="summary-title">📅 Report: {datetime.now().strftime('%B %Y')}</span>
                <p style="margin:5px 0; display:flex; justify-content:space-between;">
                    <span>Total Tasks:</span> <strong>{total_tasks}</strong>
                </p>
                <p style="margin:5px 0; display:flex; justify-content:space-between; color:green;">
                    <span>Received:</span> <strong>Rs. {total_rec:,.0f}</strong>
                </p>
                <p style="margin:5px 0; display:flex; justify-content:space-between; color:red;">
                    <span>Pending:</span> <strong>Rs. {total_pen:,.0f}</strong>
                </p>
            </div>
            """, unsafe_allow_html=True)
        except Exception as e: 
            st.warning("Could not calculate dates.")
    else: st.info("No data available.")

    st.write("")
    if st.button("🔄 Refresh Data"): st.rerun()

# --- 5. MAIN DASHBOARD ---
st.markdown("""
    <div class="top-nav">
        <h1>Write Wise Task Distributor</h1>
        <div class="badge">Online ●</div>
    </div>
""", unsafe_allow_html=True)

# Stats
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f"""<div class="stat-card"><div class="stat-num">{len(df)}</div><div class="stat-label">Total Workflow</div></div>""", unsafe_allow_html=True)
with c2:
    pending_amt = df[df['Payment Status'] == 'Pending']['Amount'].sum() if not df.empty else 0
    st.markdown(f"""<div class="stat-card"><div class="stat-num" style="color:#ef4444">Rs {pending_amt:,.0f}</div><div class="stat-label">Total Pending Payment</div></div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""<div class="stat-card"><div class="stat-num" style="color:#f59e0b">{len(df[df["Type"] == "Revision"])}</div><div class="stat-label">Revisions</div></div>""", unsafe_allow_html=True)

st.write("")

left, right = st.columns([1, 1.8])
if 'f_key' not in st.session_state: st.session_state.f_key = 0

with left:
    st.markdown('<div class="action-container">', unsafe_allow_html=True)
    st.markdown("### ⚡ Action Center")
    
    # --- TABS FOR ASSIGN & UPDATE ---
    tab1, tab2 = st.tabs(["Assign Task", "Update / Payment"])
    
    with tab1:
        st.write("")
        u_file = st.file_uploader("Upload Document", key=f"k_{st.session_state.f_key}")
        t_type = st.radio("Task Cycle", ["New Task", "Revision"], horizontal=True)
        st.divider()
        st.caption("TASK DETAILS (Optional)")
        
        c_a, c_b = st.columns(2)
        with c_a: work_cat = st.selectbox("Category", ["Assignment", "Article"])
        with c_b: pay_status = st.selectbox("Status", ["Pending", "Received"])
        amount = st.number_input("Amount (Rs)", min_value=0, step=100, value=0)

        nxt = NEW_TASK_ORDER[new_idx] if t_type == "New Task" else REVISION_ORDER[rev_idx]
        
        st.markdown(f"""<div class="hero-assignee"><p>NEXT ASSIGNEE</p><h2>{nxt}</h2></div>""", unsafe_allow_html=True)
        
        if st.button("Confirm & Assign ➝"):
            if u_file:
                # Saves date in standard readable format for next time
                timestamp = datetime.now().strftime("%d-%b-%Y %H:%M")
                new_row = pd.DataFrame([{
                    "Task / File": u_file.name, "Type": t_type, "Assigned To": nxt,
                    "Time": timestamp, "Work Category": work_cat, "Amount": amount, "Payment Status": pay_status
                }])
                conn.update(data=pd.concat([df, new_row], ignore_index=True))
                st.session_state.f_key += 1
                st.toast(f"Task Assigned to {nxt}", icon="✅")
                st.rerun()
            else: st.error("⚠️ Please attach a file.")

    with tab2:
        st.info("Edit existing tasks or Update Payment.")
        if not df.empty:
            rev_df = df.iloc[::-1]
            opts = [f"#{i+1} • {r['Task / File']} ({r['Assigned To']})" for i, r in rev_df.iterrows()]
            s_task = st.selectbox("Select Task to Edit", opts)
            idx = len(df) - 1 - opts.index(s_task)
            
            st.markdown("---")
            edit_action = st.radio("Action Type", ["Update Payment Info", "Change File"], horizontal=True)
            
            if edit_action == "Update Payment Info":
                c1, c2 = st.columns(2)
                with c1: new_amt = st.number_input("Update Amount", value=int(df.at[idx, "Amount"]))
                with c2: 
                    curr_stat = df.at[idx, "Payment Status"]
                    new_stat = st.selectbox("Update Status", ["Pending", "Received"], index=0 if curr_stat=="Pending" else 1)
                
                if st.button("💾 Save Payment Details"):
                    df.at[idx, "Amount"] = new_amt
                    df.at[idx, "Payment Status"] = new_stat
                    conn.update(data=df)
                    st.success("Payment Updated Successfully!")
                    st.rerun()

            elif edit_action == "Change File":
                n_file = st.file_uploader("Upload New File", key="fix")
                if st.button("Update File"):
                    if n_file:
                        df.at[idx, "Task / File"] = n_file.name
                        conn.update(data=df)
                        st.success("File Replaced!")
                        st.rerun()
        else: st.warning("No records found.")
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="action-container">', unsafe_allow_html=True)
    st.markdown("### 📋 Activity Log")
    if not df.empty:
        disp_df = df.iloc[::-1].copy()
        st.dataframe(
            disp_df, hide_index=True, use_container_width=True, height=600,
            column_config={
                "Task / File": st.column_config.TextColumn("File", width="medium"),
                "Type": st.column_config.TextColumn("Type", width="small"),
                "Amount": st.column_config.NumberColumn("Amount", format="Rs %d"),
                "Payment Status": st.column_config.TextColumn("Status", width="small"),
                "Assigned To": st.column_config.TextColumn("Member", width="medium"),
                "Time": st.column_config.TextColumn("Time", width="small"),
            }
        )
    else: st.info("No tasks in the system yet.")
    st.markdown('</div>', unsafe_allow_html=True)

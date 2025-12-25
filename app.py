import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="Write Wise Blocks", layout="wide", page_icon="🔲")

# --- 2. BLOCK STYLE CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; background-color: #f0f2f6; }
    
    /* REMOVE DEFAULT PADDING */
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }

    /* --- THE BLOCK CLASS --- */
    .dashboard-block {
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        color: #1e293b;
    }

    /* COLORS FOR BLOCKS */
    .blk-blue { background-color: #e0f2fe; border: 2px solid #3b82f6; }   /* New Task */
    .blk-orange { background-color: #ffedd5; border: 2px solid #f97316; } /* Revision */
    .blk-green { background-color: #dcfce7; border: 2px solid #22c55e; }  /* Payment */
    .blk-white { background-color: #ffffff; border: 2px solid #cbd5e1; }  /* Logs */

    /* HEADERS INSIDE BLOCKS */
    .blk-header {
        font-size: 1.2rem;
        font-weight: 800;
        text-transform: uppercase;
        margin-bottom: 15px;
        display: flex; align-items: center; gap: 10px;
    }
    .txt-blue { color: #1e40af; }
    .txt-orange { color: #9a3412; }
    .txt-green { color: #166534; }
    .txt-dark { color: #334155; }

    /* NEXT PERSON CARD */
    .assign-card {
        background: white; padding: 10px; border-radius: 8px;
        text-align: center; font-weight: bold; font-size: 1.1rem;
        border: 1px dashed #94a3b8; margin: 15px 0;
    }

    /* BUTTON STYLES */
    div.stButton > button {
        width: 100%; border-radius: 8px; font-weight: bold; border: none; padding: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. DATA & LOGIC ---
NEW_TASK_ORDER = ["Muhammad Imran", "Mazhar Abbas", "Muhammad Ahmad"]
REVISION_ORDER = ["Muhammad Ahmad", "Mazhar Abbas", "Muhammad Imran"]

conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    req = ["Task / File", "Type", "Assigned To", "Time", "Work Category", "Amount", "Payment Status"]
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
    st.header("👥 Team Status")
    st.caption("NEW TASK TURN")
    for i, m in enumerate(NEW_TASK_ORDER):
        st.markdown(f"{'🔵' if i==new_idx else '⚪'} {m}")
    
    st.write("")
    st.caption("REVISION TURN")
    for i, m in enumerate(REVISION_ORDER):
        st.markdown(f"{'🟠' if i==rev_idx else '⚪'} {m}")
        
    st.divider()
    if st.button("🔄 Refresh System"): st.rerun()

# --- 5. MAIN DASHBOARD (BLOCKS LAYOUT) ---

st.title("🔲 Task Command Center")

# ROW 1: ASSIGNMENT BLOCKS
c1, c2 = st.columns(2)

# --- BLUE BLOCK: NEW TASK ---
with c1:
    st.markdown("""
    <div class="dashboard-block blk-blue">
        <div class="blk-header txt-blue">📘 New Assignment Zone</div>
    </div>
    """, unsafe_allow_html=True)
    
    # We put streamlit widgets normally, visually they sit under the colored div header
    with st.container():
        u_file = st.file_uploader("Upload New File", key="n_file")
        col_a, col_b = st.columns(2)
        cat = col_a.selectbox("Category", ["Assignment", "Article"], key="cat")
        pay = col_b.selectbox("Payment Status", ["Pending", "Received"], key="pay")
        amt = st.number_input("Amount (PKR)", step=100, value=0, key="amt")

        nxt = NEW_TASK_ORDER[new_idx]
        st.markdown(f'<div class="assign-card" style="color:#1e40af">Assigned To: {nxt}</div>', unsafe_allow_html=True)
        
        if st.button("✅ Assign New Task", type="primary"):
            if u_file:
                ts = datetime.now().strftime("%d-%b-%Y %H:%M")
                new_row = pd.DataFrame([{
                    "Task / File": u_file.name, "Type": "New Task", "Assigned To": nxt,
                    "Time": ts, "Work Category": cat, "Amount": amt, "Payment Status": pay
                }])
                conn.update(data=pd.concat([df, new_row], ignore_index=True))
                st.toast("Task Assigned!")
                st.rerun()
            else: st.error("No File!")

# --- ORANGE BLOCK: REVISION ---
with c2:
    st.markdown("""
    <div class="dashboard-block blk-orange">
        <div class="blk-header txt-orange">📙 Revision Hub</div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        r_file = st.file_uploader("Upload Revision File", key="r_file")
        st.info("ℹ️ Revisions are free of cost.")
        
        nxt_rev = REVISION_ORDER[rev_idx]
        st.markdown(f'<div class="assign-card" style="color:#9a3412">Revision For: {nxt_rev}</div>', unsafe_allow_html=True)
        
        if st.button("🔄 Assign Revision"):
            if r_file:
                ts = datetime.now().strftime("%d-%b-%Y %H:%M")
                new_row = pd.DataFrame([{
                    "Task / File": r_file.name, "Type": "Revision", "Assigned To": nxt_rev,
                    "Time": ts, "Work Category": "Revision", "Amount": 0, "Payment Status": "N/A"
                }])
                conn.update(data=pd.concat([df, new_row], ignore_index=True))
                st.toast("Revision Sent!")
                st.rerun()
            else: st.error("No File!")

st.write("") # Spacer

# ROW 2: MANAGEMENT BLOCKS
c3, c4 = st.columns([1, 1.5])

# --- GREEN BLOCK: FINANCE ---
with c3:
    st.markdown("""
    <div class="dashboard-block blk-green">
        <div class="blk-header txt-green">💵 Payment Manager</div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        if not df.empty:
            # Only New Tasks
            billable = df[df["Type"] == "New Task"].iloc[::-1]
            if not billable.empty:
                t_map = {f"{r['Task / File']} ({r['Assigned To']})": i for i, r in billable.iterrows()}
                sel = st.selectbox("Select Task to Update", list(t_map.keys()))
                idx = t_map[sel]
                
                n_amt = st.number_input("Update Amount", value=int(df.at[idx, "Amount"]), key="e_amt")
                n_st = st.selectbox("Status", ["Pending", "Received"], index=0 if df.at[idx, "Payment Status"]=="Pending" else 1, key="e_st")
                
                if st.button("💾 Save Payment Info"):
                    df.at[idx, "Amount"] = n_amt
                    df.at[idx, "Payment Status"] = n_st
                    conn.update(data=df)
                    st.success("Updated!")
                    st.rerun()
            else: st.warning("No billable tasks found.")
        else: st.warning("No data.")

# --- WHITE BLOCK: LOGS ---
with c4:
    st.markdown("""
    <div class="dashboard-block blk-white">
        <div class="blk-header txt-dark">📋 Activity Database</div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        if not df.empty:
            p_amt = df[df['Payment Status'] == 'Pending']['Amount'].sum()
            st.caption(f"Total Pending Amount: Rs {p_amt:,.0f}")
            
            st.dataframe(
                df.iloc[::-1],
                height=300,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Task / File": st.column_config.TextColumn("File", width="medium"),
                    "Type": st.column_config.TextColumn("Type", width="small"),
                    "Amount": st.column_config.NumberColumn("PKR", format="%d"),
                }
            )
        else: st.info("Database Empty.")

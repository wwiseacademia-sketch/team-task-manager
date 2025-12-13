import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="TaskFlow Pro", layout="wide", page_icon="⚡")

# --- 2. ADVANCED CSS (THE MAGIC) ---
st.markdown("""
    <style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    /* General Settings */
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
        color: #1e293b;
    }
    .stApp {
        background-color: #f3f4f6;
    }

    /* Animated Gradient Header */
    .hero-header {
        background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
        padding: 40px;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
    }
    @keyframes gradient {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }
    .hero-header h1 { font-weight: 800; font-size: 3rem; margin: 0; color: white; text-shadow: 2px 2px 4px rgba(0,0,0,0.2); }
    .hero-header p { font-size: 1.2rem; opacity: 0.9; margin-top: 5px; }

    /* Modern Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
        backdrop-filter: blur(4px);
        -webkit-backdrop-filter: blur(4px);
        border: 1px solid rgba(255, 255, 255, 0.18);
        margin-bottom: 20px;
        transition: transform 0.3s;
    }
    .glass-card:hover { transform: translateY(-5px); }

    /* Custom Buttons */
    .stButton > button {
        background: #4f46e5;
        color: white;
        border-radius: 12px;
        height: 50px;
        font-weight: 600;
        font-size: 16px;
        border: none;
        box-shadow: 0 4px 14px 0 rgba(79, 70, 229, 0.39);
        transition: 0.2s;
        width: 100%;
    }
    .stButton > button:hover {
        background: #4338ca;
        transform: scale(1.02);
    }

    /* Next Assignee Highlight Box */
    .assignee-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin: 20px 0;
    }
    .assignee-box h3 { margin: 0; font-size: 1rem; opacity: 0.8; color: white;}
    .assignee-box h2 { margin: 5px 0 0 0; font-size: 1.8rem; font-weight: 700; color: white; }

    /* Sidebar Status Timeline */
    .timeline-item {
        padding: 10px;
        border-left: 3px solid #e2e8f0;
        margin-left: 10px;
        padding-left: 20px;
        position: relative;
    }
    .timeline-item.active { border-left: 3px solid #4f46e5; }
    .timeline-dot {
        height: 12px; width: 12px; background-color: #cbd5e1;
        border-radius: 50%; position: absolute; left: -7.5px; top: 15px;
    }
    .timeline-item.active .timeline-dot { background-color: #4f46e5; box-shadow: 0 0 0 4px rgba(79, 70, 229, 0.2); }
    
    /* Stats Numbers */
    div[data-testid="stMetricValue"] { font-size: 2rem; color: #4f46e5; font-weight: 700; }
    </style>
""", unsafe_allow_html=True)

# --- 3. DATA & LOGIC ---
NEW_TASK_ORDER = ["Muhammad Imran", "Mazhar Abbas", "Muhammad Ahmad"]
REVISION_ORDER = ["Muhammad Ahmad", "Mazhar Abbas", "Muhammad Imran"]

conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    try:
        df = conn.read(ttl=0)
        req = ["Task / File", "Type", "Assigned To", "Time"]
        if df.empty or not all(c in df.columns for c in req): return pd.DataFrame(columns=req)
        return df.dropna(how="all")
    except: return pd.DataFrame(columns=["Task / File", "Type", "Assigned To", "Time"])

df = get_data()

# Calculate Indices
new_idx = len(df[df["Type"] == "New Task"]) % 3
rev_idx = len(df[df["Type"] == "Revision"]) % 3

# --- 4. SIDEBAR (TIMELINE) ---
with st.sidebar:
    st.markdown("### 👤 Admin Panel")
    st.info("Logged in as: **Zaheer Abbas**")
    st.write("")
    
    st.markdown("#### 🔄 Workflow Status")
    
    # Custom Timeline HTML for Sidebar
    st.caption("New Task Cycle")
    for i, m in enumerate(NEW_TASK_ORDER):
        active_class = "active" if i == new_idx else ""
        st.markdown(f"""
        <div class="timeline-item {active_class}">
            <div class="timeline-dot"></div>
            <div style="font-weight: {'bold' if i == new_idx else 'normal'}; color: {'#1e293b' if i == new_idx else '#94a3b8'}">
                {m}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.caption("Revision Cycle")
    for i, m in enumerate(REVISION_ORDER):
        active_class = "active" if i == rev_idx else ""
        st.markdown(f"""
        <div class="timeline-item {active_class}">
            <div class="timeline-dot"></div>
            <div style="font-weight: {'bold' if i == rev_idx else 'normal'}; color: {'#1e293b' if i == rev_idx else '#94a3b8'}">
                {m}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    if st.button("🔄 Refresh System"): st.rerun()

# --- 5. MAIN DASHBOARD ---

# Animated Header
st.markdown("""
    <div class="hero-header">
        <h1>🚀 TaskFlow Command Center</h1>
        <p>Streamlined Assignment & Revision Management System</p>
    </div>
""", unsafe_allow_html=True)

# Stats Cards
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown('<div class="glass-card" style="text-align:center">', unsafe_allow_html=True)
    st.metric("Total Workflow", len(df))
    st.markdown('</div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div class="glass-card" style="text-align:center">', unsafe_allow_html=True)
    st.metric("New Tasks", len(df[df["Type"] == "New Task"]))
    st.markdown('</div>', unsafe_allow_html=True)
with c3:
    st.markdown('<div class="glass-card" style="text-align:center">', unsafe_allow_html=True)
    st.metric("Revisions", len(df[df["Type"] == "Revision"]))
    st.markdown('</div>', unsafe_allow_html=True)

# Main Control Area
col_left, col_right = st.columns([1, 1.5])

if 'f_key' not in st.session_state: st.session_state.f_key = 0

with col_left:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### ⚡ Quick Actions")
    
    tab1, tab2 = st.tabs(["Assign Task", "Fix Mistake"])
    
    with tab1:
        st.write("")
        u_file = st.file_uploader("📂 Upload Document", key=f"k_{st.session_state.f_key}")
        t_type = st.radio("Select Category", ["New Task", "Revision"], horizontal=True)
        
        # Logic
        nxt = NEW_TASK_ORDER[new_idx] if t_type == "New Task" else REVISION_ORDER[rev_idx]
        
        # Big Visual Box
        st.markdown(f"""
            <div class="assignee-box">
                <h3>UP NEXT</h3>
                <h2>{nxt}</h2>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Launch Assignment"):
            if u_file:
                new_row = pd.DataFrame([{
                    "Task / File": u_file.name, "Type": t_type, 
                    "Assigned To": nxt, "Time": datetime.now().strftime("%d-%b %I:%M %p")
                }])
                conn.update(data=pd.concat([df, new_row], ignore_index=True))
                st.session_state.f_key += 1
                st.toast(f"Assigned to {nxt}", icon="✅")
                st.rerun()
            else:
                st.error("⚠️ File missing!")

    with tab2:
        st.warning("Use this to fix incorrect file uploads.")
        if not df.empty:
            rev_df = df.iloc[::-1]
            opts = [f"#{i+1} • {r['Task / File']}" for i, r in rev_df.iterrows()]
            s_task = st.selectbox("Select Task", opts)
            real_idx = len(df) - 1 - opts.index(s_task)
            
            n_file = st.file_uploader("Correct File", key="fix")
            if st.button("💾 Save Fix"):
                if n_file:
                    df.at[real_idx, "Task / File"] = n_file.name
                    conn.update(data=df)
                    st.success("Fixed!")
                    st.rerun()
        else: st.info("No tasks.")

    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 📋 Live Activity Feed")
    
    if not df.empty:
        disp_df = df.iloc[::-1].copy()
        st.dataframe(
            disp_df, hide_index=True, use_container_width=True, height=450,
            column_config={
                "Task / File": st.column_config.TextColumn("File Name", width="large"),
                "Type": st.column_config.TextColumn("Type", width="small"),
                "Assigned To": st.column_config.TextColumn("Owner", width="medium"),
                "Time": st.column_config.TextColumn("Sent At", width="medium"),
            }
        )
    else:
        st.info("No activity recorded yet.")
    st.markdown('</div>', unsafe_allow_html=True)

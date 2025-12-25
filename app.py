import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Write Wise Pro", layout="wide", page_icon="💎")

# --- 2. ULTRA MODERN CSS (GLASSMORPHISM) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

    /* GLOBAL THEME */
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
        color: #2d3748;
    }
    .stApp {
        background-color: #f3f4f6;
        background-image: radial-gradient(#e2e8f0 1px, transparent 1px);
        background-size: 20px 20px;
    }

    /* CUSTOM CARD STYLE (GLASS EFFECT) */
    .glass-card {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.6);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
        padding: 24px;
        margin-bottom: 20px;
        transition: all 0.3s ease-in-out;
    }
    .glass-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.12);
    }

    /* HEADER STYLE */
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 10px;
        margin-bottom: 20px;
    }
    .app-title {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -1px;
    }
    .status-badge {
        background: #d1fae5;
        color: #065f46;
        padding: 6px 16px;
        border-radius: 50px;
        font-size: 0.85rem;
        font-weight: 600;
        box-shadow: 0 2px 10px rgba(16, 185, 129, 0.2);
    }

    /* STATS CARDS */
    .stat-box {
        text-align: center;
        padding: 15px;
    }
    .stat-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1a202c;
        line-height: 1.2;
    }
    .stat-label {
        font-size: 0.85rem;
        color: #718096;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }

    /* HERO ASSIGNEE SECTION */
    .hero-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 30px;
        color: white;
        text-align: center;
        position: relative;
        overflow: hidden;
        box-shadow: 0 10px 25px rgba(118, 75, 162, 0.3);
    }
    .hero-box h2 {
        color: white;
        font-size: 2rem;
        font-weight: 700;
        margin: 10px 0 0 0;
    }
    .hero-box p {
        color: rgba(255,255,255,0.8);
        margin: 0;
        font-weight: 500;
    }

    /* SIDEBAR USERS */
    .user-row {
        display: flex;
        align-items: center;
        padding: 12px;
        margin-bottom: 8px;
        border-radius: 12px;
        background: white;
        border: 1px solid transparent;
        transition: 0.2s;
    }
    .user-row.active-user {
        background: #ebf4ff;
        border-color: #bee3f8;
        box-shadow: 0 2px 5px rgba(66, 153, 225, 0.1);
    }
    .avatar {
        width: 35px;
        height: 35px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        color: white;
        margin-right: 12px;
        font-size: 0.9rem;
    }
    
    /* BUTTONS */
    div.stButton > button {
        background: linear-gradient(90deg, #1a202c 0%, #2d3748 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 12px;
        font-weight: 600;
        transition: all 0.3s;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        width: 100%;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(0,0,0,0.2);
    }
    
    /* INPUT FIELDS */
    .stTextInput > div > div, .stSelectbox > div > div, .stNumberInput > div > div {
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        background-color: white;
    }
    
    /* SUMMARY WIDGET */
    .report-widget {
        background: linear-gradient(180deg, #ffffff 0%, #f7fafc 100%);
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 20px;
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. DATA & LOGIC ---
NEW_TASK_ORDER = ["Muhammad Imran", "Mazhar Abbas", "Muhammad Ahmad"]
REVISION_ORDER = ["Muhammad Ahmad", "Mazhar Abbas", "Muhammad Imran"]

# Avatars Initials Colors
AVATAR_COLORS = {
    "Muhammad Imran": "#3b82f6", # Blue
    "Mazhar Abbas": "#8b5cf6",   # Purple
    "Muhammad Ahmad": "#10b981"  # Emerald
}

conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    req = ["Task / File", "Type", "Assigned To", "Time", "Work Category", "Amount", "Payment Status"]
    try:
        df = conn.read(ttl=0)
        for col in req:
            if col not in df.columns:
                df[col] = "" if col != "Amount" else 0
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
        return df.dropna(how="all")
    except:
        return pd.DataFrame(columns=req)

df = get_data()

new_idx = len(df[df["Type"] == "New Task"]) % 3
rev_idx = len(df[df["Type"] == "Revision"]) % 3

# --- 4. SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/906/906343.png", width=50)
    st.markdown("### Team Workflow")
    
    st.markdown("<p style='font-size:0.8rem; color:#a0aec0; margin-bottom:5px; font-weight:600;'>NEW TASK QUEUE</p>", unsafe_allow_html=True)
    for i, member in enumerate(NEW_TASK_ORDER):
        is_active = (i == new_idx)
        initials = "".join([n[0] for n in member.split()[:2]])
        color = AVATAR_COLORS.get(member, "#cbd5e1")
        
        st.markdown(f"""
        <div class="user-row {'active-user' if is_active else ''}">
            <div class="avatar" style="background:{color}; box-shadow: 0 4px 10px {color}50;">{initials}</div>
            <div style="flex-grow:1;">
                <div style="font-weight:600; font-size:0.9rem;">{member}</div>
                <div style="font-size:0.75rem; color:{'#3b82f6' if is_active else '#a0aec0'};">{'● Next In Line' if is_active else 'Waiting'}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.markdown("<p style='font-size:0.8rem; color:#a0aec0; margin-bottom:5px; font-weight:600;'>REVISION QUEUE</p>", unsafe_allow_html=True)
    for i, member in enumerate(REVISION_ORDER):
        is_active = (i == rev_idx)
        initials = "".join([n[0] for n in member.split()[:2]])
        # Orange/Amber for Revision
        rev_color = "#f59e0b" if is_active else "#cbd5e1"
        
        st.markdown(f"""
        <div class="user-row {'active-user' if is_active else ''}">
            <div class="avatar" style="background:{rev_color}; box-shadow: 0 4px 10px {rev_color}50;">{initials}</div>
            <div style="flex-grow:1;">
                <div style="font-weight:600; font-size:0.9rem;">{member}</div>
                <div style="font-size:0.75rem; color:{'#f59e0b' if is_active else '#a0aec0'};">{'● Next In Line' if is_active else 'Waiting'}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Monthly Report Widget
    st.write("")
    st.markdown("### Financials")
    if not df.empty:
        try:
            df['DateObj'] = pd.to_datetime(df['Time'], errors='coerce', dayfirst=True)
            current_month = datetime.now().month
            current_year = datetime.now().year
            monthly_df = df[(df['DateObj'].dt.month == current_month) & (df['DateObj'].dt.year == current_year)]
            
            t_tasks = len(monthly_df)
            t_rec = monthly_df[monthly_df['Payment Status'] == 'Received']['Amount'].sum()
            t_pen = monthly_df[monthly_df['Payment Status'] == 'Pending']['Amount'].sum()
            
            st.markdown(f"""
            <div class="report-widget">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                    <span style="font-weight:700; color:#2d3748;">{datetime.now().strftime('%B %Y')}</span>
                    <span style="background:#edf2f7; padding:2px 8px; border-radius:10px; font-size:0.7rem;">REPORT</span>
                </div>
                <div style="display:flex; justify-content:space-between; font-size:0.9rem; margin-bottom:5px;">
                    <span style="color:#718096">Completed Tasks</span>
                    <span style="font-weight:600">{t_tasks}</span>
                </div>
                <div style="height:1px; background:#e2e8f0; margin:10px 0;"></div>
                <div style="display:flex; justify-content:space-between; font-size:0.9rem; color:#059669;">
                    <span>Received</span>
                    <span style="font-weight:700">Rs {t_rec:,.0f}</span>
                </div>
                <div style="display:flex; justify-content:space-between; font-size:0.9rem; color:#dc2626; margin-top:5px;">
                    <span>Pending</span>
                    <span style="font-weight:700">Rs {t_pen:,.0f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        except: pass
        
    st.write("")
    if st.button("🔄 Sync System"): st.rerun()

# --- 5. MAIN CONTENT ---

# Header
st.markdown("""
<div class="header-container">
    <div class="app-title">WriteWise <span style="font-weight:300; color:#718096;">Distributor</span></div>
    <div class="status-badge">⚡ System Online</div>
</div>
""", unsafe_allow_html=True)

# Stats Row
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f"""
    <div class="glass-card stat-box">
        <div class="stat-value">{len(df)}</div>
        <div class="stat-label">Total Workflow</div>
    </div>""", unsafe_allow_html=True)
with c2:
    pending_amt = df[df['Payment Status'] == 'Pending']['Amount'].sum() if not df.empty else 0
    st.markdown(f"""
    <div class="glass-card stat-box">
        <div class="stat-value" style="color:#ef4444;">{pending_amt:,.0f}</div>
        <div class="stat-label">Pending (PKR)</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""
    <div class="glass-card stat-box">
        <div class="stat-value" style="color:#f59e0b;">{len(df[df["Type"] == "Revision"])}</div>
        <div class="stat-label">Revisions Count</div>
    </div>""", unsafe_allow_html=True)

st.write("")

# Action Area
col_left, col_right = st.columns([1, 1.8])
if 'f_key' not in st.session_state: st.session_state.f_key = 0

with col_left:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 🚀 Task Control")
    
    tab_assign, tab_update = st.tabs(["New Assignment", "Update / Payments"])
    
    with tab_assign:
        st.write("")
        u_file = st.file_uploader("Drop file here", key=f"k_{st.session_state.f_key}")
        
        # Inputs
        t_type = st.radio("Cycle Type", ["New Task", "Revision"], horizontal=True)
        st.markdown("---")
        
        row1 = st.columns(2)
        work_cat = row1[0].selectbox("Category", ["Assignment", "Article"])
        pay_status = row1[1].selectbox("Payment", ["Pending", "Received"])
        
        amount = st.number_input("Amount (PKR)", step=100, value=0)
        
        # Hero Section
        nxt = NEW_TASK_ORDER[new_idx] if t_type == "New Task" else REVISION_ORDER[rev_idx]
        st.markdown(f"""
        <div class="hero-box">
            <p>NEXT ASSIGNMENT GOES TO</p>
            <h2>{nxt}</h2>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Confirm & Assign Now ➝"):
            if u_file:
                timestamp = datetime.now().strftime("%d-%b-%Y %H:%M")
                new_row = pd.DataFrame([{
                    "Task / File": u_file.name, "Type": t_type, "Assigned To": nxt,
                    "Time": timestamp, "Work Category": work_cat, "Amount": amount, "Payment Status": pay_status
                }])
                conn.update(data=pd.concat([df, new_row], ignore_index=True))
                st.session_state.f_key += 1
                st.toast("Task Distributed Successfully!", icon="🚀")
                st.rerun()
            else: st.error("Please attach a document.")

    with tab_update:
        st.write("")
        if not df.empty:
            rev_df = df.iloc[::-1]
            opts = [f"{r['Task / File']} ({r['Assigned To']})" for i, r in rev_df.iterrows()]
            s_task = st.selectbox("Select Task", opts)
            # Find Index by matching string logic (simple approach)
            # Better approach is tracking ID but string match works for simple usage
            sel_idx = opts.index(s_task)
            real_idx = len(df) - 1 - sel_idx
            
            st.markdown("#### Edit Details")
            action = st.radio("Select Action", ["Update Payment", "Replace File"], horizontal=True)
            
            if action == "Update Payment":
                c1, c2 = st.columns(2)
                curr_amt = int(df.at[real_idx, "Amount"])
                n_amt = c1.number_input("New Amount", value=curr_amt)
                
                curr_st = df.at[real_idx, "Payment Status"]
                n_st = c2.selectbox("New Status", ["Pending", "Received"], index=0 if curr_st=="Pending" else 1)
                
                if st.button("Save Changes"):
                    df.at[real_idx, "Amount"] = n_amt
                    df.at[real_idx, "Payment Status"] = n_st
                    conn.update(data=df)
                    st.success("Updated!")
                    st.rerun()
            else:
                nf = st.file_uploader("New File")
                if st.button("Replace File"):
                    if nf:
                        df.at[real_idx, "Task / File"] = nf.name
                        conn.update(data=df)
                        st.success("File Replaced!")
                        st.rerun()
        else: st.info("No data to edit.")
        
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 📋 Activity Logs")
    
    if not df.empty:
        disp_df = df.iloc[::-1].copy()
        st.dataframe(
            disp_df,
            hide_index=True,
            use_container_width=True,
            height=650,
            column_config={
                "Task / File": st.column_config.TextColumn("Document", width="medium"),
                "Type": st.column_config.TextColumn("Type", width="small"),
                "Amount": st.column_config.NumberColumn("PKR", format="%d"),
                "Payment Status": st.column_config.TextColumn("Status", width="small"),
                "Assigned To": st.column_config.TextColumn("User", width="medium"),
                "Time": st.column_config.TextColumn("Date", width="small"),
            }
        )
    else:
        st.info("System is ready. Add first task.")
    st.markdown('</div>', unsafe_allow_html=True)

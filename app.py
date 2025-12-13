import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="TeamFlow Pro", layout="wide", page_icon="⚡")

# --- MODERN UI (CSS STYLING) ---
st.markdown("""
    <style>
    /* Global Settings */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background-color: #f8fafc; /* Very light blue-grey */
    }

    /* Gradient Header */
    .header-box {
        background: linear-gradient(135deg, #4f46e5 0%, #3b82f6 100%);
        padding: 30px;
        border-radius: 20px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 10px 25px rgba(63, 72, 204, 0.2);
    }
    .header-box h1 { margin: 0; font-size: 2.2rem; font-weight: 800; color: white; }
    .header-box p { margin: 5px 0 0 0; opacity: 0.8; font-size: 1rem; }

    /* Custom Cards */
    .modern-card {
        background: white;
        padding: 25px;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        border: 1px solid #e2e8f0;
        margin-bottom: 20px;
    }

    /* Assign Button Styling */
    div.stButton > button {
        background: linear-gradient(90deg, #4f46e5 0%, #6366f1 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 12px;
        font-weight: 600;
        width: 100%;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.2);
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(79, 70, 229, 0.3);
    }

    /* Next Assignee Highlight */
    .assignee-badge {
        background-color: #eff6ff;
        border-left: 5px solid #3b82f6;
        padding: 15px;
        border-radius: 8px;
        color: #1e293b;
        font-weight: 600;
        margin: 15px 0;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .assignee-badge span { color: #3b82f6; font-size: 1.1rem; }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    
    /* Cycle Status Indicators */
    .status-dot {
        height: 10px; width: 10px; border-radius: 50%; display: inline-block; margin-right: 8px;
    }
    .active-user { background-color: #dbeafe; border: 1px solid #3b82f6; color: #1e3a8a; padding: 8px; border-radius: 8px; font-weight: bold; display: block; margin-bottom: 5px;}
    .inactive-user { color: #94a3b8; padding: 8px; display: block; margin-bottom: 5px;}

    </style>
""", unsafe_allow_html=True)

# --- MEMBERS ---
NEW_TASK_ORDER = ["Muhammad Imran", "Mazhar Abbas", "Muhammad Ahmad"]
REVISION_ORDER = ["Muhammad Ahmad", "Mazhar Abbas", "Muhammad Imran"]

# --- GOOGLE SHEETS CONNECTION ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    try:
        df = conn.read(ttl=0)
        required_cols = ["Task / File", "Type", "Assigned To", "Time"]
        if df.empty or not all(col in df.columns for col in required_cols):
            return pd.DataFrame(columns=required_cols)
        return df.dropna(how="all")
    except:
        return pd.DataFrame(columns=["Task / File", "Type", "Assigned To", "Time"])

df = get_data()

# --- CALCULATE LOGIC ---
total_new = len(df[df["Type"] == "New Task"])
new_idx = total_new % 3

total_rev = len(df[df["Type"] == "Revision"])
rev_idx = total_rev % 3

# --- SIDEBAR (Dashboard Controls) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=50)
    st.title("Admin Panel")
    st.caption(f"Logged in as: **Zaheer Abbas**")
    st.divider()

    st.subheader("🔄 Cycle Status")
    
    # New Task Cycle Visual
    st.markdown("**🟢 New Task Order**")
    for i, member in enumerate(NEW_TASK_ORDER):
        if i == new_idx:
            st.markdown(f"<div class='active-user'>⚡ {member} (Next)</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='inactive-user'>○ {member}</div>", unsafe_allow_html=True)
            
    st.divider()
    
    # Revision Cycle Visual
    st.markdown("**🟠 Revision Order**")
    for i, member in enumerate(REVISION_ORDER):
        if i == rev_idx:
            st.markdown(f"<div class='active-user'>⚡ {member} (Next)</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='inactive-user'>○ {member}</div>", unsafe_allow_html=True)
    
    st.divider()
    if st.button("🔄 Refresh Data"):
        st.rerun()

# --- MAIN DASHBOARD AREA ---

# 1. Header Section
st.markdown("""
    <div class="header-box">
        <h1>⚡ TeamFlow Dashboard</h1>
        <p>Manage assignments, track revisions, and automate workflow.</p>
    </div>
""", unsafe_allow_html=True)

# 2. Stats Row
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Total Tasks Processed", len(df), delta="All Time")
with c2:
    st.metric("New Tasks", total_new, delta="Forward Cycle")
with c3:
    st.metric("Revisions", total_rev, delta="Reverse Cycle")

st.write("") # Spacer

# 3. Action Area & History
col_action, col_history = st.columns([1, 1.8])

if 'file_key' not in st.session_state: st.session_state.file_key = 0

# --- LEFT CARD: ACTION ---
with col_action:
    st.markdown('<div class="modern-card">', unsafe_allow_html=True)
    st.subheader("🚀 Assign Work")
    
    tab_assign, tab_fix = st.tabs(["New Assignment", "Fix Mistake"])
    
    with tab_assign:
        st.write("")
        uploaded_file = st.file_uploader("Drop file here", key=f"up_{st.session_state.file_key}")
        
        task_type = st.radio("Select Category", ["New Task", "Revision"], horizontal=True)

        # Logic
        if task_type == "New Task": 
            next_person = NEW_TASK_ORDER[new_idx]
            role_color = "#3b82f6"
        else: 
            next_person = REVISION_ORDER[rev_idx]
            role_color = "#f59e0b"

        # Visual Badge
        st.markdown(f"""
            <div class="assignee-badge">
                <div>Next Assignee</div>
                <span>{next_person}</span>
            </div>
        """, unsafe_allow_html=True)

        if st.button("Assign Now ➝", use_container_width=True):
            if not uploaded_file:
                st.error("⚠️ Please upload a file first.")
            else:
                new_row = pd.DataFrame([{
                    "Task / File": uploaded_file.name,
                    "Type": task_type,
                    "Assigned To": next_person,
                    "Time": datetime.now().strftime("%d-%b %I:%M %p")
                }])
                updated_df = pd.concat([df, new_row], ignore_index=True)
                conn.update(data=updated_df)
                st.session_state.file_key += 1
                st.toast(f"Success! Task assigned to {next_person}", icon="🎉")
                st.rerun()

    with tab_fix:
        st.info("Upload correct file to replace wrong one.")
        if not df.empty:
            df_rev = df.iloc[::-1]
            options = []
            idx_map = {}
            for i, row in df_rev.iterrows():
                txt = f"#{i+1} • {row['Task / File']} ({row['Assigned To']})"
                options.append(txt)
                idx_map[txt] = i
            
            sel = st.selectbox("Select Task", options)
            real_idx = idx_map[sel]
            
            new_f = st.file_uploader("Correct File", key="fix")
            if st.button("Update File"):
                if new_f:
                    df.at[real_idx, "Task / File"] = new_f.name
                    conn.update(data=df)
                    st.success("Updated!")
                    st.rerun()
        else:
            st.warning("No records found.")

    st.markdown('</div>', unsafe_allow_html=True)

# --- RIGHT CARD: HISTORY ---
with col_history:
    st.markdown('<div class="modern-card">', unsafe_allow_html=True)
    st.subheader("📋 Recent Activity")
    
    if not df.empty:
        d_df = df.iloc[::-1].copy()
        
        # Display Dataframe with modern config
        st.dataframe(
            d_df,
            hide_index=True,
            use_container_width=True,
            height=400,
            column_config={
                "Task / File": st.column_config.TextColumn("File Name", width="large", help="Name of the file"),
                "Type": st.column_config.TextColumn("Category", width="small"),
                "Assigned To": st.column_config.TextColumn("Member", width="medium"),
                "Time": st.column_config.TextColumn("Timestamp", width="medium"),
            }
        )
    else:
        st.info("No tasks assigned yet.")
        
    st.markdown('</div>', unsafe_allow_html=True)

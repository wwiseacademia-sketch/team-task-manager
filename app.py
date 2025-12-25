import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Write Wise Pro", layout="wide", page_icon="💎")

# --- 2. CSS STYLING ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Poppins', sans-serif; color: #2d3748; }
    .stApp { background-color: #f3f4f6; background-image: radial-gradient(#e2e8f0 1px, transparent 1px); background-size: 20px 20px; }
    .glass-card {
        background: rgba(255, 255, 255, 0.85); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
        border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.6);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07); padding: 24px; margin-bottom: 20px;
    }
    .hero-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px; padding: 30px; color: white; text-align: center;
        box-shadow: 0 10px 25px rgba(118, 75, 162, 0.3);
    }
    .hero-box h2 { color: white; margin: 10px 0 0 0; }
    div.stButton > button {
        background: linear-gradient(90deg, #1a202c 0%, #2d3748 100%); color: white;
        border: none; padding: 12px 24px; border-radius: 12px; font-weight: 600; width: 100%;
    }
    .stTextInput > div > div, .stSelectbox > div > div, .stNumberInput > div > div {
        border-radius: 10px; border: 1px solid #e2e8f0; background-color: white;
    }
    .user-row { display: flex; align-items: center; padding: 12px; margin-bottom: 8px; border-radius: 12px; background: white; }
    .user-row.active-user { background: #ebf4ff; border-color: #bee3f8; }
    .avatar { width: 35px; height: 35px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; margin-right: 12px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- 3. DATA LOGIC ---
NEW_TASK_ORDER = ["Muhammad Imran", "Mazhar Abbas", "Muhammad Ahmad"]
REVISION_ORDER = ["Muhammad Ahmad", "Mazhar Abbas", "Muhammad Imran"]
AVATAR_COLORS = {"Muhammad Imran": "#3b82f6", "Mazhar Abbas": "#8b5cf6", "Muhammad Ahmad": "#10b981"}

conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    req = ["Task / File", "Type", "Assigned To", "Time", "Work Category", "Amount", "Payment Status"]
    try:
        df = conn.read(ttl=0)
        for col in req:
            if col not in df.columns: df[col] = "" if col != "Amount" else 0
        
        # CLEANING DATA TO FIX DROPDOWN ISSUE
        df['Type'] = df['Type'].astype(str).str.strip()  # Remove spaces
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
        
        return df.dropna(how="all")
    except: return pd.DataFrame(columns=req)

df = get_data()

new_idx = len(df[df["Type"] == "New Task"]) % 3
rev_idx = len(df[df["Type"] == "Revision"]) % 3

# --- 4. SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/906/906343.png", width=50)
    st.markdown("### Team Workflow")
    
    # NEW TASK QUEUE
    st.markdown("<p style='font-size:0.8rem; color:#a0aec0; margin-bottom:5px; font-weight:600;'>NEW TASK QUEUE</p>", unsafe_allow_html=True)
    for i, member in enumerate(NEW_TASK_ORDER):
        is_active = (i == new_idx)
        initials = "".join([n[0] for n in member.split()[:2]])
        color = AVATAR_COLORS.get(member, "#cbd5e1")
        st.markdown(f"""<div class="user-row {'active-user' if is_active else ''}"><div class="avatar" style="background:{color};">{initials}</div><div style="flex-grow:1;"><div style="font-weight:600; font-size:0.9rem;">{member}</div><div style="font-size:0.75rem; color:{'#3b82f6' if is_active else '#a0aec0'};">{'● Next In Line' if is_active else 'Waiting'}</div></div></div>""", unsafe_allow_html=True)

    st.write("")
    # REVISION QUEUE
    st.markdown("<p style='font-size:0.8rem; color:#a0aec0; margin-bottom:5px; font-weight:600;'>REVISION QUEUE</p>", unsafe_allow_html=True)
    for i, member in enumerate(REVISION_ORDER):
        is_active = (i == rev_idx)
        initials = "".join([n[0] for n in member.split()[:2]])
        rev_color = "#f59e0b" if is_active else "#cbd5e1"
        st.markdown(f"""<div class="user-row {'active-user' if is_active else ''}"><div class="avatar" style="background:{rev_color};">{initials}</div><div style="flex-grow:1;"><div style="font-weight:600; font-size:0.9rem;">{member}</div><div style="font-size:0.75rem; color:{'#f59e0b' if is_active else '#a0aec0'};">{'● Next In Line' if is_active else 'Waiting'}</div></div></div>""", unsafe_allow_html=True)

    st.write("")
    if st.button("🔄 Sync System"): st.rerun()

# --- 5. MAIN CONTENT ---
st.markdown("""
<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
    <h1 style="margin:0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Write Wise Pro</h1>
    <span style="background:#d1fae5; color:#065f46; padding:5px 15px; border-radius:20px; font-weight:bold; font-size:0.8rem;">⚡ Online</span>
</div>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1: st.markdown(f"""<div class="glass-card" style="text-align:center; padding:15px;"><div style="font-size:2rem; font-weight:bold;">{len(df)}</div><div style="color:#718096; font-size:0.8rem;">TOTAL WORKFLOW</div></div>""", unsafe_allow_html=True)
with c2: 
    p_amt = df[df['Payment Status'] == 'Pending']['Amount'].sum() if not df.empty else 0
    st.markdown(f"""<div class="glass-card" style="text-align:center; padding:15px;"><div style="font-size:2rem; font-weight:bold; color:#ef4444;">{p_amt:,.0f}</div><div style="color:#718096; font-size:0.8rem;">PENDING (PKR)</div></div>""", unsafe_allow_html=True)
with c3: st.markdown(f"""<div class="glass-card" style="text-align:center; padding:15px;"><div style="font-size:2rem; font-weight:bold; color:#f59e0b;">{len(df[df["Type"] == "Revision"])}</div><div style="color:#718096; font-size:0.8rem;">REVISIONS</div></div>""", unsafe_allow_html=True)

col_left, col_right = st.columns([1, 1.8])
if 'f_key' not in st.session_state: st.session_state.f_key = 0

with col_left:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 🚀 Task Control")
    
    tab_assign, tab_update = st.tabs(["New Assignment", "Update / Payments"])
    
    with tab_assign:
        st.write("")
        u_file = st.file_uploader("Drop file here", key=f"k_{st.session_state.f_key}")
        t_type = st.radio("Cycle Type", ["New Task", "Revision"], horizontal=True)
        st.markdown("---")
        
        if t_type == "New Task":
            r1 = st.columns(2)
            work_cat = r1[0].selectbox("Category", ["Assignment", "Article"])
            pay_status = r1[1].selectbox("Payment", ["Pending", "Received"])
            amount = st.number_input("Amount (PKR)", step=100, value=0)
        else:
            st.info("ℹ️ Revisions are non-billable.")
            work_cat, pay_status, amount = "Revision", "N/A", 0
        
        nxt = NEW_TASK_ORDER[new_idx] if t_type == "New Task" else REVISION_ORDER[rev_idx]
        st.markdown(f"""<div class="hero-box"><p>NEXT ASSIGNMENT</p><h2>{nxt}</h2></div>""", unsafe_allow_html=True)
        
        if st.button("Confirm & Assign ➝"):
            if u_file:
                timestamp = datetime.now().strftime("%d-%b-%Y %H:%M")
                new_row = pd.DataFrame([{
                    "Task / File": u_file.name, "Type": t_type, "Assigned To": nxt,
                    "Time": timestamp, "Work Category": work_cat, "Amount": amount, "Payment Status": pay_status
                }])
                conn.update(data=pd.concat([df, new_row], ignore_index=True))
                st.session_state.f_key += 1
                st.toast("Assigned!", icon="✅")
                st.rerun()
            else: st.error("Attach file first.")

    with tab_update:
        st.write("")
        if not df.empty:
            # STRICT FILTER: ONLY 'New Task' (Case Sensitive & Trimmed)
            # This logic ensures Revisions are 100% excluded
            billable_df = df[df["Type"] == "New Task"].copy()
            
            if not billable_df.empty:
                # Reverse to show latest first
                billable_df = billable_df.iloc[::-1]
                
                # Mapping Display Name -> Real Index
                # Using a dictionary to keep track of the original row index
                task_map = {f"{r['Task / File']} ({r['Assigned To']})": i for i, r in billable_df.iterrows()}
                
                s_task = st.selectbox("Select Billable Task", list(task_map.keys()))
                
                # Get the actual index in the main dataframe
                real_idx = task_map[s_task]
                
                st.markdown("#### Edit Details")
                action = st.radio("Action", ["Update Payment", "Replace File"], horizontal=True)
                
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
                
                elif action == "Replace File":
                    nf = st.file_uploader("New File", key="rep_doc")
                    if st.button("Replace File"):
                        if nf:
                            df.at[real_idx, "Task / File"] = nf.name
                            conn.update(data=df)
                            st.success("File Replaced!")
                            st.rerun()
            else:
                st.info("No billable tasks found.")
        else: st.info("No data.")
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 📋 Activity Logs")
    if not df.empty:
        disp_df = df.iloc[::-1].copy()
        st.dataframe(
            disp_df, hide_index=True, use_container_width=True, height=650,
            column_config={
                "Task / File": st.column_config.TextColumn("Document", width="medium"),
                "Type": st.column_config.TextColumn("Type", width="small"),
                "Amount": st.column_config.NumberColumn("PKR", format="%d"),
                "Payment Status": st.column_config.TextColumn("Status", width="small"),
                "Assigned To": st.column_config.TextColumn("User", width="medium"),
                "Time": st.column_config.TextColumn("Date", width="small"),
            }
        )
    else: st.info("Ready.")
    st.markdown('</div>', unsafe_allow_html=True)

import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="WriteWise Pro", layout="centered", page_icon="✨")

# --- 2. ULTRA MODERN CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    
    /* Global Settings */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        background-color: #f1f5f9; /* Slate 100 */
        color: #1e293b;
    }
    
    /* Hide Default Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding-top: 1.5rem; padding-bottom: 3rem;}

    /* Modern Cards */
    div[data-testid="stVerticalBlock"] > div[style*="background-color"] {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        padding: 20px;
    }

    /* Custom Metrics Card (Top Right) */
    .metric-card {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        padding: 15px 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
        text-align: center;
    }
    .metric-label { font-size: 0.85rem; opacity: 0.9; font-weight: 500; }
    .metric-value { font-size: 1.8rem; font-weight: 700; }

    /* Buttons */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        border: none;
        transition: all 0.2s ease;
    }
    /* Primary Button Styling */
    div[data-testid="stForm"] .stButton > button, 
    button[kind="primary"] {
        background: #0f172a;
        color: white;
        box-shadow: 0 4px 6px rgba(15, 23, 42, 0.15);
    }
    div[data-testid="stForm"] .stButton > button:hover {
        transform: translateY(-2px);
    }

    /* Assign Badges */
    .user-badge {
        display: flex;
        align-items: center;
        gap: 10px;
        background-color: #f0f9ff;
        border: 1px solid #bae6fd;
        padding: 12px;
        border-radius: 12px;
        color: #0369a1;
        font-weight: 600;
        margin-bottom: 20px;
    }
    .rev-badge {
        background-color: #fff7ed;
        border: 1px solid #fed7aa;
        color: #c2410c;
    }

    /* Input Fields */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        border-radius: 8px;
        border: 1px solid #cbd5e1;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. DATA LOGIC ---
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
    except: return pd.DataFrame(columns=req)

df = get_data()

# Auto-Assign Logic
new_idx = len(df[df["Type"] == "New Task"]) % 3
rev_idx = len(df[df["Type"] == "Revision"]) % 3
current_writer_new = NEW_TASK_ORDER[new_idx]
current_writer_rev = REVISION_ORDER[rev_idx]

# --- 4. HEADER SECTION ---
col_head, col_metric = st.columns([1.8, 1])

with col_head:
    st.markdown("<h1 style='margin-bottom:0; color:#0f172a;'>WriteWise</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748b; font-size:1rem;'>Professional Task Management</p>", unsafe_allow_html=True)

with col_metric:
    if not df.empty:
        pending = df[df['Payment Status'] == 'Pending']['Amount'].sum()
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Pending Payments</div>
                <div class="metric-value">PKR {pending/1000:.1f}k</div>
            </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# --- 5. MODERN TABS ---
tab_assign, tab_db, tab_stats = st.tabs(["⚡ Assignment", "📂 Database", "📈 Analytics"])

# --- TAB 1: ASSIGN ---
with tab_assign:
    # Action Selector (Pills)
    task_mode = st.radio("Select Mode", ["New Task", "Revision"], horizontal=True, label_visibility="collapsed")
    
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True) # Spacer

    with st.container(border=True):
        if task_mode == "New Task":
            st.markdown(f"""
                <div class="user-badge">
                    <span style="font-size:1.2rem">👤</span> 
                    <span>Assigning to: <b>{current_writer_new}</b></span>
                </div>
            """, unsafe_allow_html=True)
            
            u_file = st.file_uploader("Upload Assignment File", key="n_file")
            
            c1, c2 = st.columns(2)
            cat = c1.selectbox("Work Category", ["Assignment", "Article"], key="cat")
            priority = c2.select_slider("Priority Level", options=["Normal", "High"], value="Normal")
            
            c3, c4 = st.columns(2)
            pay_status = c3.selectbox("Payment Status", ["Pending", "Received"], key="pay")
            amount = c4.number_input("Amount (PKR)", step=100, value=0)
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Confirm & Assign", type="primary", use_container_width=True):
                if u_file:
                    ts = datetime.now().strftime("%d-%b-%Y %H:%M")
                    new_row = pd.DataFrame([{
                        "Task / File": u_file.name, "Type": "New Task", "Assigned To": current_writer_new,
                        "Time": ts, "Work Category": cat, "Amount": amount, 
                        "Payment Status": pay_status, "Priority": priority
                    }])
                    conn.update(data=pd.concat([df, new_row], ignore_index=True))
                    st.cache_data.clear()
                    st.toast(f"Success! Assigned to {current_writer_new}", icon="🎉")
                    st.rerun()
                else:
                    st.error("⚠️ Please upload a file first.")

        else: # Revision
            st.markdown(f"""
                <div class="user-badge rev-badge">
                    <span style="font-size:1.2rem">↺</span> 
                    <span>Revision for: <b>{current_writer_rev}</b></span>
                </div>
            """, unsafe_allow_html=True)
            
            r_file = st.file_uploader("Upload Revision File", key="r_file")
            st.caption("ℹ️ Revisions are tracked for records but count as 0 billable amount.")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Send Revision", type="primary", use_container_width=True):
                if r_file:
                    ts = datetime.now().strftime("%d-%b-%Y %H:%M")
                    new_row = pd.DataFrame([{
                        "Task / File": r_file.name, "Type": "Revision", "Assigned To": current_writer_rev,
                        "Time": ts, "Work Category": "Revision", "Amount": 0, 
                        "Payment Status": "N/A", "Priority": "Normal"
                    }])
                    conn.update(data=pd.concat([df, new_row], ignore_index=True))
                    st.cache_data.clear()
                    st.toast(f"Revision Sent to {current_writer_rev}", icon="🚀")
                    st.rerun()
                else:
                    st.error("⚠️ Please upload a file first.")

# --- TAB 2: DATABASE ---
with tab_db:
    c_search, c_refresh = st.columns([4, 1])
    with c_search:
        search = st.text_input("🔍 Search Database", placeholder="Type filename or writer name...")
    with c_refresh:
        st.write("") # Spacer
        st.write("") 
        if st.button("🔄", help="Refresh Data"):
            st.cache_data.clear()
            st.rerun()

    if not df.empty:
        view_df = df.iloc[::-1].copy()
        if search:
            view_df = view_df[
                view_df['Task / File'].str.contains(search, case=False) | 
                view_df['Assigned To'].str.contains(search, case=False)
            ]
        
        st.dataframe(
            view_df, height=350, use_container_width=True, hide_index=True,
            column_order=["Task / File", "Type", "Assigned To", "Amount", "Payment Status"],
            column_config={
                "Amount": st.column_config.NumberColumn("PKR", format="%d"),
                "Payment Status": st.column_config.TextColumn("Status")
            }
        )
        
        st.markdown("### ⚙️ Management Console")
        with st.container(border=True):
            all_tasks = df.iloc[::-1]
            if not all_tasks.empty:
                t_map = {f"{r['Type']} - {r['Task / File']} ({r['Assigned To']})": i for i, r in all_tasks.iterrows()}
                sel_task = st.selectbox("Select Task to Edit/Delete", list(t_map.keys()))
                idx = t_map[sel_task]
                
                c_edit1, c_edit2 = st.columns(2)
                e_amt = c_edit1.number_input("Update Amount", value=int(df.at[idx, "Amount"]))
                
                cur_stat = df.at[idx, "Payment Status"]
                opts = ["Pending", "Received", "N/A"]
                s_idx = opts.index(cur_stat) if cur_stat in opts else 0
                e_stat = c_edit2.selectbox("Update Status", opts, index=s_idx)
                
                if st.button("💾 Save Changes", use_container_width=True):
                    df.at[idx, "Amount"] = e_amt
                    df.at[idx, "Payment Status"] = e_stat
                    conn.update(data=df)
                    st.cache_data.clear()
                    st.success("Record Updated Successfully!")
                    st.rerun()

                st.markdown("---")
                
                # Delete Zone
                with st.form("delete_form"):
                    st.markdown("**⚠️ Danger Zone**")
                    c_del1, c_del2 = st.columns([2, 1])
                    del_pass = c_del1.text_input("Admin Password", type="password", placeholder="Enter key to delete")
                    
                    st.write("") # Alignment fix
                    if c_del2.form_submit_button("🗑️ Delete Task", type="primary"):
                        if del_pass == "1234":
                            df = df.drop(idx)
                            conn.update(data=df)
                            st.cache_data.clear()
                            st.success("Task Deleted Permanently!")
                            st.rerun()
                        else:
                            st.error("❌ Incorrect Password")
            else:
                st.info("No records available.")
    else:
        st.info("Database is empty.")

# --- TAB 3: STATS ---
with tab_stats:
    st.markdown("### 🏆 Team Overview")
    if not df.empty:
        # Custom Grid Layout for Stats
        for writer in NEW_TASK_ORDER:
            n_count = len(df[(df['Assigned To'] == writer) & (df['Type'] == 'New Task')])
            r_count = len(df[(df['Assigned To'] == writer) & (df['Type'] == 'Revision')])
            
            # Using HTML for cleaner stat cards
            st.markdown(f"""
                <div style="background:white; padding:15px; border-radius:12px; border:1px solid #e2e8f0; margin-bottom:10px; display:flex; justify-content:space-between; align-items:center;">
                    <div style="font-weight:700; font-size:1.1rem; color:#0f172a;">{writer}</div>
                    <div style="display:flex; gap:20px;">
                        <div style="text-align:center;">
                            <div style="font-size:0.8rem; color:#64748b;">New</div>
                            <div style="font-weight:700; font-size:1.2rem; color:#2563eb;">{n_count}</div>
                        </div>
                        <div style="text-align:center;">
                            <div style="font-size:0.8rem; color:#64748b;">Rev</div>
                            <div style="font-weight:700; font-size:1.2rem; color:#ea580c;">{r_count}</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
    else:
        st.write("No data available.")

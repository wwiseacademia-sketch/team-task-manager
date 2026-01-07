import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="Write Wise Ultimate", layout="centered", page_icon="📱")

# --- 2. CSS STYLING ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #f8fafc; }
    .block-container { padding-top: 1rem; padding-bottom: 3rem; }
    .stContainer { background-color: white; border-radius: 12px; }
    div[data-testid="stMetricValue"] { font-size: 1.5rem; color: #0f172a; }
    .assign-badge { background-color: #e0f2fe; color: #0369a1; padding: 8px 12px; border-radius: 8px; font-weight: 600; text-align: center; margin-bottom: 15px; border: 1px solid #bae6fd; }
    .rev-badge { background-color: #ffedd5; color: #c2410c; padding: 8px 12px; border-radius: 8px; font-weight: 600; text-align: center; margin-bottom: 15px; border: 1px solid #fed7aa; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 3. DATA & LOGIC ---
MEMBERS_LIST = ["Muhammad Imran", "Mazhar Abbas", "Muhammad Ahmad"]
NEW_TASK_ORDER = ["Muhammad Imran", "Mazhar Abbas", "Muhammad Ahmad"]
REVISION_ORDER = ["Muhammad Ahmad", "Mazhar Abbas", "Muhammad Imran"]

conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    req = ["Task / File", "Type", "Assigned To", "Time", "Work Category", "Amount", "Payment Status", "Priority", "Added By"]
    try:
        df = conn.read(ttl=0)
        for col in req:
            if col not in df.columns: df[col] = "" if col != "Amount" else 0
        df['Type'] = df['Type'].astype(str).str.strip()
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
        return df.dropna(how="all")
    except: return pd.DataFrame(columns=req)

df = get_data()

# Logic for Auto-Assign
new_idx = len(df[df["Type"] == "New Task"]) % 3
rev_idx = len(df[df["Type"] == "Revision"]) % 3
current_writer_new = NEW_TASK_ORDER[new_idx]
current_writer_rev = REVISION_ORDER[rev_idx]

# --- 4. HEADER ---
c1, c2 = st.columns([2, 1])
with c1:
    st.title("WriteWise")
    st.caption("🚀 Task Command Center")
with c2:
    if not df.empty:
        pending = df[df['Payment Status'] == 'Pending']['Amount'].sum()
        st.metric("Pending", f"{pending/1000:.1f}k", delta_color="inverse")

st.divider()

# --- 5. TABS ---
tab_assign, tab_db, tab_stats = st.tabs(["➕ Assign", "🗂️ History", "📊 Stats"])

# --- TAB 1: ASSIGN (Added By Feature Included) ---
with tab_assign:
    adder_name = st.selectbox("👤 Who is adding this?", MEMBERS_LIST, key="adder")
    task_mode = st.radio("Select Action", ["New Task", "Revision"], horizontal=True, label_visibility="collapsed")
    
    with st.container(border=True):
        if task_mode == "New Task":
            st.markdown(f'<div class="assign-badge">👉 Assigning to: {current_writer_new}</div>', unsafe_allow_html=True)
            u_file = st.file_uploader("Upload File", key="n_file")
            c_a, c_b = st.columns(2)
            cat = c_a.selectbox("Category", ["Assignment", "Article"], key="cat")
            priority = c_b.select_slider("Priority", options=["Normal", "High"], value="Normal")
            c_c, c_d = st.columns(2)
            pay_status = c_c.selectbox("Payment", ["Pending", "Received"], key="pay")
            amount = c_d.number_input("Amount (PKR)", step=100, value=0)
            
            if st.button("🚀 Confirm Assignment", type="primary", use_container_width=True):
                if u_file:
                    ts = datetime.now().strftime("%d-%b-%Y %H:%M")
                    new_row = pd.DataFrame([{
                        "Task / File": u_file.name, "Type": "New Task", "Assigned To": current_writer_new,
                        "Time": ts, "Work Category": cat, "Amount": amount, 
                        "Payment Status": pay_status, "Priority": priority,
                        "Added By": adder_name
                    }])
                    conn.update(data=pd.concat([df, new_row], ignore_index=True))
                    st.cache_data.clear()
                    st.toast(f"Assigned to {current_writer_new}!", icon="✅")
                    st.rerun()
                else:
                    st.error("⚠️ Please upload a file first.")
                    
        else: # Revision
            st.markdown(f'<div class="rev-badge">↺ Revision for: {current_writer_rev}</div>', unsafe_allow_html=True)
            r_file = st.file_uploader("Upload Revision File", key="r_file")
            
            if st.button("qh Send Revision", type="primary", use_container_width=True):
                if r_file:
                    ts = datetime.now().strftime("%d-%b-%Y %H:%M")
                    new_row = pd.DataFrame([{
                        "Task / File": r_file.name, "Type": "Revision", "Assigned To": current_writer_rev,
                        "Time": ts, "Work Category": "Revision", "Amount": 0, 
                        "Payment Status": "N/A", "Priority": "Normal",
                        "Added By": adder_name
                    }])
                    conn.update(data=pd.concat([df, new_row], ignore_index=True))
                    st.cache_data.clear()
                    st.toast(f"Revision sent to {current_writer_rev}!", icon="🟠")
                    st.rerun()
                else:
                    st.error("⚠️ Please upload a file first.")

# --- TAB 2: HISTORY (FIXED DELETE BUTTON) ---
with tab_db:
    st.markdown("### Recent Tasks")
    search = st.text_input("🔍 Search task...", placeholder="File, Writer or Adder")
    
    if not df.empty:
        view_df = df.iloc[::-1].copy()
        if search:
            view_df = view_df[
                view_df['Task / File'].str.contains(search, case=False) | 
                view_df['Assigned To'].str.contains(search, case=False) |
                view_df['Added By'].str.contains(search, case=False)
            ]
        
        st.dataframe(view_df, height=300, use_container_width=True, hide_index=True,
                     column_order=["Task / File", "Type", "Assigned To", "Added By", "Amount"],
                     column_config={"Amount": st.column_config.NumberColumn("PKR", format="%d")})
        
        with st.expander("⚙️ Edit / Delete Task"):
            all_tasks = df.iloc[::-1]
            if not all_tasks.empty:
                t_map = {f"{r['Type']} - {r['Task / File']} ({r['Assigned To']})": i for i, r in all_tasks.iterrows()}
                sel_task = st.selectbox("Select Task", list(t_map.keys()))
                idx = t_map[sel_task]
                
                # Update Amount/Status
                c1, c2 = st.columns(2)
                e_amt = c1.number_input("Amount", value=int(df.at[idx, "Amount"]))
                e_stat = c2.selectbox("Status", ["Pending", "Received", "N/A"], index=0)
                
                if st.button("Save Changes"):
                    df.at[idx, "Amount"] = e_amt
                    df.at[idx, "Payment Status"] = e_stat
                    conn.update(data=df)
                    st.cache_data.clear()
                    st.success("Updated!")
                    st.rerun()

                st.divider()
                st.markdown("**🗑️ Delete Zone**")
                
                # --- FIXED DELETE LOGIC USING FORM ---
                with st.form("delete_form"):
                    st.write(f"Deleting: **{sel_task}**")
                    del_pass = st.text_input("Enter Password (1234)", type="password")
                    del_submitted = st.form_submit_button("Confirm Delete", type="primary")
                    
                    if del_submitted:
                        if del_pass == "1234":
                            df = df.drop(idx)
                            conn.update(data=df)
                            st.cache_data.clear()
                            st.success("Task Deleted!")
                            st.rerun()
                        else:
                            st.error("❌ Wrong Password!")
            else:
                st.info("No tasks.")
    else:
        st.info("Database empty.")

# --- TAB 3: STATS ---
with tab_stats:
    st.markdown("### Team Performance")
    if not df.empty:
        for writer in NEW_TASK_ORDER:
            n_count = len(df[(df['Assigned To'] == writer) & (df['Type'] == 'New Task')])
            r_count = len(df[(df['Assigned To'] == writer) & (df['Type'] == 'Revision')])
            
            with st.container(border=True):
                st.markdown(f"**{writer}**")
                sc1, sc2 = st.columns(2)
                sc1.metric("New Tasks", n_count)
                sc2.metric("Revisions", r_count)
                
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

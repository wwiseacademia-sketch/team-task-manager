import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURATION ---
ADMIN_USER = "Zaheer Abbas"
MEMBERS = ["Muhammad Imran", "Mazhar Abbas", "Muhammad Ahmad"]

NEW_TASK_CYCLE = ["Muhammad Imran", "Mazhar Abbas", "Muhammad Ahmad", "Completed"]
REVISION_CYCLE = ["Muhammad Ahmad", "Mazhar Abbas", "Muhammad Imran", "Completed"]

# --- DATABASE SETUP ---
if 'tasks' not in st.session_state:
    st.session_state.tasks = []
if 'task_id_counter' not in st.session_state:
    st.session_state.task_id_counter = 101

# --- FUNCTIONS ---
def get_next_assignee(current_assignee, task_type):
    cycle = NEW_TASK_CYCLE if task_type == "New Task" else REVISION_CYCLE
    try:
        idx = cycle.index(current_assignee)
        if idx + 1 < len(cycle):
            return cycle[idx + 1]
    except ValueError:
        return cycle[0]
    return "Completed"

def create_new_task(title, task_type, file_name):
    first_assignee = NEW_TASK_CYCLE[0] if task_type == "New Task" else REVISION_CYCLE[0]
    new_task = {
        "ID": st.session_state.task_id_counter,
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Title": title,
        "Type": task_type,
        "File": file_name,
        "Current Assignee": first_assignee,
        "Status": "Pending"
    }
    st.session_state.tasks.append(new_task)
    st.session_state.task_id_counter += 1

# --- MODERN UI STYLING ---
st.set_page_config(page_title="TeamFlow", layout="wide", page_icon="🚀")

# Custom CSS for "Arena" like look
st.markdown("""
    <style>
    /* Global Styles */
    .stApp {
        background-color: #f4f6f9;
    }
    .main-header {
        font-family: 'Helvetica Neue', sans-serif;
        color: #1E293B;
        font-weight: 700;
    }
    /* Card Style */
    .css-1r6slb0 {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    /* Button Styling */
    div.stButton > button {
        background-color: #2563EB;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 24px;
        font-weight: 600;
    }
    div.stButton > button:hover {
        background-color: #1D4ED8;
    }
    /* Success Message */
    .success-box {
        padding: 15px;
        background-color: #D1FAE5;
        color: #065F46;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("🚀 TeamFlow")
st.sidebar.markdown("---")
st.sidebar.subheader("👤 User Login")
user_role = st.sidebar.radio("Select Role", ["Admin", "Team Member"])

current_user = None
if user_role == "Admin":
    current_user = ADMIN_USER
    st.sidebar.success(f"👨‍💼 Admin: {ADMIN_USER}")
else:
    current_user = st.sidebar.selectbox("Select Member", MEMBERS)
    st.sidebar.info(f"👨‍💻 Member: {current_user}")

# --- MAIN DASHBOARD HEADER ---
st.markdown(f"<h1 class='main-header'>Dashboard // {current_user}</h1>", unsafe_allow_html=True)
st.markdown("---")

# ================= ADMIN DASHBOARD =================
if current_user == ADMIN_USER:
    
    # Stats Row
    col1, col2, col3 = st.columns(3)
    total_tasks = len(st.session_state.tasks)
    pending_tasks = len([t for t in st.session_state.tasks if t['Status'] != 'Completed'])
    completed_tasks = total_tasks - pending_tasks
    
    col1.metric("Total Tasks", total_tasks)
    col2.metric("In Progress", pending_tasks)
    col3.metric("Completed", completed_tasks)
    
    st.markdown("### 🛠 Control Panel")
    
    tab_new, tab_edit, tab_view = st.tabs(["✨ New Task", "🔧 Fix Mistakes", "📋 All Records"])
    
    with tab_new:
        with st.container():
            st.write("Create a new workflow cycle.")
            c1, c2 = st.columns([2, 1])
            with c1:
                t_title = st.text_input("Task Name")
            with c2:
                t_type = st.selectbox("Workflow Type", ["New Task", "Revision"])
            
            t_file = st.file_uploader("Attach File")
            
            if st.button("🚀 Launch Task"):
                if t_title and t_file:
                    create_new_task(t_title, t_type, t_file.name)
                    st.success(f"Task initiated! Assigned to: **{NEW_TASK_CYCLE[0] if t_type == 'New Task' else REVISION_CYCLE[0]}**")
                else:
                    st.error("Please fill all details.")

    with tab_edit:
        st.info("Use this if you uploaded the wrong file. The task will remain with the current user.")
        active_ids = [t['ID'] for t in st.session_state.tasks if t['Status'] != 'Completed']
        
        if active_ids:
            sel_id = st.selectbox("Select Task ID", active_ids)
            idx = next((i for i, item in enumerate(st.session_state.tasks) if item["ID"] == sel_id), None)
            
            if idx is not None:
                task = st.session_state.tasks[idx]
                st.markdown(f"**Task:** {task['Title']} | **Current File:** `{task['File']}`")
                new_f = st.file_uploader("Upload Correct File")
                if st.button("Update File"):
                    if new_f:
                        st.session_state.tasks[idx]['File'] = new_f.name
                        st.success("File updated!")
                        st.rerun()
        else:
            st.write("No active tasks to edit.")

    with tab_view:
        if st.session_state.tasks:
            st.dataframe(pd.DataFrame(st.session_state.tasks), use_container_width=True)
        else:
            st.write("No data found.")

# ================= MEMBER DASHBOARD =================
else:
    my_tasks = [t for t in st.session_state.tasks if t["Current Assignee"] == current_user and t["Status"] != "Completed"]
    
    if not my_tasks:
        st.markdown("""
        <div style="text-align: center; padding: 50px; background: white; border-radius: 10px;">
            <h2>🎉 All Caught Up!</h2>
            <p>You have no pending tasks at the moment.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.subheader("⚡ Your Action Items")
        
        for task in my_tasks:
            # Card Layout
            with st.container():
                st.markdown(f"""
                <div style="background-color: white; padding: 20px; border-radius: 12px; border-left: 5px solid #2563EB; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 20px;">
                    <h3 style="margin:0; color: #1E293B;">{task['Title']}</h3>
                    <p style="color: #64748B; font-size: 14px;">Task ID: #{task['ID']} | Type: <span style="background:#E0F2FE; color:#0284C7; padding:2px 8px; border-radius:4px;">{task['Type']}</span></p>
                    <hr style="margin: 10px 0; border-top: 1px solid #F1F5F9;">
                    <p><strong>📂 File to Process:</strong> {task['File']}</p>
                    <p style="font-size: 12px; color: #94A3B8;">Received: {task['Date']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                next_person = get_next_assignee(current_user, task["Type"])
                
                col_btn, col_empty = st.columns([1, 4])
                with col_btn:
                    btn_text = "✅ Complete & Finish" if next_person == "Completed" else f"📤 Send to {next_person}"
                    if st.button(btn_text, key=task['ID']):
                        t_idx = st.session_state.tasks.index(task)
                        if next_person == "Completed":
                            st.session_state.tasks[t_idx]['Status'] = "Completed"
                            st.session_state.tasks[t_idx]['Current Assignee'] = "Completed"
                            st.balloons()
                        else:
                            st.session_state.tasks[t_idx]['Current Assignee'] = next_person
                        st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("© 2024 Task Manager System")

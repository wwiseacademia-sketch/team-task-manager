import streamlit as st
import pandas as pd
from datetime import datetime

# --- SETUP PAGE & CSS ---
st.set_page_config(page_title="Write Wise Task Distributor", layout="wide", page_icon="📝")

# Custom CSS to match the Screenshot Design
st.markdown("""
    <style>
    /* Main Background */
    .stApp { background-color: #f4f7f6; }
    
    /* Card Design */
    .css-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    
    /* Headings */
    h1 { color: #3b3bff; text-align: center; font-family: sans-serif; font-weight: 800; font-size: 2rem;}
    .sub-head { text-align: center; color: #666; font-size: 1rem; margin-top: -10px; margin-bottom: 30px;}
    
    /* Assign Button */
    div.stButton > button {
        background-color: #4f46e5; /* Purple/Blue */
        color: white;
        width: 100%;
        border-radius: 10px;
        padding: 10px;
        font-weight: bold;
        border: none;
    }
    div.stButton > button:hover { background-color: #4338ca; }
    
    /* Next Assignee Box */
    .next-assignee-box {
        background-color: #f0f9ff;
        border: 1px solid #bae6fd;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin-top: 10px;
        margin-bottom: 10px;
    }
    .assignee-name {
        color: #0284c7; /* Blue Text */
        font-size: 1.2rem;
        font-weight: bold;
    }
    
    /* Badges */
    .badge-new { background-color: #dcfce7; color: #166534; padding: 4px 8px; border-radius: 5px; font-size: 0.8rem; font-weight: bold;}
    .badge-rev { background-color: #ffedd5; color: #9a3412; padding: 4px 8px; border-radius: 5px; font-size: 0.8rem; font-weight: bold;}
    </style>
""", unsafe_allow_html=True)

# --- CONFIGURATION ---
NEW_TASK_ORDER = ["Muhammad Imran", "Mazhar Abbas", "Muhammad Ahmad"]
REVISION_ORDER = ["Muhammad Ahmad", "Mazhar Abbas", "Muhammad Imran"]

# --- SESSION STATE (Database) ---
if 'log' not in st.session_state:
    st.session_state.log = []

# Track whose turn it is (Index 0, 1, or 2)
if 'new_task_idx' not in st.session_state:
    st.session_state.new_task_idx = 0 
if 'rev_task_idx' not in st.session_state:
    st.session_state.rev_task_idx = 0

# --- HEADER ---
st.markdown("<h1>📝 Write Wise Task Distributor</h1>", unsafe_allow_html=True)
st.markdown("<div class='sub-head'>Admin/Generator: <span style='color:#4f46e5; font-weight:bold;'>Zaheer Abbas</span></div>", unsafe_allow_html=True)

# --- LAYOUT (2 Columns) ---
left_col, right_col = st.columns([1, 2.2])

# ================= LEFT COLUMN: CONTROLS =================
with left_col:
    # --- CARD 1: ASSIGN WORK ---
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    st.markdown("### 📤 Assign Work")
    
    # 1. File Upload
    uploaded_file = st.file_uploader("Upload File (Task/Revision)", label_visibility="collapsed")
    if uploaded_file:
        st.success(f"File selected: {uploaded_file.name}")
    else:
        st.info("Click to upload file")

    # 2. Task Type
    task_type = st.selectbox("Task Type", ["New Task", "Revision"])

    # 3. Calculate Next Assignee (Visual Only)
    if task_type == "New Task":
        next_person = NEW_TASK_ORDER[st.session_state.new_task_idx]
        next_idx = st.session_state.new_task_idx
        order_list = NEW_TASK_ORDER
    else:
        next_person = REVISION_ORDER[st.session_state.rev_task_idx]
        next_idx = st.session_state.rev_task_idx
        order_list = REVISION_ORDER

    # Show who is next
    st.markdown(f"""
        <div class="next-assignee-box">
            <div style="font-size:0.8rem; color:#666; text-transform:uppercase; letter-spacing:1px;">Next Assignee</div>
            <div class="assignee-name">{next_person}</div>
        </div>
    """, unsafe_allow_html=True)

    # 4. Assign Button
    if st.button("🚀 Assign File"):
        if uploaded_file:
            # Add to Log
            new_entry = {
                "Task / File": uploaded_file.name,
                "Type": task_type,
                "Assigned To": next_person,
                "Time": datetime.now().strftime("%d/%m/%Y, %I:%M %p")
            }
            # Insert at the top (Index 0)
            st.session_state.log.insert(0, new_entry)
            
            # Update Turn (Cycle Logic)
            if task_type == "New Task":
                st.session_state.new_task_idx = (st.session_state.new_task_idx + 1) % 3
            else:
                st.session_state.rev_task_idx = (st.session_state.rev_task_idx + 1) % 3
            
            st.toast(f"Assigned to {next_person}!", icon="✅")
            st.rerun()
        else:
            st.error("Please upload a file first.")
            
    st.markdown('</div>', unsafe_allow_html=True) # End Card 1

    # --- CARD 2: CYCLE STATUS ---
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    st.markdown("#### Cycle Status")
    
    # Visualizing the New Task Cycle
    st.caption("New Task Cycle (Round Robin)")
    new_html = ""
    for i, member in enumerate(NEW_TASK_ORDER):
        color = "#dcfce7" if i == st.session_state.new_task_idx else "#f3f4f6"
        border = "2px solid #22c55e" if i == st.session_state.new_task_idx else "1px solid #e5e7eb"
        text_w = "bold" if i == st.session_state.new_task_idx else "normal"
        new_html += f"<span style='background:{color}; border:{border}; padding:5px; border-radius:5px; font-weight:{text_w}; margin-right:5px; font-size:0.8rem'>{member.split(' ')[-1]}</span>"
        if i < 2: new_html += " → "
    st.markdown(new_html, unsafe_allow_html=True)

    st.write("") # Spacer

    # Visualizing the Revision Cycle
    st.caption("Revision Cycle")
    rev_html = ""
    for i, member in enumerate(REVISION_ORDER):
        color = "#ffedd5" if i == st.session_state.rev_task_idx else "#f3f4f6"
        border = "2px solid #f97316" if i == st.session_state.rev_task_idx else "1px solid #e5e7eb"
        text_w = "bold" if i == st.session_state.rev_task_idx else "normal"
        rev_html += f"<span style='background:{color}; border:{border}; padding:5px; border-radius:5px; font-weight:{text_w}; margin-right:5px; font-size:0.8rem'>{member.split(' ')[-1]}</span>"
        if i < 2: rev_html += " → "
    st.markdown(rev_html, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True) # End Card 2


# ================= RIGHT COLUMN: LOG =================
with right_col:
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    
    # Header row with Reset button
    c1, c2 = st.columns([4, 1])
    c1.markdown("### 📋 Assignment Log")
    if c2.button("Reset All", type="secondary"):
        st.session_state.log = []
        st.session_state.new_task_idx = 0
        st.session_state.rev_task_idx = 0
        st.rerun()

    # Display Table
    if st.session_state.log:
        df = pd.DataFrame(st.session_state.log)
        
        # Adding ID column (1, 2, 3...) based on current list length
        df.insert(0, "#", range(len(df), 0, -1))

        # We use Styler to highlight columns logic
        def highlight_type(val):
            if val == "New Task": return 'background-color: #dcfce7; color: #166534; font-weight: bold; border-radius:5px;'
            return 'background-color: #ffedd5; color: #9a3412; font-weight: bold; border-radius:5px;'

        # Using Streamlit Dataframe with Column Config for cleaner look
        st.dataframe(
            df,
            hide_index=True,
            use_container_width=True,
            column_config={
                "#": st.column_config.NumberColumn(width="small"),
                "Task / File": st.column_config.TextColumn(width="large"),
                "Type": st.column_config.TextColumn(width="medium"),
                "Assigned To": st.column_config.TextColumn(width="medium"),
                "Time": st.column_config.TextColumn(width="medium"),
            }
        )
    else:
        st.info("No files assigned yet. Upload a file to start.")
        
    st.markdown('</div>', unsafe_allow_html=True) # End Card 3

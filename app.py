import streamlit as st
import pandas as pd
from datetime import datetime

# --- SETUP PAGE & CSS ---
st.set_page_config(page_title="Write Wise Task Distributor", layout="wide", page_icon="📝")

# Custom CSS for Professional Look
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
    
    /* Buttons */
    div.stButton > button {
        width: 100%;
        border-radius: 10px;
        font-weight: bold;
        border: none;
        padding: 10px;
    }
    /* Assign Button Color */
    .stButton button { background-color: #4f46e5; color: white; }
    .stButton button:hover { background-color: #4338ca; }
    
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
    
    /* Fix Mistake Area */
    .fix-box {
        border: 1px dashed #ef4444;
        background-color: #fef2f2;
        padding: 15px;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- CONFIGURATION ---
NEW_TASK_ORDER = ["Muhammad Imran", "Mazhar Abbas", "Muhammad Ahmad"]
REVISION_ORDER = ["Muhammad Ahmad", "Mazhar Abbas", "Muhammad Imran"]

# --- SESSION STATE (Database) ---
if 'log' not in st.session_state:
    st.session_state.log = []

# Track whose turn it is
if 'new_task_idx' not in st.session_state:
    st.session_state.new_task_idx = 0 
if 'rev_task_idx' not in st.session_state:
    st.session_state.rev_task_idx = 0

# --- HEADER ---
st.markdown("<h1>📝 Write Wise Task Distributor</h1>", unsafe_allow_html=True)
st.markdown("<div class='sub-head'>Admin/Generator: <span style='color:#4f46e5; font-weight:bold;'>Zaheer Abbas</span></div>", unsafe_allow_html=True)

# --- LAYOUT (2 Columns) ---
left_col, right_col = st.columns([1.2, 2])

# ================= LEFT COLUMN: CONTROLS =================
with left_col:
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    
    # TABS: Assign vs Fix Mistake
    tab1, tab2 = st.tabs(["📤 Assign Work", "✏️ Fix Mistake (Edit)"])
    
    # --- TAB 1: ASSIGN NEW WORK ---
    with tab1:
        st.write("") # Spacer
        uploaded_file = st.file_uploader("Upload File", label_visibility="collapsed")
        
        if uploaded_file:
            st.success(f"Selected: {uploaded_file.name}")
        else:
            st.info("Click to upload file")

        task_type = st.selectbox("Task Type", ["New Task", "Revision"])

        # Calculate Next Assignee
        if task_type == "New Task":
            next_person = NEW_TASK_ORDER[st.session_state.new_task_idx]
        else:
            next_person = REVISION_ORDER[st.session_state.rev_task_idx]

        st.markdown(f"""
            <div class="next-assignee-box">
                <div style="font-size:0.8rem; color:#666;">Next Assignee</div>
                <div class="assignee-name">{next_person}</div>
            </div>
        """, unsafe_allow_html=True)

        if st.button("🚀 Assign File"):
            if uploaded_file:
                new_entry = {
                    "Task / File": uploaded_file.name,
                    "Type": task_type,
                    "Assigned To": next_person,
                    "Time": datetime.now().strftime("%d/%m/%Y, %I:%M %p")
                }
                # Insert at top
                st.session_state.log.insert(0, new_entry)
                
                # Update Turn
                if task_type == "New Task":
                    st.session_state.new_task_idx = (st.session_state.new_task_idx + 1) % 3
                else:
                    st.session_state.rev_task_idx = (st.session_state.rev_task_idx + 1) % 3
                
                st.toast(f"Assigned to {next_person}!", icon="✅")
                st.rerun()
            else:
                st.error("Please upload a file first.")

    # --- TAB 2: EDIT / FIX MISTAKE ---
    with tab2:
        st.write("")
        st.markdown('<div class="fix-box">', unsafe_allow_html=True)
        st.write("**Edit Wrong File** (New Task or Revision)")
        
        if st.session_state.log:
            # Create a smart dropdown list showing TYPE
            task_options = []
            for i, entry in enumerate(st.session_state.log):
                # Format: #1 [Revision] Filename.docx -> Imran
                display_text = f"#{len(st.session_state.log)-i} [{entry['Type']}] {entry['Task / File']} ➝ {entry['Assigned To']}"
                task_options.append(display_text)
            
            selected_option = st.selectbox("Select Task to Fix", task_options)
            
            # Find the actual index in the list
            selected_index = task_options.index(selected_option)
            selected_task = st.session_state.log[selected_index]
            
            st.caption(f"Currently assigned to: **{selected_task['Assigned To']}**")
            
            # New File Uploader
            new_correct_file = st.file_uploader("Upload Correct File", key="fix_uploader")
            
            if st.button("💾 Update File Now"):
                if new_correct_file:
                    # Update the file name in the database
                    st.session_state.log[selected_index]['Task / File'] = new_correct_file.name
                    st.success("File updated successfully!")
                    st.rerun()
                else:
                    st.error("Please select the correct file to upload.")
        else:
            st.warning("No tasks available to edit yet.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True) # End Card 1

    # --- CARD 2: CYCLE STATUS (Visuals) ---
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    st.markdown("#### Cycle Status")
    
    st.caption("New Task Cycle")
    new_html = ""
    for i, member in enumerate(NEW_TASK_ORDER):
        color = "#dcfce7" if i == st.session_state.new_task_idx else "#f3f4f6"
        border = "2px solid #22c55e" if i == st.session_state.new_task_idx else "1px solid #e5e7eb"
        text_w = "bold" if i == st.session_state.new_task_idx else "normal"
        new_html += f"<span style='background:{color}; border:{border}; padding:4px; border-radius:5px; font-weight:{text_w}; margin-right:3px; font-size:0.75rem'>{member.split(' ')[-1]}</span>"
        if i < 2: new_html += " → "
    st.markdown(new_html, unsafe_allow_html=True)

    st.write("")
    st.caption("Revision Cycle")
    rev_html = ""
    for i, member in enumerate(REVISION_ORDER):
        color = "#ffedd5" if i == st.session_state.rev_task_idx else "#f3f4f6"
        border = "2px solid #f97316" if i == st.session_state.rev_task_idx else "1px solid #e5e7eb"
        text_w = "bold" if i == st.session_state.rev_task_idx else "normal"
        rev_html += f"<span style='background:{color}; border:{border}; padding:4px; border-radius:5px; font-weight:{text_w}; margin-right:3px; font-size:0.75rem'>{member.split(' ')[-1]}</span>"
        if i < 2: rev_html += " → "
    st.markdown(rev_html, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)


# ================= RIGHT COLUMN: LOG =================
with right_col:
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    
    c1, c2 = st.columns([4, 1])
    c1.markdown("### 📋 Assignment Log")
    if c2.button("Reset All", type="secondary"):
        st.session_state.log = []
        st.session_state.new_task_idx = 0
        st.session_state.rev_task_idx = 0
        st.rerun()

    if st.session_state.log:
        df = pd.DataFrame(st.session_state.log)
        df.insert(0, "#", range(len(df), 0, -1))

        st.dataframe(
            df,
            hide_index=True,
            use_container_width=True,
            column_config={
                "#": st.column_config.NumberColumn(width="small"),
                "Task / File": st.column_config.TextColumn(width="large"),
                "Type": st.column_config.TextColumn(width="small"),
                "Assigned To": st.column_config.TextColumn(width="medium"),
                "Time": st.column_config.TextColumn(width="medium"),
            }
        )
    else:
        st.info("Waiting for tasks...")
        
    st.markdown('</div>', unsafe_allow_html=True)

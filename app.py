import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- PAGE SETUP ---
st.set_page_config(page_title="Write Wise Task Distributor", layout="wide", page_icon="📝")

# --- CSS STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f6; }
    .css-card { background-color: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); margin-bottom: 20px; }
    h1 { color: #3b3bff; text-align: center; font-weight: 800; font-size: 2rem;}
    .sub-head { text-align: center; color: #666; font-size: 1rem; margin-bottom: 30px;}
    div.stButton > button { width: 100%; border-radius: 10px; font-weight: bold; border: none; padding: 10px; }
    .stButton button { background-color: #4f46e5; color: white; }
    .stButton button:hover { background-color: #4338ca; }
    .next-assignee-box { background-color: #f0f9ff; border: 1px solid #bae6fd; padding: 15px; border-radius: 10px; text-align: center; margin: 10px 0; }
    .assignee-name { color: #0284c7; font-size: 1.2rem; font-weight: bold; }
    .fix-box { border: 1px dashed #ef4444; background-color: #fef2f2; padding: 15px; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- MEMBERS ---
NEW_TASK_ORDER = ["Muhammad Imran", "Mazhar Abbas", "Muhammad Ahmad"]
REVISION_ORDER = ["Muhammad Ahmad", "Mazhar Abbas", "Muhammad Imran"]

# --- CONNECT TO GOOGLE SHEET ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    try:
        # Sheet se Data parho (No Cache = Fresh Data)
        df = conn.read(ttl=0)
        # Agar sheet khali ho to Columns khud bana do
        required_cols = ["Task / File", "Type", "Assigned To", "Time"]
        if df.empty or not all(col in df.columns for col in required_cols):
            return pd.DataFrame(columns=required_cols)
        return df.dropna(how="all")
    except Exception:
        return pd.DataFrame(columns=["Task / File", "Type", "Assigned To", "Time"])

# --- HEADER ---
st.markdown("<h1>📝 Write Wise Task Distributor</h1>", unsafe_allow_html=True)
st.markdown("<div class='sub-head'>Admin: <span style='color:#4f46e5; font-weight:bold;'>Zaheer Abbas</span> (Google Sheets Connected)</div>", unsafe_allow_html=True)

# --- LOAD DATA & CALCULATE TURN ---
df = get_data()

# Logic: Count karo k kitny tasks ho chukay hain, wahi agla number hoga
total_new = len(df[df["Type"] == "New Task"])
new_idx = total_new % 3

total_rev = len(df[df["Type"] == "Revision"])
rev_idx = total_rev % 3

# --- UI LAYOUT ---
left_col, right_col = st.columns([1.2, 2])
if 'file_key' not in st.session_state: st.session_state.file_key = 0

with left_col:
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["📤 Assign Work", "✏️ Fix Mistake"])
    
    # === TAB 1: ASSIGN ===
    with tab1:
        st.write("")
        uploaded_file = st.file_uploader("Upload File", key=f"up_{st.session_state.file_key}")
        
        if uploaded_file: st.success(f"Selected: {uploaded_file.name}")
        else: st.info("⚠️ Pehly File Upload karein")

        task_type = st.selectbox("Task Type", ["New Task", "Revision"])

        # Next Banda kon hai?
        if task_type == "New Task": next_person = NEW_TASK_ORDER[new_idx]
        else: next_person = REVISION_ORDER[rev_idx]

        st.markdown(f"""
            <div class="next-assignee-box">
                <div style="font-size:0.8rem; color:#666;">Next Assignee</div>
                <div class="assignee-name">{next_person}</div>
            </div>
        """, unsafe_allow_html=True)

        if st.button("🚀 Assign File"):
            if not uploaded_file:
                st.error("⛔ RUKAIN! File upload nahi hui. Task assign nahi hoga.")
            else:
                # Naya Data
                new_row = pd.DataFrame([{
                    "Task / File": uploaded_file.name,
                    "Type": task_type,
                    "Assigned To": next_person,
                    "Time": datetime.now().strftime("%d/%m/%Y, %I:%M %p")
                }])
                
                # Sheet update karo
                updated_df = pd.concat([df, new_row], ignore_index=True)
                conn.update(data=updated_df)
                
                # Reset
                st.session_state.file_key += 1
                st.toast(f"Saved! Assignee: {next_person}", icon="✅")
                st.rerun()

    # === TAB 2: FIX MISTAKE ===
    with tab2:
        st.write("")
        st.markdown('<div class="fix-box">', unsafe_allow_html=True)
        st.write("**Edit Wrong File**")
        
        if not df.empty:
            df_rev = df.iloc[::-1] # Show latest first
            options = []
            idx_map = {}
            for i, row in df_rev.iterrows():
                txt = f"#{i+1} [{row['Type']}] {row['Task / File']} ➝ {row['Assigned To']}"
                options.append(txt)
                idx_map[txt] = i
            
            sel = st.selectbox("Select Task", options)
            real_idx = idx_map[sel]
            
            new_f = st.file_uploader("Upload Correct File", key="fix")
            if st.button("💾 Update File Now"):
                if new_f:
                    df.at[real_idx, "Task / File"] = new_f.name
                    conn.update(data=df)
                    st.success("File Updated in Google Sheet!")
                    st.rerun()
                else: st.error("File to select karein.")
        else:
            st.warning("No Data found.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # === CYCLE DISPLAY ===
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    st.caption("New Task Cycle")
    h = ""
    for i, m in enumerate(NEW_TASK_ORDER):
        c = "#dcfce7" if i == new_idx else "#f3f4f6"
        b = "2px solid #22c55e" if i == new_idx else "1px solid #e5e7eb"
        h += f"<span style='background:{c}; border:{b}; padding:4px; border-radius:5px; margin-right:3px; font-size:0.75rem'>{m.split(' ')[-1]}</span>"
        if i < 2: h += " → "
    st.markdown(h, unsafe_allow_html=True)
    
    st.write("")
    st.caption("Revision Cycle")
    h2 = ""
    for i, m in enumerate(REVISION_ORDER):
        c = "#ffedd5" if i == rev_idx else "#f3f4f6"
        b = "2px solid #f97316" if i == rev_idx else "1px solid #e5e7eb"
        h2 += f"<span style='background:{c}; border:{b}; padding:4px; border-radius:5px; margin-right:3px; font-size:0.75rem'>{m.split(' ')[-1]}</span>"
        if i < 2: h2 += " → "
    st.markdown(h2, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with right_col:
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    c1, c2 = st.columns([4, 1])
    c1.markdown("### 📋 Assignment Log")
    if c2.button("Refresh"): st.rerun()

    if not df.empty:
        d_df = df.iloc[::-1].copy()
        d_df.insert(0, "#", range(len(df), 0, -1))
        st.dataframe(d_df, hide_index=True, use_container_width=True)
    else:
        st.info("No data in Google Sheet.")
    st.markdown('</div>', unsafe_allow_html=True)

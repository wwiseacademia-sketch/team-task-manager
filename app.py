import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="WriteWise Dashboard", 
    layout="wide", # WIDE MODE for Dashboard feel
    page_icon="⚡"
)

# --- 2. PREMIUM CSS STYLING ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    /* General Body */
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
        background-color: #f8f9fc;
        color: #1e293b;
    }
    
    /* Remove Top Padding */
    .block-container { padding-top: 1.5rem; padding-bottom: 3rem; }
    
    /* Hide Default Header/Footer */
    header, footer {visibility: hidden;}
    
    /* DASHBOARD CARDS */
    .dash-card {
        background: white;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
        border: 1px solid #f1f5f9;
        transition: transform 0.2s;
    }
    .dash-card:hover { transform: translateY(-2px); }
    
    /* TOTAL PENDING WIDGET (Gradient) */
    .money-card {
        background: linear-gradient(135deg, #0f172a 0%, #334155 100%);
        color: white;
        border-radius: 16px;
        padding: 25px;
        box-shadow: 0 10px 25px rgba(15, 23, 42, 0.2);
        text-align: right;
    }
    .money-label { font-size: 0.9rem; opacity: 0.8; font-weight: 500; letter-spacing: 0.5px; }
    .money-value { font-size: 2.2rem; font-weight: 700; margin-top: 5px; }
    
    /* WRITER ASSIGNMENT BADGE */
    .assign-box {
        background: #eff6ff;
        border-left: 5px solid #3b82f6;
        padding: 15px 20px;
        border-radius: 8px;
        color: #1e3a8a;
        font-weight: 600;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .rev-box {
        background: #fff7ed;
        border-left: 5px solid #f97316;
        padding: 15px 20px;
        border-radius: 8px;
        color: #7c2d12;
        font-weight: 600;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    /* CUSTOM BUTTONS */
    div.stButton > button {
        border-radius: 8px;
        font-weight: 600;
        height: 45px;
        border: none;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    /* Primary Action Button */
    button[kind="primary"] {
        background: linear-gradient(to right, #2563eb, #1d4ed8);
        color: white;
    }
    
    /* TABS Styling */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: white;
        border-radius: 8px 8px 0 0;
        border: 1px solid #e2e8f0;
        border-bottom: none;
        padding: 0 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #fff;
        border-top: 3px solid #2563eb;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. BACKEND LOGIC ---
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

# Auto-Assign Calculation
new_idx = len(df[df["Type"] == "New Task"]) % 3
rev_idx = len(df[df["Type"] == "Revision"]) % 3
current_writer_new = NEW_TASK_ORDER[new_idx]
current_writer_rev = REVISION_ORDER[rev_idx]

# --- 4. TOP DASHBOARD SECTION ---
col_brand, col_stats = st.columns([2, 1])

with col_brand:
    st.markdown("## WriteWise <span style='color:#3b82f6'>Pro</span>", unsafe_allow_html=True)
    st.markdown("**Team Management System** | `v2.0`")

with col_stats:
    if not df.empty:
        pending = df[df['Payment Status'] == 'Pending']['Amount'].sum()
        st.markdown(f"""
        <div class="money-card">
            <div class="money-label">PENDING PAYMENTS</div>
            <div class="money-value">PKR {pending:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

st.write("") # Spacer

# --- 5. MAIN NAVIGATION ---
t_assign, t_dash, t_manage = st.tabs(["🚀 Assignment", "📊 Analytics", "📂 Manage Data"])

# --- TAB 1: ASSIGNMENT ---
with t_assign:
    c_form, c_info = st.columns([2, 1]) # Split layout
    
    with c_form:
        with st.container(border=True):
            st.markdown("### 📝 New Entry")
            mode = st.radio("Type", ["New Task", "Revision"], horizontal=True, label_visibility="collapsed")
            
            if mode == "New Task":
                st.markdown(f"""
                <div class="assign-box">
                    <span>NEXT WRITER:</span>
                    <span style="font-size:1.1rem; text-decoration:underline;">{current_writer_new}</span>
                </div>
                """, unsafe_allow_html=True)
                
                u_file = st.file_uploader("Upload File", key="n_file")
                col1, col2 = st.columns(2)
                cat = col1.selectbox("Category", ["Assignment", "Article"], key="cat")
                priority = col2.select_slider("Priority", ["Normal", "High"], value="Normal")
                
                col3, col4 = st.columns(2)
                pay_status = col3.selectbox("Payment", ["Pending", "Received"], key="pay")
                amount = col4.number_input("PKR Amount", step=500, value=0)
                
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Confirm Assignment", type="primary", use_container_width=True):
                    if u_file:
                        ts = datetime.now().strftime("%d-%b-%Y %H:%M")
                        new_row = pd.DataFrame([{
                            "Task / File": u_file.name, "Type": "New Task", "Assigned To": current_writer_new,
                            "Time": ts, "Work Category": cat, "Amount": amount, 
                            "Payment Status": pay_status, "Priority": priority
                        }])
                        conn.update(data=pd.concat([df, new_row], ignore_index=True))
                        st.cache_data.clear()
                        st.success(f"Task Assigned to {current_writer_new}!")
                        st.rerun()
                    else:
                        st.error("⚠️ Upload file first")

            else: # Revision
                st.markdown(f"""
                <div class="rev-box">
                    <span>REVISION FOR:</span>
                    <span style="font-size:1.1rem; text-decoration:underline;">{current_writer_rev}</span>
                </div>
                """, unsafe_allow_html=True)
                
                r_file = st.file_uploader("Upload Revision", key="r_file")
                st.info("Revisions are non-billable.")
                
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
                        st.success(f"Revision sent to {current_writer_rev}!")
                        st.rerun()
                    else:
                        st.error("⚠️ Upload file first")

    # Side Info Panel
    with c_info:
        st.markdown("### 💡 Quick Tips")
        st.info("**New Task Order:**\nImran → Mazhar → Ahmad")
        st.warning("**Revision Order:**\nAhmad → Mazhar → Imran")
        st.caption("Auto-sync is enabled.")

# --- TAB 2: ANALYTICS (DASHBOARD) ---
with t_dash:
    if not df.empty:
        st.markdown("### 📈 Performance Overview")
        
        # Prepare Data for Chart
        chart_data = df.groupby(['Assigned To', 'Type']).size().reset_index(name='Count')
        
        # ALTAIR BAR CHART (Professional Look)
        chart = alt.Chart(chart_data).mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5).encode(
            x=alt.X('Assigned To', axis=alt.Axis(labelAngle=0)),
            y=alt.Y('Count'),
            color=alt.Color('Type', scale=alt.Scale(domain=['New Task', 'Revision'], range=['#3b82f6', '#f97316'])),
            tooltip=['Assigned To', 'Type', 'Count']
        ).properties(
            height=350
        ).configure_axis(
            grid=False,
            labelFontSize=12,
            titleFontSize=14
        ).configure_view(
            strokeWidth=0
        )
        
        st.altair_chart(chart, use_container_width=True)
        
        # Detailed Grid
        st.markdown("### 🔢 Detailed Breakdown")
        c_d1, c_d2, c_d3 = st.columns(3)
        cols = [c_d1, c_d2, c_d3]
        
        for i, writer in enumerate(NEW_TASK_ORDER):
            n_count = len(df[(df['Assigned To'] == writer) & (df['Type'] == 'New Task')])
            r_count = len(df[(df['Assigned To'] == writer) & (df['Type'] == 'Revision')])
            
            with cols[i]:
                st.markdown(f"""
                <div class="dash-card">
                    <h4 style="margin:0; color:#1e293b;">{writer}</h4>
                    <hr style="margin:10px 0; border-top:1px solid #f1f5f9;">
                    <div style="display:flex; justify-content:space-between;">
                        <span style="color:#64748b;">New Tasks</span>
                        <b style="color:#3b82f6;">{n_count}</b>
                    </div>
                    <div style="display:flex; justify-content:space-between; margin-top:5px;">
                        <span style="color:#64748b;">Revisions</span>
                        <b style="color:#f97316;">{r_count}</b>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
    else:
        st.info("No data available for analytics.")
        
    if st.button("🔄 Refresh Analytics"):
        st.cache_data.clear()
        st.rerun()

# --- TAB 3: MANAGE DATA ---
with t_manage:
    st.markdown("### 🗂️ Database Records")
    
    # Search Bar
    c_s, c_b = st.columns([3, 1])
    search = c_s.text_input("Search Records", placeholder="Enter filename or writer...")
    
    if not df.empty:
        view_df = df.iloc[::-1].copy()
        if search:
            view_df = view_df[
                view_df['Task / File'].str.contains(search, case=False) | 
                view_df['Assigned To'].str.contains(search, case=False)
            ]
        
        st.dataframe(
            view_df, 
            height=300, 
            use_container_width=True, 
            hide_index=True,
            column_order=["Task / File", "Type", "Assigned To", "Amount", "Payment Status"],
            column_config={
                "Amount": st.column_config.NumberColumn("PKR", format="%d"),
                "Payment Status": st.column_config.TextColumn("Status", help="Current payment state")
            }
        )
        
        # EDIT / DELETE PANEL
        st.markdown("<br>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("#### 🛠️ Modification Panel")
            
            all_tasks = df.iloc[::-1]
            if not all_tasks.empty:
                t_map = {f"{r['Type']} | {r['Task / File']} ({r['Assigned To']})": i for i, r in all_tasks.iterrows()}
                sel_task = st.selectbox("Select Record", list(t_map.keys()))
                idx = t_map[sel_task]
                
                ec1, ec2 = st.columns(2)
                e_amt = ec1.number_input("Edit Amount", value=int(df.at[idx, "Amount"]))
                
                cur_stat = df.at[idx, "Payment Status"]
                opts = ["Pending", "Received", "N/A"]
                s_idx = opts.index(cur_stat) if cur_stat in opts else 0
                e_stat = ec2.selectbox("Edit Status", opts, index=s_idx)
                
                if st.button("Save Changes"):
                    df.at[idx, "Amount"] = e_amt
                    df.at[idx, "Payment Status"] = e_stat
                    conn.update(data=df)
                    st.cache_data.clear()
                    st.success("Record updated.")
                    st.rerun()
                
                st.divider()
                
                # Delete Section
                with st.form("del_form"):
                    st.markdown("**🗑️ Delete Record**")
                    col_p, col_btn = st.columns([3, 1])
                    d_pass = col_p.text_input("Admin Password", type="password", label_visibility="collapsed", placeholder="Enter Password")
                    
                    if col_btn.form_submit_button("Delete Permanently", type="primary"):
                        if d_pass == "1234":
                            df = df.drop(idx)
                            conn.update(data=df)
                            st.cache_data.clear()
                            st.success("Deleted successfully!")
                            st.rerun()
                        else:
                            st.error("Incorrect Password")
            else:
                st.write("No tasks found.")
    else:
        st.write("Database is empty.")

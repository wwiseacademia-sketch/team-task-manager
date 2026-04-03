# ---------------------------------
# WriteWise Pro - v2.0 (Professional)
# ---------------------------------

import streamlit as st
import pandas as pd
from datetime import datetime

# --- Page Configuration (MUST be the first Streamlit command) ---
st.set_page_config(
    page_title="WriteWise Pro | Task Distributor",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Professional Styling (CSS Injection) ---
# Yeh "Super Pro" look and feel ke liye jadu hai
def load_custom_styling():
    st.markdown("""
    <style>
        /* --- General Theme & Font --- */
        .stApp {
            background-color: #0E1117; /* Dark Background */
        }
        
        /* --- Interactive Tabs --- */
        button[data-baseweb="tab"] {
            font-size: 16px;
            font-weight: 500;
            background-color: transparent;
            border-radius: 8px;
            padding: 10px 15px;
            margin: 0 5px;
            transition: transform 0.3s ease, background-color 0.3s ease; /* Smooth animation */
        }
        button[data-baseweb="tab"]:hover {
            transform: scale(1.1); /* Tab ko 11% bada karein */
            background-color: #262730; /* Hover par halka background */
        }
        button[data-baseweb="tab"][aria-selected="true"] {
            background-color: #0068C9; /* Selected tab ka color */
            color: white;
            font-weight: bold;
        }

        /* --- Custom "Card" for Metrics --- */
        .metric-card {
            background-color: #1a1a2e; /* Card ka background color */
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            border: 1px solid #2a2a4a;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .metric-card h3 {
            font-size: 18px;
            color: #a0a0b0; /* Label ka color */
            margin-bottom: 10px;
        }
        .metric-card p {
            font-size: 32px;
            font-weight: bold;
            color: #ffffff; /* Value ka color */
            margin: 0;
        }

        /* --- Buttons --- */
        .stButton>button {
            border-radius: 8px;
            border: 1px solid #0068C9;
            background-color: #0068C9;
            color: white;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #0056a8;
            border-color: #0056a8;
        }
        
    </style>
    """, unsafe_allow_html=True)

# --- Data Loading and Initialization ---
@st.cache_data(ttl=600)
def load_data():
    try:
        df = pd.read_csv("data.csv")
    except FileNotFoundError:
        df = pd.DataFrame(columns=[
            "Task ID", "File Name", "Task Type", "Assigned To", 
            "Priority", "Payment (PKR)", "Payment Status", "Timestamp"
        ])
    return df

def save_data(df):
    df.to_csv("data.csv", index=False)

# --- Main Application Logic ---

# Custom styling ko load karein
load_custom_styling()

# Data load karein
df = load_data()

# Writers ki list aur rotation order
WRITERS = ["Muhammad Imran", "Mazhar Abbas", "Muhammad Ahmad"]
NEW_TASK_ORDER = [WRITERS[0], WRITERS[1], WRITERS[2]]
REVISION_ORDER = [WRITERS[2], WRITERS[1], WRITERS[0]]

# Title ko behtar andaz mein dikhayein
st.markdown("<h1 style='text-align: center; color: #FAFAFA;'>✍️ WriteWise Pro - Task Distributor</h1>", unsafe_allow_html=True)
st.markdown("---")


# --- Tabs ka Istemal ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Dashboard", 
    "✍️ Task Entry", 
    "🔍 Records & Payments", 
    "📊 Monthly Reports"
])

# == TAB 1: Dashboard =========================================================
with tab1:
    st.header("Overall Performance Dashboard")
    
    if df.empty:
        st.warning("Koi data mojood nahi. Pehle 'Task Entry' tab se kaam shamil karein.")
    else:
        # Metrics ko cards mein dikhayein
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Kul Tasks</h3>
                <p>{len(df)}</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Naye Tasks</h3>
                <p>{len(df[df['Task Type'] == 'New Task'])}</p>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Revisions</h3>
                <p>{len(df[df['Task Type'] == 'Revision'])}</p>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            pending_payment = df[df['Payment Status'] == 'Pending']['Payment (PKR)'].sum()
            st.markdown(f"""
            <div class="metric-card">
                <h3>Pending Payments</h3>
                <p>PKR {pending_payment:,.0f}</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        
        # Performance Chart
        st.subheader("Writer Ki Karkardagi")
        performance = df['Assigned To'].value_counts().reset_index()
        performance.columns = ['Writer', 'Total Tasks']
        st.bar_chart(performance.set_index('Writer'))

# == TAB 2: Task Entry ========================================================
with tab2:
    st.header("Naya Kaam Shamil Karein")
    
    # Next writer maloom karein
    last_writer_new = df[df['Task Type'] == 'New Task']['Assigned To'].iloc[-1] if not df[df['Task Type'] == 'New Task'].empty else None
    last_writer_rev = df[df['Task Type'] == 'Revision']['Assigned To'].iloc[-1] if not df[df['Task Type'] == 'Revision'].empty else None

    def get_next_writer(order, last_writer):
        if last_writer is None:
            return order[0]
        try:
            last_index = order.index(last_writer)
            return order[(last_index + 1) % len(order)]
        except ValueError:
            return order[0]

    next_new_task_writer = get_next_writer(NEW_TASK_ORDER, last_writer_new)
    next_revision_writer = get_next_writer(REVISION_ORDER, last_writer_rev)
    
    col1, col2 = st.columns([2, 1]) # Form ke liye zyada jaga, side info ke liye kam

    with col1:
        with st.form("task_form", clear_on_submit=True):
            task_type = st.selectbox("Task Ki Qisam", ["New Task", "Revision"])
            file_name = st.text_input("File Ka Naam")
            priority = st.select_slider("Ahmiyat (Priority)", ["Low", "Normal", "High", "Urgent"])
            payment = st.number_input("Payment (PKR)", min_value=0, step=100)
            
            submitted = st.form_submit_button("✅ Task Shamil Karein")

            if submitted:
                if not file_name:
                    st.error("File ka naam likhna lazmi hai!")
                else:
                    new_task_id = df["Task ID"].max() + 1 if not df.empty else 1
                    assigned_to = next_new_task_writer if task_type == 'New Task' else next_revision_writer
                    
                    new_entry = pd.DataFrame([{
                        "Task ID": new_task_id,
                        "File Name": file_name,
                        "Task Type": task_type,
                        "Assigned To": assigned_to,
                        "Priority": priority,
                        "Payment (PKR)": payment,
                        "Payment Status": "Pending",
                        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }])
                    
                    df = pd.concat([df, new_entry], ignore_index=True)
                    save_data(df)
                    st.success(f"✅ Kaam '{file_name}' ko {assigned_to} ke liye shamil kar diya gaya hai!")

    with col2:
        st.subheader("Next Writer Rotation")
        st.info(f"**Naye Task Ke Liye:** {next_new_task_writer}")
        st.warning(f"**Revision Ke Liye:** {next_revision_writer}")


# == TAB 3: Records & Payments ===============================================
with tab3:
    st.header("Tamam Records Aur Payments")
    
    if df.empty:
        st.info("Abhi tak koi record mojood nahi.")
    else:
        st.dataframe(df.sort_values(by="Task ID", ascending=False), use_container_width=True)

        st.markdown("---")
        st.subheader("Record Mein Tabdeeli Karein")

        task_id_to_edit = st.number_input("Edit Karne Ke Liye Task ID Likhein", min_value=1, format="%d")
        
        if task_id_to_edit in df["Task ID"].values:
            task_data = df[df["Task ID"] == task_id_to_edit].iloc[0]
            
            col1, col2 = st.columns(2)
            with col1:
                new_payment = st.number_input("Nayi Payment Amount", value=task_data["Payment (PKR)"], key=f"pay_{task_id_to_edit}")
            with col2:
                new_status = st.selectbox("Naya Payment Status", ["Pending", "Paid"], index=["Pending", "Paid"].index(task_data["Payment Status"]), key=f"stat_{task_id_to_edit}")
            
            if st.button("💾 Update Karein"):
                df.loc[df["Task ID"] == task_id_to_edit, "Payment (PKR)"] = new_payment
                df.loc[df["Task ID"] == task_id_to_edit, "Payment Status"] = new_status
                save_data(df)
                st.success(f"Task ID {task_id_to_edit} update ho gaya hai.")
                st.experimental_rerun()
        else:
            st.warning("Durust Task ID likhein.")

        with st.expander("❌ Record Delete Karein (Admin Only)"):
            admin_pass = st.text_input("Admin Password", type="password")
            task_id_to_delete = st.number_input("Delete Karne Ke Liye Task ID", min_value=1, format="%d")
            if st.button("🗑️ Delete"):
                if admin_pass == "YOUR_ADMIN_PASSWORD": # Apna password yahan likhein
                    if task_id_to_delete in df['Task ID'].values:
                        df = df[df["Task ID"] != task_id_to_delete]
                        save_data(df)
                        st.success(f"Task ID {task_id_to_delete} delete kar diya gaya hai.")
                        st.experimental_rerun()
                    else:
                        st.error("Ghalat Task ID.")
                else:
                    st.error("Ghalat Admin Password!")

# == TAB 4: Monthly Reports ==================================================
with tab4:
    st.header("Mahana Karkardagi Ki Report")
    
    if df.empty:
        st.info("Koi data mojood nahi, isliye report nahi banayi ja sakti.")
    else:
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        
        col1, col2 = st.columns(2)
        with col1:
            available_years = sorted(df['Timestamp'].dt.year.unique(), reverse=True)
            selected_year = st.selectbox("Saal Chunein", available_years)
        with col2:
            available_months = sorted(df[df['Timestamp'].dt.year == selected_year]['Timestamp'].dt.month.unique())
            month_names = {m: datetime(1900, m, 1).strftime('%B') for m in available_months}
            selected_month_name = st.selectbox("Mahina Chunein", [month_names[m] for m in available_months])
            selected_month = [m for m, name in month_names.items() if name == selected_month_name][0]

        if st.button("📊 Report Banayein"):
            # Data ko month aur year ke hisab se filter karein
            monthly_df = df[(df['Timestamp'].dt.year == selected_year) & (df['Timestamp'].dt.month == selected_month)]
            
            if monthly_df.empty:
                st.warning(f"{selected_month_name} {selected_year} ke liye koi data nahi hai.")
            else:
                st.subheader(f"Summary for {selected_month_name} {selected_year}")

                # Overall Summary
                total_tasks = len(monthly_df)
                new_tasks = len(monthly_df[monthly_df['Task Type'] == 'New Task'])
                revisions = len(monthly_df[monthly_df['Task Type'] == 'Revision'])
                total_payment = monthly_df['Payment (PKR)'].sum()
                
                c1, c2, c3, c4 = st.columns(4)
                with c1: st.metric("Kul Tasks", total_tasks)
                with c2: st.metric("Naye Tasks", new_tasks)
                with c3: st.metric("Revisions", revisions)
                with c4: st.metric("Kul Kamai (PKR)", f"{total_payment:,.0f}")
                
                st.markdown("---")
                
                # Writer-wise Summary
                st.subheader("Writer Ki Mahana Karkardagi")
                writer_summary = monthly_df.groupby('Assigned To').agg(
                    New_Tasks=('Task Type', lambda x: (x == 'New Task').sum()),
                    Revisions=('Task Type', lambda x: (x == 'Revision').sum()),
                    Total_Earnings_PKR=('Payment (PKR)', 'sum')
                ).reset_index()
                
                st.dataframe(writer_summary, use_container_width=True)


import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import kagglehub

# --- CONFIG & STYLING ---
st.set_page_config(page_title="HR Insight Hub - Visual Attrition Analysis", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; } /* Light grey background */
    .stMetric { 
        background-color: #1f1e21; 
        padding: 15px; 
        border-radius: 10px; 
        box-shadow: 0 2px 8px rgba(0,0,0,0.08); /* More pronounced shadow */
        border-left: 5px solid #4CAF50; /* Green accent border */
    }
    h1, h2, h3 { color: #2E4053; } /* Darker headings */
    .stSelectbox, .stMultiSelect, .stSlider {
        background-color: #1f1e21;
        border-radius: 5px;
        padding: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    path = kagglehub.dataset_download("pavansubhasht/ibm-hr-analytics-attrition-dataset")
    df = pd.read_csv(f"{path}/WA_Fn-UseC_-HR-Employee-Attrition.csv")
    return df

df_raw = load_data()

# --- SIDEBAR: INTERACTIVE FILTERS ---
st.sidebar.header("🎛️ ตัวกรองข้อมูล")
st.sidebar.markdown("ปรับแต่งการวิเคราะห์ตามแผนกและช่วงอายุ")

# Filter 1: Department
selected_dept = st.sidebar.multiselect(
    "เลือกแผนก:", 
    options=df_raw['Department'].unique(), 
    default=df_raw['Department'].unique(),
    help="เลือกแผนกที่ต้องการวิเคราะห์"
)

# Filter 2: Age Range
age_min, age_max = int(df_raw['Age'].min()), int(df_raw['Age'].max())
selected_age = st.sidebar.slider(
    "ช่วงอายุพนักงาน:", 
    age_min, age_max, (age_min, age_max),
    help="ปรับเพื่อดูข้อมูลพนักงานตามช่วงอายุที่เลือก"
)

# Apply Filters
df = df_raw[(df_raw['Department'].isin(selected_dept)) & 
            (df_raw['Age'].between(selected_age[0], selected_age[1]))]

# --- MAIN DASHBOARD ---
st.title("🌟 HR Insight Hub: เจาะลึกการลาออกอย่างเข้าใจง่าย")
st.markdown(f"**วิเคราะห์ข้อมูลพนักงานจำนวน `{len(df)}` คน** (จาก `{len(df_raw)}` คนเดิม) ที่ถูกคัดกรอง")

# --- Key Metrics ---
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
attrition_rate = (df['Attrition'] == 'Yes').mean() * 100
col_m1.metric("อัตราการลาออก (โดยรวม)", f"{attrition_rate:.1f}%")
col_m2.metric("เงินเดือนเฉลี่ย (บาท)", f"{df['MonthlyIncome'].mean():,.0f}")
col_m3.metric("อายุงานเฉลี่ย (ปี)", f"{df['YearsAtCompany'].mean():,.1f}")
col_m4.metric("ความพอใจงานเฉลี่ย (1-4)", f"{df['JobSatisfaction'].mean():.2f}")

st.divider()

# --- QUESTION 1: เงินเดือนต่ำ หรือ ความพอใจต่ำ? ---


col1, col2 = st.columns(2)

with col1:
    # Graph 1.1: Box Plot for Monthly Income
    fig1_1 = px.box(df, x="Attrition", y="MonthlyIncome", color="Attrition",
                    title="เปรียบเทียบ 'เงินเดือน' ของพนักงานที่ลาออก vs ไม่ลาออก",
                    labels={"MonthlyIncome": "เงินเดือนต่อเดือน", "Attrition": "สถานะการลาออก"},
                    color_discrete_map={'Yes':'#FF6347', 'No':'#4682B4'}) # Red for Yes, Blue for No
    fig1_1.update_layout(showlegend=False) # Hide redundant legend
    st.plotly_chart(fig1_1, use_container_width=True)
    st.info("📉 **Insight:** พนักงานที่ลาออกมักมีเงินเดือนเฉลี่ยที่ต่ำกว่าอย่างเห็นได้ชัด")

with col2:
    # Graph 1.2: Bar Chart for Job Satisfaction
    sat_df = df.groupby(['JobSatisfaction', 'Attrition']).size().reset_index(name='Count')
    fig1_2 = px.bar(sat_df, x="JobSatisfaction", y="Count", color="Attrition",
                    title="สัดส่วนการลาออกตาม 'ระดับความพอใจในงาน' (1=ต่ำสุด, 4=สูงสุด)",
                    labels={"JobSatisfaction": "ระดับความพอใจในงาน", "Count": "จำนวนพนักงาน"},
                    barmode="group",
                    color_discrete_map={'Yes':'#FF6347', 'No':'#4682B4'})
    fig1_2.update_layout(xaxis_title="ระดับความพอใจในงาน (1=ไม่พอใจมาก, 4=พอใจมาก)")
    st.plotly_chart(fig1_2, use_container_width=True)
    st.info("😟 **Insight:** ความพอใจในงานที่ต่ำมาก (ระดับ 1-2) สัมพันธ์กับการลาออกที่สูงขึ้น")

st.divider()

# --- QUESTION 2: Work-Life Balance ลดการลาออกได้จริง? ---


# Graph 2.1: Percentage Attrition by WorkLifeBalance
wlb_attrition = df.groupby('WorkLifeBalance')['Attrition'].value_counts(normalize=True).unstack(fill_value=0)['Yes'] * 100
wlb_attrition_df = wlb_attrition.reset_index(name='Attrition_Rate')
fig2_1 = px.bar(wlb_attrition_df, x='WorkLifeBalance', y='Attrition_Rate', 
                title="อัตราการลาออก (%) ตามระดับ Work-Life Balance",
                labels={'WorkLifeBalance': 'ระดับ Work-Life Balance (1=แย่มาก, 4=ดีเยี่ยม)', 'Attrition_Rate': '% การลาออก'},
                color='Attrition_Rate', color_continuous_scale='OrRd') # Gradient color for impact
fig2_1.update_layout(xaxis_title="ระดับ Work-Life Balance", yaxis_title="% อัตราการลาออก")
st.plotly_chart(fig2_1, use_container_width=True)
st.info("✅ **Insight:** ระดับ Work-Life Balance ที่แย่ (1-2) มีอัตราการลาออกสูงกว่าอย่างเห็นได้ชัด **เป็นความจริง ไม่ใช่แค่ความเชื่อ!**")

st.divider()

# --- QUESTION 3: พนักงานเก่า vs พนักงานใหม่ ใครเสี่ยงลาออกมากกว่า? ---


col3_1, col3_2 = st.columns(2)

with col3_1:
    # Graph 3.1: Histogram of YearsAtCompany
    fig3_1 = px.histogram(df, x="YearsAtCompany", color="Attrition", marginal="box",
                          title="การกระจายตัวของ 'อายุงานในบริษัท' (YearsAtCompany)",
                          labels={"YearsAtCompany": "อายุงานในบริษัท (ปี)", "count": "จำนวนพนักงาน"},
                          color_discrete_map={'Yes':'#FF6347', 'No':'#4682B4'})
    st.plotly_chart(fig3_1, use_container_width=True)
    st.info("⏳ **Insight:** พนักงานที่มีอายุงานน้อย (โดยเฉพาะ 0-2 ปี) มีแนวโน้มลาออกสูงกว่า")

with col3_2:
    # Graph 3.2: Histogram of YearsWithCurrManager
    fig3_2 = px.histogram(df, x="YearsWithCurrManager", color="Attrition", marginal="box",
                          title="การกระจายตัวของ 'ระยะเวลาที่อยู่กับหัวหน้าคนปัจจุบัน'",
                          labels={"YearsWithCurrManager": "ระยะเวลา (ปี)", "count": "จำนวนพนักงาน"},
                          color_discrete_map={'Yes':'#FF6347', 'No':'#4682B4'})
    st.plotly_chart(fig3_2, use_container_width=True)
    st.info("🤝 **Insight:** การเปลี่ยนแปลงหัวหน้าบ่อย (อยู่กับหัวหน้าน้อยปี) อาจเป็นสัญญาณเตือน")

st.divider()

# --- QUESTION 4: ตำแหน่งงานหรือแผนกไหนมีวัฒนธรรมเสี่ยงลาออก? ---


# 1. คำนวณหา % การลาออก
role_attrition_rate = df.groupby('JobRole')['Attrition'].value_counts(normalize=True).unstack(fill_value=0)['Yes'] * 100

# 2. เรียงลำดับข้อมูลใน Pandas ให้เสร็จสรรพ (เรียงจากน้อยไปมาก เพื่อให้กราฟแนวนอนตัวมากอยู่บนสุด)
role_attrition_rate = role_attrition_rate.sort_values(ascending=True).reset_index(name='Attrition_Rate')

# 3. วาดกราฟโดย "ไม่ต้อง" สั่ง update_yaxes เรื่องการเรียงลำดับแล้ว
fig4_1 = px.bar(role_attrition_rate, 
                x='Attrition_Rate', 
                y='JobRole', 
                orientation='h',
                title="10 อันดับตำแหน่งงานที่มีอัตราการลาออกสูงสุด",
                labels={'Attrition_Rate': '% การลาออก', 'JobRole': 'ตำแหน่งงาน'},
                color='Attrition_Rate', 
                color_continuous_scale='Reds')

# ปรับความสวยงามเล็กน้อย (ไม่ต้องสั่ง category_order แล้ว)
fig4_1.update_layout(yaxis={'categoryorder':'trace'}) 

st.plotly_chart(fig4_1, use_container_width=True)
st.info("🚨 **Insight:** ตำแหน่งอย่าง 'Sales Representative' มักมีอัตราการลาออกสูงเป็นพิเศษ")

st.divider()

# --- QUESTION 5: โมเดลกำลังเรียนรู้ 'พฤติกรรมมนุษย์' หรือ 'กฎองค์กร'? ---


# Graph 5.1: Attrition by OverTime (Pie Chart for easy proportion)
overtime_attrition_pie = df.groupby('OverTime')['Attrition'].value_counts(normalize=True).unstack(fill_value=0)
fig5_1 = go.Figure(data=[go.Pie(labels=overtime_attrition_pie.index, 
                                values=overtime_attrition_pie['Yes'], 
                                pull=[0.05 if x == 'Yes' else 0 for x in overtime_attrition_pie.index], # Slightly pull "Yes" slice
                                marker_colors=['#FF6347','#4682B4'] # Red for Yes, Blue for No
                                )])
fig5_1.update_layout(title_text="สัดส่วนการลาออกของพนักงานที่ 'ทำงานล่วงเวลา' (OverTime)")
st.plotly_chart(fig5_1, use_container_width=True)
st.info("📊 **Insight:** พนักงานที่ 'ทำงานล่วงเวลา' (Yes) มีโอกาสลาออกสูงกว่าอย่างมีนัยสำคัญ **นี่คือตัวอย่างของ 'กฎองค์กร' หรือ 'สภาพแวดล้อม' ที่ส่งผลต่อพฤติกรรม**")

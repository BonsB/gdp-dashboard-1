import streamlit as st
import pandas as pd
import plotly.express as px

# 1. การตั้งค่าหน้าเว็บ
st.set_page_config(page_title="รายงานวิเคราะห์สุขภาพจิตในองค์กร", layout="wide")

@st.cache_data
def load_and_clean_data():
    df = pd.read_csv('data/mental-heath-in-tech-2016_20161114.csv')
    
    column_mapping = {
        "If you have a mental health issue, do you feel that it interferes with your work when NOT being treated effectively?": "work_interfere_not_treated",
        "Are you self-employed?": "self_employed",
        "How many employees does your company or organization have?": "company_size",
        "Is your employer primarily a tech company/organization?": "tech_company",
        "Is your primary role within your company related to tech/IT?": "tech_role",
        "Do you work remotely?": "remote_work",
        "Does your employer provide mental health benefits as part of healthcare coverage?": "mental_health_benefits",
        "Do you know the options for mental health care available under your employer-provided coverage?": "care_options_awareness",
        "Has your employer ever formally discussed mental health (for example, as part of a wellness campaign or other official communication)?": "employer_discussion",
        "Does your employer offer resources to learn more about mental health concerns and options for seeking help?": "employer_resources",
        "Is your anonymity protected if you choose to take advantage of mental health or substance abuse treatment resources provided by your employer?": "anonymity_protected",
        "If a mental health issue prompted you to request a medical leave from work, asking for that leave would be:": "medical_leave_ease",
        "What is your age?": "age",
        "What is your gender?": "gender",
        "What country do you live in?": "country",
        "Which of the following best describes your work position?": "work_position"
    }
    
    df = df[list(column_mapping.keys())].rename(columns=column_mapping)
    
    # Cleaning Gender
    df['gender'] = df['gender'].str.lower().str.strip()
    df.loc[df['gender'].isin(['male', 'm', 'man', 'cis male']), 'gender'] = 'ชาย (Male)'
    df.loc[df['gender'].isin(['female', 'f', 'woman', 'cis female']), 'gender'] = 'หญิง (Female)'
    df.loc[~df['gender'].isin(['ชาย (Male)', 'หญิง (Female)']), 'gender'] = 'อื่น ๆ (Others)'
    
    # Filter Age
    df = df[(df['age'] >= 18) & (df['age'] <= 75)]
    
    return df

df = load_and_clean_data()

st.title("📑 รายงานวิเคราะห์ความสัมพันธ์ระหว่างสภาพแวดล้อมการทำงานและสุขภาพจิตพนักงาน")
st.markdown("---")

# --- ส่วนที่ 1: ผลกระทบต่อประสิทธิภาพการทำงาน ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("สัดส่วนระดับผลกระทบต่อการทำงาน เมื่อปัญหาสุขภาพจิตไม่ได้รับการรักษาอย่างเหมาะสม")
    fig1 = px.pie(df, names='work_interfere_not_treated', hole=0.4, 
                 color_discrete_sequence=px.colors.sequential.RdBu)
    st.plotly_chart(fig1, width='stretch')

with col2:
    st.subheader("ความรู้สึกสะดวกใจในการลาป่วยด้วยเหตุผลด้านสุขภาพจิต จำแนกตามเพศของพนักงาน")
    leave_order = ["Very easy", "Somewhat easy", "Neither easy nor difficult", "Somewhat difficult", "Very difficult", "I don't know"]
    fig2 = px.histogram(df, x="medical_leave_ease", color="gender", 
                       category_orders={"medical_leave_ease": leave_order}, barmode="group",
                       labels={"medical_leave_ease": "ระดับความสะดวกในการลา", "gender": "กลุ่มตัวอย่าง"})
    st.plotly_chart(fig2, width='stretch')

# --- ส่วนที่ 2: บทบาทขององค์กรและสวัสดิการ ---
st.divider()

col3, col4 = st.columns(2)

with col3:
    st.subheader("การจัดสรรสวัสดิการด้านสุขภาพจิตจำแนกตามขนาดขององค์กร")
    size_order = ["1-5", "6-25", "26-100", "100-500", "500-1000", "More than 1000"]
    fig3 = px.histogram(df, x="company_size", color="mental_health_benefits", 
                       category_orders={"company_size": size_order},
                       labels={"company_size": "จำนวนพนักงานในองค์กร", "mental_health_benefits": "การจัดสรรสวัสดิการ"})
    st.plotly_chart(fig3, width='stretch')

with col4:
    st.subheader("ความสัมพันธ์ระหว่างรูปแบบการทำงาน (Remote/Onsite) กับการคุ้มครองความเป็นส่วนตัวของพนักงาน")
    sunburst_df = df[['remote_work', 'anonymity_protected']].dropna()
    fig4 = px.sunburst(sunburst_df, path=['remote_work', 'anonymity_protected'], 
                      color='remote_work', labels={'labels':'ข้อมูล', 'parent':'กลุ่ม'})
    st.plotly_chart(fig4, width='stretch')

# --- ส่วนที่ 3: วัฒนธรรมองค์กรและการรับรู้ข้อมูุล ---
st.divider()

col5, col6 = st.columns(2)

with col5:
    st.subheader("ความสอดคล้องระหว่างการสื่อสารภายในองค์กรกับการจัดสรรทรัพยากรด้านสุขภาพจิต")
    heatmap_data = pd.crosstab(df['employer_discussion'], df['employer_resources'])
    fig5 = px.imshow(heatmap_data, text_auto=True, color_continuous_scale='YlGnBu',
                    labels=dict(x="การจัดสรรทรัพยากร/แหล่งข้อมูล", y="ความถี่การสื่อสารขององค์กร"))
    st.plotly_chart(fig5, width='stretch')

with col6:
    st.subheader("ระดับการรับรู้สิทธิการรักษาสุขภาพจิตของพนักงานสายเทคโนโลยี")
    fig6 = px.histogram(df, x="tech_role", color="care_options_awareness", barmode="group",
                       labels={"tech_role": "บทบาทหน้าที่ (1=สายเทคโนโลยี, 0=สายอื่น)", "care_options_awareness": "ระดับการรับรู้สิทธิ"})
    st.plotly_chart(fig6, width='stretch')


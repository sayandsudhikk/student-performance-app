import streamlit as st
import pandas as pd
import plotly.express as px
from api_client import get_student_view


def student_interface():
    st.subheader("Student Dashboard")
    user = st.session_state.user
    student_id = user.get('linked_student_id')
    if not student_id:
        st.error("No linked student ID")
        return
    resp = get_student_view(student_id)
    if resp.get('error'):
        st.error(resp['error'])
        return
    records = resp['records']
    evaluation = resp.get('evaluation')
    df = pd.DataFrame(records)
    # convert numeric fields to numbers to avoid type issues
    for col in ['subject_score', 'attendance', 'study_hours', 'internal_mark']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    st.write(df[['subject','subject_score','attendance','study_hours']])
    if not df.empty:
        st.plotly_chart(px.bar(df, x='subject', y='subject_score', title='Marks'), key='stu_marks')
        st.plotly_chart(px.bar(df, x='subject', y='attendance', title='Attendance'), key='stu_attendance')
        st.plotly_chart(px.bar(df, x='subject', y='study_hours', title='Study Hours'), key='stu_study_hours')
    if evaluation and evaluation.get('evaluation_status') == 'COMPLETED':
        st.write(f"**Result:** {evaluation['pass_fail_result']} (Confidence: {evaluation['confidence_level']})")
        st.write(f"**Teacher comment:** {evaluation['teacher_comment']}")
        st.write("**Recommendations:**")
        for rec in evaluation['ai_recommendation'].split('\n'):
            st.write(f"- {rec}")
    else:
        st.info("Evaluation pending. Please wait for teacher review.")

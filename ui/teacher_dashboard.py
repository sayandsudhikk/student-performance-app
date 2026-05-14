import streamlit as st
import pandas as pd
import plotly.express as px
from api_client import upload_excel, search_student, generate_evaluation, save_evaluation


def teacher_interface():
    st.subheader("Teacher Dashboard")
    menu = st.sidebar.selectbox("Menu", ["Upload Data", "Search Student"])

    if menu == "Upload Data":
        file = st.file_uploader("Upload Excel file", type=['xlsx'])
        if file:
            with open("temp.xlsx", "wb") as f:
                f.write(file.getbuffer())
            resp = upload_excel("temp.xlsx")
            if resp.get('error'):
                st.error(resp['error'])
            else:
                st.success("Data uploaded")
    elif menu == "Search Student":
        student_id = st.text_input("Student ID to search")
        if st.button("Search"):
            resp = search_student(student_id)
            if resp.get('error'):
                st.error(resp['error'])
            else:
                records = resp['records']
                df = pd.DataFrame(records)
                # ensure numeric columns have proper dtype (fixes arrow serialization errors)
                for col in ['subject_score', 'attendance', 'study_hours', 'internal_mark']:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                st.write(df)
                # graphs
                if not df.empty:
                    fig1 = px.bar(df, x='subject', y='subject_score', title='Subject vs Marks')
                    fig2 = px.bar(df, x='subject', y='attendance', title='Subject vs Attendance')
                    fig3 = px.bar(df, x='subject', y='study_hours', title='Subject vs Study Hours')
                    st.plotly_chart(fig1, key='marks_chart')
                    st.plotly_chart(fig2, key='attendance_chart')
                    st.plotly_chart(fig3, key='study_hours_chart')

                # store relevant values in session state for later use
                st.session_state['current_student_id'] = student_id
                st.session_state['current_df'] = df
        # if we already have search results in session state, display them
        if 'current_df' in st.session_state:
            df = st.session_state['current_df']
            st.write(df)
            if not df.empty:
                fig1 = px.bar(df, x='subject', y='subject_score', title='Subject vs Marks')
                fig2 = px.bar(df, x='subject', y='attendance', title='Subject vs Attendance')
                fig3 = px.bar(df, x='subject', y='study_hours', title='Subject vs Study Hours')
                st.plotly_chart(fig1, key='marks_chart2')
                st.plotly_chart(fig2, key='attendance_chart2')
                st.plotly_chart(fig3, key='study_hours_chart2')

            comment = st.text_area("Teacher comment", key='comment')
            if st.button("Generate Evaluation"):
                student_id = st.session_state.get('current_student_id')
                gen = generate_evaluation(student_id, comment)
                if gen.get('error'):
                    st.error(gen['error'])
                else:
                    # keep the result in session so it survives reruns
                    st.session_state['last_gen'] = gen
                    st.json(gen)
                    if gen.get('raw_response') is not None:
                        st.subheader("Raw LLM response")
                        st.json(gen['raw_response'])
            # if we have a previously generated evaluation, show save button
            if 'last_gen' in st.session_state:
                gen = st.session_state['last_gen']
                if st.button("Save Evaluation"):
                    student_id = st.session_state.get('current_student_id')
                    save_resp = save_evaluation(
                        student_id,
                        gen['pass_fail'],
                        gen['confidence'],
                        gen['explanation'],
                        gen['recommendations'],
                        st.session_state.get('comment', '')
                    )
                    if save_resp.get('error'):
                        st.error(save_resp['error'])
                    else:
                        st.success("Evaluation saved")
                        # clear stored gen
                        del st.session_state['last_gen']
                        del st.session_state['comment']
                        del st.session_state['current_student_id']
                        del st.session_state['current_df']

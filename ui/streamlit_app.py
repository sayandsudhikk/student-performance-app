import streamlit as st
from teacher_dashboard import teacher_interface
from student_dashboard import student_interface
from api_client import login, register

st.title("Student Performance Evaluation System")

# compatibility helper for rerun

def rerun():
    if hasattr(st, 'experimental_rerun'):
        st.experimental_rerun()
    else:
        st.rerun()

# session state helpers
if 'user' not in st.session_state:
    st.session_state['user'] = None
if 'registering' not in st.session_state:
    st.session_state['registering'] = False

if st.session_state.user is None:
    # show either login or registration form
    if st.session_state.registering:
        st.subheader("Register")
        r_username = st.text_input("Username", key='r_user')
        r_password = st.text_input("Password", type='password', key='r_pass')
        role = st.selectbox("Role", ["TEACHER", "STUDENT"])
        linked = None
        if role == "STUDENT":
            linked = st.text_input("Linked student_id")
        if st.button("Submit Registration"):
            payload = {'username': r_username, 'password': r_password, 'role': role}
            if linked:
                payload['linked_student_id'] = linked
            resp = register(**payload)
            if resp.get('error'):
                st.error(resp['error'])
            else:
                st.success("Registration successful. Please log in.")
                st.session_state.registering = False
                rerun()
        if st.button("Back to login"):
            st.session_state.registering = False
            rerun()
    else:
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type='password')
        if st.button("Login"):
            result = login(username, password)
            if result.get('error'):
                st.error(result['error'])
            else:
                st.session_state.user = result
                st.success("Logged in")
                rerun()
        if st.button("Register an account"):
            st.session_state.registering = True
            rerun()
else:
    role = st.session_state.user['role']
    if role == 'TEACHER':
        teacher_interface()
    else:
        student_interface()

    if st.button("Logout"):
        st.session_state.user = None
        rerun()

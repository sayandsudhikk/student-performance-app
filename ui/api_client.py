import requests
import os

# Use BACKEND_URL env variable if set (set this in Streamlit Cloud secrets),
# otherwise fall back to localhost for local development.
BASE_URL = os.environ.get('BACKEND_URL', 'http://localhost:5000')

def safe_request(resp):
    """Return JSON if possible, otherwise a dict describing the error."""
    try:
        return resp.json()
    except ValueError:
        return {'error': f'Unexpected response ({resp.status_code})', 'text': resp.text}



def register(username, password, role, linked_student_id=None):
    resp = requests.post(f"{BASE_URL}/auth/register", json={
        'username': username,
        'password': password,
        'role': role,
        'linked_student_id': linked_student_id
    })
    return safe_request(resp)


def login(username, password):
    resp = requests.post(f"{BASE_URL}/auth/login", json={'username': username, 'password': password})
    return safe_request(resp)


def upload_excel(file_path):
    with open(file_path, 'rb') as f:
        files = {'file': f}
        resp = requests.post(f"{BASE_URL}/teacher/upload", files=files)
        return safe_request(resp)


def search_student(student_id):
    resp = requests.get(f"{BASE_URL}/teacher/search", params={'student_id': student_id})
    return safe_request(resp)


def generate_evaluation(student_id, teacher_comment):
    resp = requests.post(f"{BASE_URL}/teacher/generate", json={'student_id': student_id, 'teacher_comment': teacher_comment})
    return safe_request(resp)


def save_evaluation(student_id, pass_fail, confidence, explanation, recommendations, teacher_comment):
    resp = requests.post(f"{BASE_URL}/teacher/save_evaluation", json={
        'student_id': student_id,
        'pass_fail': pass_fail,
        'confidence': confidence,
        'explanation': explanation,
        'recommendations': recommendations,
        'teacher_comment': teacher_comment
    })
    return safe_request(resp)


def get_student_view(student_id):
    resp = requests.get(f"{BASE_URL}/student/data", params={'student_id': student_id})
    return safe_request(resp)

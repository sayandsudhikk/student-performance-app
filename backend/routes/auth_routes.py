from flask import Blueprint, request, jsonify
from database.db import get_connection
from utils.validators import is_valid_username, is_valid_password

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')
    linked_student_id = data.get('linked_student_id')

    if not username or not password or not role:
        return jsonify({'error': 'Missing fields'}), 400

    if not is_valid_username(username) or not is_valid_password(password):
        return jsonify({'error': 'Invalid username or password'}), 400

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO users (username, password, role, linked_student_id) VALUES (?,?,?,?)',
            (username, password, role.upper(), linked_student_id)
        )
        conn.commit()
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500
    conn.close()
    return jsonify({'message': 'registered'}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'Missing credentials'}), 400

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
    user = cursor.fetchone()
    conn.close()
    if user:
        return jsonify({'username': user['username'], 'role': user['role'], 'linked_student_id': user['linked_student_id']}), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

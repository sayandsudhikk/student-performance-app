from flask import Blueprint, request, jsonify
from database.db import get_connection

student_bp = Blueprint('student', __name__)


@student_bp.route('/data', methods=['GET'])
def get_student_data():
    student_id = request.args.get('student_id')
    if not student_id:
        return jsonify({'error': 'student_id required'}), 400
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM student_records WHERE student_id=?', (student_id,))
    records = cursor.fetchall()
    if not records:
        conn.close()
        return jsonify({'error': 'not found'}), 404
    records_list = [dict(r) for r in records]
    # fetch evaluation (take most recent)
    cursor.execute(
        'SELECT * FROM evaluations WHERE record_id IN (SELECT id FROM student_records WHERE student_id=?) ORDER BY timestamp DESC LIMIT 1',
        (student_id,)
    )
    eval_row = cursor.fetchone()
    conn.close()
    evaluation = dict(eval_row) if eval_row else None
    return jsonify({'records': records_list, 'evaluation': evaluation}), 200

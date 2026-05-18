from flask import Blueprint, request, jsonify
from services.excel_service import ExcelService
from services.llm_service import generate_evaluation
from database.db import get_connection

teacher_bp = Blueprint('teacher', __name__)


@teacher_bp.route('/upload', methods=['POST'])
def upload_excel():
    # expectation: file uploaded as form-data
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'No file provided'}), 400
    import tempfile, os
    tmp_dir = tempfile.gettempdir()
    filepath = os.path.join(tmp_dir, file.filename)
    file.save(filepath)
    try:
        ExcelService.validate_and_store(filepath)
        # optionally remove temp file
        os.remove(filepath)
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    return jsonify({'message': 'data stored'}), 200


@teacher_bp.route('/search', methods=['GET'])
def search_student():
    student_id = request.args.get('student_id')
    if not student_id:
        return jsonify({'error': 'student_id required'}), 400
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM student_records WHERE student_id=?', (student_id,))
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        return jsonify({'error': 'not found'}), 404
    records = [dict(r) for r in rows]
    return jsonify({'records': records}), 200


@teacher_bp.route('/generate', methods=['POST'])
def generate():
    data = request.json
    student_id = data.get('student_id')
    comment = data.get('teacher_comment', '')
    # fetch academic data
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM student_records WHERE student_id=?', (student_id,))
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        return jsonify({'error': 'student not found'}), 404
    student_data = {'records': [dict(r) for r in rows]}
    try:
        llm_result = generate_evaluation(student_data, comment)
    except Exception as e:
        return jsonify({'error': f'Evaluation failed: {str(e)}'}), 500
    if llm_result.get('error'):
        return jsonify(llm_result), 400
    return jsonify(llm_result), 200


@teacher_bp.route('/save_evaluation', methods=['POST'])
def save_evaluation():
    data = request.json
    student_id = data.get('student_id')
    pass_fail = data.get('pass_fail')
    confidence = data.get('confidence')
    explanation = data.get('explanation')
    recommendations = data.get('recommendations')
    comment = data.get('teacher_comment', '')
    if not student_id or pass_fail is None:
        return jsonify({'error': 'missing fields'}), 400
    conn = get_connection()
    cursor = conn.cursor()
    # find each relevant record and update/insert evaluation
    cursor.execute('SELECT id FROM student_records WHERE student_id=?', (student_id,))
    record = cursor.fetchone()
    if not record:
        conn.close()
        return jsonify({'error': 'student record not found'}), 404
    record_id = record['id']
    if isinstance(recommendations, list):
        recommendations_str = '\n'.join(str(r) for r in recommendations)
    else:
        recommendations_str = str(recommendations) if recommendations else ''
    cursor.execute(
        '''INSERT INTO evaluations
           (record_id, pass_fail_result, confidence_level, teacher_comment, ai_recommendation, evaluation_status)
           VALUES (?,?,?,?,?,?)''',
        (record_id, pass_fail, confidence, comment, recommendations_str, 'COMPLETED')
    )
    conn.commit()
    conn.close()
    return jsonify({'message': 'evaluation saved'}), 200

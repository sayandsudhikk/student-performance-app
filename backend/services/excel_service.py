import pandas as pd
from database.db import get_connection


class ExcelService:
    @staticmethod
    def validate_and_store(file_path):
        """Read an Excel file, validate columns, and insert rows into student_records."""
        required_cols = [
            'student_id', 'student_name', 'register_number',
            'roll_number', 'subject', 'study_hours',
            'attendance', 'subject_score', 'internal_mark'
        ]
        df = pd.read_excel(file_path)
        # normalize columns (lowercase and strip whitespace) to prevent case-sensitivity errors
        df.columns = df.columns.astype(str).str.lower().str.strip()
        # ensure columns exist
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")

        # drop completely empty rows
        df = df.dropna(how='all')
        # remove duplicates within the upload file itself (student_id + subject should be unique)
        df = df.drop_duplicates(subset=['student_id', 'subject'], keep='last')

        conn = get_connection()
        cursor = conn.cursor()
        for _, row in df.iterrows():
            try:
                # use REPLACE to overwrite any existing record for the same student+subject
                cursor.execute(
                    '''INSERT OR REPLACE INTO student_records
                        (id, student_id, student_name, register_number, roll_number,
                         subject, study_hours, attendance, subject_score, internal_mark)
                       VALUES (
                         (SELECT id FROM student_records WHERE student_id=? AND subject=?),
                         ?,?,?,?,?,?,?,?,?)''',
                    (
                        row['student_id'], row['subject'],
                        row['student_id'], row['student_name'], row['register_number'],
                        row['roll_number'], row['subject'], row['study_hours'],
                        row['attendance'], row['subject_score'], row['internal_mark']
                    )
                )
            except Exception:
                # skip problematic rows
                continue
        conn.commit()
        conn.close()

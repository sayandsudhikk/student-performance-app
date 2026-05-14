from flask import Flask
from flask_cors import CORS
from routes.auth_routes import auth_bp
from routes.teacher_routes import teacher_bp
from routes.student_routes import student_bp

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # allow cross-origin requests from Streamlit Cloud
app.config.from_object('config.db_config')

# ensure database exists
from database.db import init_db, get_connection
import os
# create database file if missing
if not os.path.exists(app.config['DB_PATH']):
    init_db()

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(teacher_bp, url_prefix='/teacher')
app.register_blueprint(student_bp, url_prefix='/student')

if __name__ == '__main__':
    app.run(debug=True)

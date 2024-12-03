from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from application.config import Config
from application.database import db
from application.model import *
from datetime import date
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity




# Configure the secret key for JWT

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    app.config['JWT_SECRET_KEY'] = 'your_secret_key'  # Change this to a secure key
    jwt = JWTManager(app)


    with app.app_context():
        db.create_all()

        # Initialize some default data if necessary
        if not Stream.query.filter_by(name='Engineering').first():
            default_stream = Stream(name='Engineering', description='Engineering Stream')
            db.session.add(default_stream)

        if not Student.query.filter_by(id=1).first():
            student = Student(
                id=1,
                year=1,
                section='A',
                name = 'Sanji',
                stream_id=default_stream.id
            )
            db.session.add(student)
            student = Student(
                id=2,
                year=1,
                section='A',
                name='Jack Cooper',
                stream_id=default_stream.id
            )
            db.session.add(student)

        if not Faculty.query.filter_by(id=1).first():
            faculty = Faculty(
                id=1,
                stream_id=default_stream.id,
                name='default',
                passcode="password"
            )
            db.session.add(faculty)

        if not Course.query.filter_by(course_id=1).first():
            course = Course(
                course_id=1,
                stream_id=default_stream.id
            )
            db.session.add(course)
        
        if not Answer.query.filter_by(id=1).first():
            answer = Answer(
                question_id=1,
                student_id=1,
                marks = 1,
                exam_id =1,
            )
            db.session.add(answer)
            answer = Answer(
                question_id=1,
                student_id=2,
                marks = 1,
                exam_id =1,
            )
            db.session.add(answer)
            
        if not Exam.query.filter_by(id=1).first():
            exam = Exam(
                id=1,
                year=1,
                section='A',
                name='default',
                date=date(2024,12,12),
                courseID = "1",
                faculty_id=faculty.id,
                max_marks=100,
                co1=15, co2=20, co3=25, co4=20, co5=10, co6=10
            )
            db.session.add(exam)

        if not Question.query.filter_by(id=1).first():
            question = Question(
                id=1,
                exam_id=exam.id,
                co=1,
                marks =1
            )
            db.session.add(question)
        
        if not Teaches.query.filter_by(id=1).first():
            teaches = Teaches(
                id=1,
                faculty_id=1,
                year=1,
                section="A",
                course_id=1,
            )
            db.session.add(teaches)
        
        if not Course.query.filter_by(course_id=1).first():
            course = Course(
                course_id=1,
                stream_id=default_stream.id
            )

        db.session.commit()
    
    return app

app = create_app()

from application.routes import *

if __name__ == '__main__':
    app.run(debug=True)

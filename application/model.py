from application.database import db

# ------------------- Main Tables -------------------
class Answer(db.Model):
    __tablename__ = 'answer'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question_id = db.Column(db.Integer, nullable=False)
    exam_id = db.Column(db.Integer,nullable = False)
    student_id = db.Column(db.Integer, nullable=False)
    marks = db.Column(db.Integer,nullable = False)
    
    def __repr__(self):
        return f'<Stream {self.name}>'
    
    
class Stream(db.Model):
    __tablename__ = 'stream'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    
    # Relationships
    students = db.relationship('Student', back_populates='stream')
    faculty = db.relationship('Faculty', back_populates='stream')
    courses = db.relationship('Course', back_populates='stream')

    def __repr__(self):
        return f'<Stream {self.name}>'


class Student(db.Model):
    __tablename__ = 'student'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    year = db.Column(db.Integer, nullable=False)
    section = db.Column(db.String, nullable=False)
    stream_id = db.Column(db.Integer, db.ForeignKey('stream.id'), nullable=False)
    
    # Relationships
    stream = db.relationship('Stream', back_populates='students')

    def __repr__(self):
        return f'<Student {self.id} - Year {self.year}>'


class Faculty(db.Model):
    __tablename__ = 'faculty'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    stream_id = db.Column(db.Integer, db.ForeignKey('stream.id'), nullable=False)
    name = db.Column(db.String, nullable=False)
    passcode = db.Column(db.String, nullable=False)
    
    # Relationships
    stream = db.relationship('Stream', back_populates='faculty')

    def __repr__(self):
        return f'<Faculty {self.name}>'


class Teaches(db.Model):
    __tablename__ = 'teaches'
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'), primary_key=True)
    year = db.Column(db.Integer, primary_key=True, nullable=False)
    section = db.Column(db.String, primary_key=True, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.course_id'), primary_key=True)

    def __repr__(self):
        return f'<Teaches Faculty {self.faculty_id} - Course {self.course_id}>'


class Course(db.Model):
    __tablename__ = 'course'
    course_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    stream_id = db.Column(db.Integer, db.ForeignKey('stream.id'), nullable=False)
    
    # Relationships
    stream = db.relationship('Stream', back_populates='courses')

    def __repr__(self):
        return f'<Course {self.course_id}>'


class Exam(db.Model):
    __tablename__ = 'exam'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    year = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String,nullable=False)
    
    date = db.Column(db.Date,nullable=False) 
    
    courseID = db.Column(db.String,nullable = False)
    section = db.Column(db.String, nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=False)
    max_marks = db.Column(db.Integer, nullable=False)
    co1 = db.Column(db.Integer, nullable=True)
    co2 = db.Column(db.Integer, nullable=True)
    co3 = db.Column(db.Integer, nullable=True)
    co4 = db.Column(db.Integer, nullable=True)
    co5 = db.Column(db.Integer, nullable=True)
    co6 = db.Column(db.Integer, nullable=True)
    
    def __repr__(self):
        return f'<Exam {self.id} - Faculty {self.faculty_id}>'


class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exam.id'), nullable=False)
    co = db.Column(db.Integer, nullable=False)
    marks = db.Column(db.Integer,nullable = False)
    
    def __repr__(self):
        return f'<Question {self.id} - Exam {self.exam_id} CO {self.co}>'

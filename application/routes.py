from flask import render_template, request, redirect, url_for, flash, session, jsonify, send_file
from app import app, db
from datetime import datetime
from application.model import *
from bokeh.plotting import figure, show, output_file
from bokeh.embed import components
from plotly.graph_objs import Bar, Figure
import json
import plotly


import pandas as pd
import io

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        facultyID = request.form.get('facultyID')
        password = request.form.get('password')
        
        faculty = Faculty.query.filter_by(id = facultyID).first()
        if(faculty!=None):
            if(faculty.passcode == password):
                session['faculty_id'] = faculty.id
                session['faculty_name'] = faculty.name
                return redirect(url_for("landingPage"))
        else:
            return render_template('login.html')
        
@app.route("/logout", methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route("/landingPage",methods = ['GET',"POST"])
def landingPage():
    session['exam_id'] = None
    if(request.method == 'POST'):
        return redirect(url_for('landingPage'))
    faculty = Faculty.query.filter_by(id = session['faculty_id']).first()
    exams  = Exam.query.filter_by(faculty_id = session['faculty_id']).all()
    
    teaches = Teaches.query.filter_by(faculty_id = session['faculty_id']).all()
    return render_template('landing.html',faculty = faculty,exams = exams,teaches = teaches)


@app.route('/landingPage/new-exam',methods = ['POST'])
def new_exam():
    
    facultyID = session['faculty_id']
    
    year = request.form.get('year')
    section = request.form.get('section')
    
    date_string = request.form.get('date')
    date = datetime.strptime(date_string, '%Y-%m-%d').date()
    
    name = request.form.get('name')
    courseID = request.form.get('courseID')
    co1 = int(request.form.get('co1'))
    co2 = int(request.form.get('co2'))
    co3 = int(request.form.get('co3'))
    co4 = int(request.form.get('co4'))
    co5 = int(request.form.get('co5'))
    co6 = int(request.form.get('co6'))
    
    newExam = Exam(
        year = year,
        section = section,
        date = date,
        name = name,
        courseID = courseID,
        co1 = co1,
        co2 = co2,
        co3 = co3,
        co4 = co4,
        co5 = co5,
        co6 = co6,
        max_marks = co1+co2+co3+co4+co5+co6,
        faculty_id = facultyID
    )
    
    exams  = Exam.query.filter_by(faculty_id = session['faculty_id']).all()
    
    db.session.add(newExam)
    db.session.commit()
    return render_template('landing.html',faculty = facultyID,exams = exams)



@app.route("/landingPage/examsDetails", methods = ['GET','POST'])
def examsDetails():
    if(request.method == "GET"):
        examID = request.args.get('examID')
        session["exam_id"] = examID 
        exam = Exam.query.filter_by(id = examID).first()
    if(request.method == "POST"):
        exam = Exam.query.filter_by(id = session["exam_id"]).first()
        print(f"session {exam}")
        student_s = request.form.getlist('student_ids[]')
        question_s = request.form.getlist('question_ids[]')
        marks = request.form.getlist('marks[]')
        changesMade = len(student_s)
        print(f"changesMade {changesMade}")
        
        for i in range(changesMade):
            student_id = int(student_s[i])
            mark = int(marks[i])
            question_id = int(question_s[i])
            print(f"{student_id} \n {question_id} \n {mark}")
            answer = Answer.query.filter_by(student_id=student_id, question_id=question_id, exam_id = exam.id).first()
            answer.marks = int(mark)
            db.session.commit()
                       
    faculty_id = session['faculty_id']
    faculty = Faculty.query.filter_by(id = faculty_id).first()
    
    Answers = Answer.query.filter_by(exam_id = exam.id).all()
    examAttendees = len(Answers)
    co=[0 for _ in range(6)]
    questions = Question.query.filter_by(exam_id = exam.id)
    for q in questions:
        coAnswers = [ans for ans in Answers if ans.question_id == q.id ]
        for i in coAnswers:
            co[q.co-1]+=i.marks
    for i in range(6):
        if examAttendees!=0:
            co_attribute = f"co{i+1}"  
            co_value = getattr(exam, co_attribute, None)
            co[i] = co[i]*100/(examAttendees*int(co_value))
    COs = ['CO1','CO2', 'CO3', 'CO4', 'CO5', 'CO6']
    fig = Figure(
        data=[Bar(x=COs, y=co, marker_color='rgba(55, 128, 191, 0.6)')],
        layout=dict(
            title="",
            xaxis=dict(title=""),
            yaxis=dict(title=""),
            height=250,
            width=500,
            margin=dict(l=20, r=20, t=40, b=30)
        )
    )
    
    plotly_chart_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    top_marks_list = Answer.query.filter_by(exam_id = session["exam_id"]).order_by(Answer.marks.desc()).limit(3).all()
    top_marks=[]
    for i in top_marks_list:
        top_student = Student.query.filter_by(id = i.student_id).first()
        top_marks.append({"student_name":top_student.name,
                          "marks":i.marks,
                          "student_id":i.student_id})
    stream = Stream.query.filter_by(id=faculty.stream_id).first()
    students = Student.query.filter_by(year=exam.year, section=exam.section, stream_id=stream.id).all()
    student_answers = []
    
    for student in students:
        answers = Answer.query.filter_by(student_id=student.id, exam_id=exam.id).all()
        student_answers_entry = {
            'studentID': student.id,
            'student_name':student.name,
            'answers': answers,
            'co1': 0,
            'co2': 0,
            'co3': 0,
            'co4': 0,
            'co5': 0,
            'co6': 0,
            'questions': {answer.question_id: answer.marks for answer in answers}
        }
        for answer in answers:
            question = Question.query.filter_by(id=answer.question_id).first()
            student_answers_entry[f'co{question.co}'] += answer.marks
        student_answers.append(student_answers_entry)
    
    questions = Question.query.filter_by(exam_id=exam.id).all()
    return render_template('examDetails.html',
                           facultyName = faculty.name,exam = exam,
                           plotly_chart_json=plotly_chart_json,
                           top_marks = top_marks,
                           students=student_answers, 
                           questions=questions)



@app.route("/landingPage/examEdit", methods=['GET'])
def examEdit():
    exam = Exam.query.filter_by(id=session['exam_id']).first()
    
    faculty_id = session['faculty_id']
    faculty = Faculty.query.filter_by(id=faculty_id).first()
    
    stream = Stream.query.filter_by(id=faculty.stream_id).first()
    
    teaches = Teaches.query.filter_by(faculty_id=faculty_id, year=exam.year, section=exam.section).first()
    
    course = Course.query.filter_by(course_id=exam.courseID).first()
    
    students = Student.query.filter_by(year=exam.year, section=exam.section, stream_id=stream.id).all()
    
    student_answers = []
    
    for student in students:
        answers = Answer.query.filter_by(student_id=student.id, exam_id=exam.id).all()
        student_answers_entry = {
            'studentID': student.id,
            'answers': answers,
            'co1': 0,
            'co2': 0,
            'co3': 0,
            'co4': 0,
            'co5': 0,
            'co6': 0,
            'questions': {answer.question_id: answer.marks for answer in answers}
        }
        for answer in answers:
            question = Question.query.filter_by(id=answer.question_id).first()
            student_answers_entry[f'co{question.co}'] += answer.marks
        student_answers.append(student_answers_entry)
    
    questions = Question.query.filter_by(exam_id=exam.id).all()
    print(exam.id)
    return render_template('entermarks.html', facultyName=faculty.name, exam=exam, students=student_answers, questions=questions)


@app.route("/landingPage/class", methods=['GET'])
def classPage():
    session['year'] = request.args.get("year")
    session['section'] = request.args.get("section")
    session['course_id'] = request.args.get("course_id")
    course = Course.query.filter_by(course_id = session['course_id']).first()
    session['stream_id'] = course.stream_id
    teaches = Teaches.query.filter(Teaches.faculty_id == session["faculty_id"],
                                   Teaches.section == session['section'],
                                   Teaches.year == session['year'],
                                   Teaches.course_id ==session['course_id']).first()
    
    exams = Exam.query.filter(Exam.year == session['year'],
                              Exam.faculty_id == session['faculty_id'],
                              Exam.section == session['section']).all()


    questions = []
    for exam in exams:
        questions.extend(Question.query.filter_by(exam_id=exam.id).all())
    
    co = [[0,0] for i in range(6)] 
    for question in questions:
        answers = Answer.query.filter_by(question_id=question.id).all()
        marks=0
        for i in range(len(answers)):
            marks+=answers[i].marks
        marks/=len(answers)
        percentage = (marks/question.marks)*100
        co[question.co-1][0]+=percentage
        co[question.co-1][1]+=1
        
        coFinal=[]
        for i in range(6):
            if(co[i][1]==0):
                coFinal.append(int())
            else:
                co[i][0]/=100
                # print(f"co[i][0]{co[i][0]}")
                # print(f"co[i][1]{co[i][1]}")
                coFinal.append(co[i][0]/co[i][1])
            
                
    fig = Figure(
        data=[Bar(x=coFinal, y=[1,2,3,4,5,6], marker_color='rgba(55, 128, 191, 0.6)')],
        layout=dict(
            title="",
            xaxis=dict(title=""),
            yaxis=dict(title=""),
            height=250,
            width=500,
            margin=dict(l=20, r=20, t=40, b=30)
        )
    )
    
    plotly_chart_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
                
    students = Student.query.filter(Student.year == session['year'],
                                    Student.stream_id == session['stream_id'],
                                    Student.section == session['section']).all()
    
    minmaxStudentCOs=[]
    for student in students:
        answerCO=[0 for _ in range(6)]
        for i in range(6):
            answers = Answer.query.filter(Answer.student_id==student.id,
                                          Answer.question_id.in_([q.id for q in questions if q.co==i+1 ])).all()
            for answer in answers:
                answerCO[i]+=answer.marks
        
        max=0
        min=99999
        avg=0
        for i in range(6):
            avg+=answerCO[i]
            if answerCO[i]>max:
                max=i+1
            elif answerCO[i]<min:
                min=i+1
        avg/=6
        
        minmaxStudentCOs.append({"student_name":student.name,
                                 "max_co":max,
                                 "min_co":min,
                                 "avg_co":avg})
        
        
    for exam in exams:
        answers = Answer.query.filter(Answer.exam_id == exam.id).all()
        
    visitedStudents=set()
    studentTotals = []
    for answer in answers:
        if answer.student_id not in visitedStudents:
            student = Student.query.filter_by(id = answer.student_id).first()
            visitedStudents.add(answer.student_id)
            studentTotals.append({"student_id":student.id,
                                   "student_name":student.name,
                                   "marks":answer.marks})
            print(f" studentTotals : {studentTotals}") 
        else:
            for studentTotal in studentTotals:
                if studentTotal["student_id"]==answer.student_id:
                    studentTotal["marks"]+=answer.marks
    
    for i in range(len(studentTotals)):
        for j in range(len(studentTotals)-1):
            if studentTotals[j]["marks"]<studentTotals[j+1]["marks"]:
                studentTotals[j],studentTotals[j+1]=studentTotals[j+1],studentTotals[j]
    
    
    print(f" studentTotals : {studentTotals}") 

    top_marks = studentTotals[:3]
    print(f"minmaxStudentCOs\n {minmaxStudentCOs}")
    return render_template("classDetail.html",
                            cos=coFinal,
                            minmaxStudentCOs=minmaxStudentCOs,
                            top_marks=top_marks,
                            teaches = teaches,
                            plotly_chart_json=plotly_chart_json)
    
    
from flask import jsonify, request

@app.route('/search/exams', methods=['GET'])
def search_exams():
    query = request.args.get('q', '').lower()
    if query:
        filtered_exams = [exam for exam in Exam.query.filter_by(faculty_id = session['faculty_id']).all() if query in exam.name.lower()]
    else:
        filtered_exams = Exam.query.filter_by(faculty_id = session['faculty_id']).all()  # Show all exams if no query

    return render_template('partials/exam_results.html', exams=filtered_exams)



@app.route('/download', methods=['POST'])
def download_file():
    data = request.json  # Get data from client-side
    file_format = data.get('format')  # "csv" or "excel"
    table_data = data.get('table_data')  # List of table rows (as dictionaries)

    # Convert table data into a DataFrame
    df = pd.DataFrame(table_data)

    if file_format == 'csv':
        # Generate CSV
        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)
        return send_file(io.BytesIO(output.getvalue().encode()), 
                         mimetype="text/csv", 
                         as_attachment=True, 
                         download_name="report.csv")
    elif file_format == 'excel':
        # Generate Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Report')
        output.seek(0)
        return send_file(output, 
                         mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
                         as_attachment=True, 
                         download_name="report.xlsx")
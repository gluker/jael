import json, bbcode
from sympy import *
import re
from parse import *
from datetime import datetime
from flask import render_template, request, redirect, url_for, jsonify,make_response
from database import db_session
from . import app
from models import Course, ProblemSet, Problem, Requirement
from forms import ProblemSetForm, ProblemForm

@app.route('/')
@app.route('/courses/')
def showAllCourses():
    courses = db_session.query(Course).all()
    return render_template("showallcourses.html",courses=courses)

###  Views for courses ###
@app.route('/courses/new/', methods=['POST','GET'])
def newCourse():
    if request.method == "POST":
        name = request.form['name']
        course = Course(name=name)
        db_session.add(course)
        db_session.commit()
        return redirect(url_for('showAllCourses'))
    return render_template("newcourse.html")

@app.route('/courses/<int:course_id>/')
@app.route('/courses/<int:course_id>/psets/')
def showCourse(course_id):
    course = db_session.query(Course).get(course_id)
    psets = course.problemsets
    return render_template("showcourse.html",course=course,psets=psets)

@app.route('/courses/<int:course_id>/edit', methods=['GET','POST'])
def editCourse(course_id):
    course = db_session.query(Course).get(course_id)
    if request.method == "POST":
        course.name = request.form['name']
        db_session.commit()
        return redirect(url_for("showCourse",course_id=course.id))
    return render_template("editcourse.html",course=course)

@app.route('/courses/<int:course_id>/delete/', methods=['GET','POST'])
def deleteCourse(course_id):
    course = db_session.query(Course).get(course_id)
    if request.method == "POST":
        db_session.delete(course)
        db_session.commit()
        return redirect(url_for("showAllCourses"))
    return render_template("deletecourse.html",course=course)

### Views for Problem Sets ###
@app.route('/courses/<int:course_id>/psets/new/', methods=['GET','POST'])
def newPSet(course_id):
    course = db_session.query(Course).get(course_id)
    form = ProblemSetForm(request.form)
    if request.method == "POST" and form.validate():
        print form
        pset = ProblemSet()
        pset.title = form.title.data
        pset.opens = form.opens.data
        pset.due = form.due.data
        pset.course_id=course.id
        course.problemsets.append(pset)
        db_session.commit()
        return redirect(url_for("showCourse",course_id=course.id))
    return render_template("newpset.html",course=course)

@app.route('/courses/<int:course_id>/psets/<int:pset_id>/')
@app.route('/courses/<int:course_id>/psets/<int:pset_id>/problems/')
def showPSet(course_id,pset_id):
    course = db_session.query(Course).get(course_id)
    pset = db_session.query(ProblemSet).get(pset_id)
    problems = pset.problems
    return render_template("showpset.html",course=course,pset=pset,problems=problems)

@app.route('/courses/<int:course_id>/psets/<int:pset_id>/edit/',methods=['POST','GET'])
def editPSet(course_id,pset_id):
    course = db_session.query(Course).get(course_id)
    pset = db_session.query(ProblemSet).get(pset_id)
    form = ProblemSetForm(request.form)
    if request.method == "POST" and form.validate():
        pset.title = form.title.data
        pset.opens = form.opens.data
        pset.due = form.due.data
        db_session.commit()
        return redirect(url_for('showPSet',course_id=course.id,pset_id=pset.id))
    return render_template("editpset.html",course=course,pset=pset)

@app.route('/courses/<int:course_id>/psets/<int:pset_id>/delete/', methods=["GET",'POST'])
def deletePSet(course_id,pset_id):
    pset = db_session.query(ProblemSet).get(pset_id)
    if request.method == "POST":
        db_session.delete(pset)
        db_session.commit()
        return redirect(url_for('showCourse',course_id=course_id))
    return render_template("deletepset.html",course=course,pset=pset)

### Views for Problems ###
@app.route('/courses/<int:course_id>/psets/<int:pset_id>/problems/new/', methods=['GET','POST'])
def newProblem(course_id, pset_id):
    course = db_session.query(Course).get(course_id)
    pset = db_session.query(ProblemSet).get(pset_id)
    form = ProblemForm(request.form)
    if request.method == "POST" and form.validate():
        problem = Problem(text=request.form['text'])
        pset.problems.append(problem)
        for cnt in range(1,int(request.form['counter'])+1):
           req = Requirement(condition = request.form['condition'+str(cnt)],
                        comment = request.form['comment'+str(cnt)])
           problem.requirements.append(req) 
        db_session.commit()
        return redirect(url_for('showPSet',course_id=course.id,pset_id=pset.id))
    return render_template("newproblem.html",course=course,pset=pset)

@app.route('/courses/<int:course_id>/psets/<int:pset_id>/problems/newvis/', methods=['GET','POST'])
def newProblemVisual(course_id,pset_id):
    return render_template("newproblem_visual.html")

@app.route('/courses/<int:course_id>/psets/<int:pset_id>/problems/<int:problem_id>/')
def showProblem(course_id,pset_id,problem_id):
    course = db_session.query(Course).get(course_id)
    pset = db_session.query(ProblemSet).get(pset_id)
    problem = db_session.query(Problem).get(problem_id)
    text = bb_to_html(problem.text)
    return render_template("showproblem.html",course=course,pset=pset,problem=problem,text=text)

@app.route('/courses/<int:course_id>/psets/<int:pset_id>/problems/<int:problem_id>/edit/', methods=['GET','POST'])
def editProblem(course_id,pset_id,problem_id):
    course = db_session.query(Course).get(course_id)
    pset = db_session.query(ProblemSet).get(pset_id)
    problem = db_session.query(Problem).get(problem_id)
    if request.method == "POST":
        problem.text = request.form['text']
        db_session.commit()
        return redirect(url_for('showProblem',course_id=course.id,pset_id=pset.id,problem_id=problem.id))
    return render_template("editproblem.html",course=course,pset=pset,problem=problem)

@app.route('/courses/<int:course_id>/psets/<int:pset_id>/problems/<int:problem_id>/delete/', methods=["GET","POST"])
def deleteProblem(course_id,pset_id,problem_id):
    course = db_session.query(Course).get(course_id)
    pset = db_session.query(ProblemSet).get(pset_id)
    problem = db_session.query(Problem).get(problem_id)
    if request.method == "POST":
        db_session.delete(problem)
        db_session.commit()
        return redirect(url_for('showPSet',course_id=course.id,pset_id=pset.id))
    return render_template("deleteproblem.html",course=course,pset=pset,problem=problem)


@app.route('/courses/<int:course_id>/psets/<int:pset_id>/problems/<int:problem_id>/check/', methods=["POST","GET"])
def checkProblem(course_id,pset_id,problem_id):
    problem = db_session.query(Problem).get(problem_id)
    messages = []
    total = len(request.form)
    correct = 0.0
    for req in problem.requirements:
        cond = req.condition
        for key in request.form.keys():
            try:
                check_input(request.form[key])
                cond = cond.replace(key,request.form[key])
            except Exception as ext:
                print "Bad input catched!"
                print ext
                return jsonify(errors = ["Please check the input!"])
        try:
            res = sympify(cond)
            if res:
                correct += 1
            else:
                messages.append(req.comment)
        except:
            print "Sympify exception"
            return jsonify(errors = ["Please check the input!"])

    return jsonify(messages = messages, rate = int((correct/total)*100))


def check_input(input):
    whitelist = ['abs','sin','cos','tan']
    if re.search('[\?_">\\<=\'{}\[\]]',input):
        raise Exception("Unwanted symbols")

    for word in re.findall('[a-zA-Z]+',input):
        if word not in whitelist:
            raise Exception("Unallowed word: %s" % word)

def bb_to_html(bbtext):
    parser = bbcode.Parser()
    parser.newline = '<br>'
    def input_formatter(tag_name, value, options, parent, context):
        tag ='<input type="'+options['type']
        if 'name' in options:
            tag+='" name="'+options['name']
        if 'value' in options:
            tag+='" value="'+options['value']

        return '<input type="%s" name="%s" value="%s" >' %(options['type'],options['name'],options['value'])
    
            
    parser.add_formatter('input',input_formatter,standalone = True)
    return parser.format(bbtext)

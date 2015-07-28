from flask import render_template
from . import app
from . import models

### dummy data for testing ###
courses = [{'id':1, 'name':"Complicated Math"},{'id':2, 'name':"Even more complicated math"}]
course = courses[0]
psets = [{'id':1, 'title':"Firsr week of course", 'course_id':1},
            {'id':2, 'title':"Second", 'course_id':1}]
pset = psets[1]
problems = [{'id':1,'text':"Text for 1<sup>st</sup> problem"},{'id':2,'text':"<h3>Problem</h3> blabla"}]
problem = problems[0]

@app.route('/')
@app.route('/courses/')
def showAllCourses():
    return render_template("showallcourses.html",courses=courses)

###  Views for courses ###
@app.route('/courses/new/')
def newCourse():
    return render_template("newcourse.html")

@app.route('/courses/<int:course_id>')
@app.route('/courses/<int:course_id>/psets/')
def showCourse(course_id):
    return render_template("showcourse.html",course=course,psets=psets)

@app.route('/courses/<int:course_id>/edit')
def editCourse(course_id):
    return render_template("editcourse.html",course=course)

@app.route('/courses/<int:course_id>/delete/')
def deleteCourse(course_id):
    return render_template("deletecourse.html",course=course)

### Views for Problem Sets ###
@app.route('/courses/<int:course_id>/psets/new/')
def newPSet(course_id):
    return render_template("newpset.html",course=course)

@app.route('/courses/<int:course_id>/psets/<int:pset_id>/')
@app.route('/course/<int:course_id>/psets/<int:pset_id>/problems/')
def showPSet(course_id,pset_id):
    return render_template("showpset.html",course=course,pset=pset,problems=problems)

@app.route('/courses/<int:course_id>/psets/<int:pset_id>/edit/')
def editPSet(course_id,pset_id):
    return render_template("editpset.html",course=course,pset=pset)

@app.route('/courses/<int:course_id>/psets/<int:pset_id>/delete/')
def deletePSet(course_id,pset_id):
    return render_template("deletepset.html",course=course,pset=pset)

### Views for Problems ###
@app.route('/course/<int:course_id>/psets/<int:pset_id>/problems/new/')
def newProblem(course_id, pset_id):
    return render_template("newproblem.html",course=course,pset=pset)

@app.route('/courses/<int:course_id>/psets/<int:pset_id>/problems/<int:problem_id>/')
def showProblem(course_id,pset_id,problem_id):
    return render_template("showproblem.html",course=course,pset=pset,problem=problem)

@app.route('/courses/<int:course_id>/psets/<int:pset_id>/problems/<int:problem_id>/edit/')
def editProblem(course_id,pset_id,problem_id):
    return render_template("editproblem.html",course=course,pset=pset,problem=problem)

@app.route('/courses/<int:course_id>/psets/<int:pset_id>/problems/<int:problem_id>/delete/')
def deleteProblem(course_id,pset_id,problem_id):
    return render_template("deleteproblem.html",course=course,pset=pset,problem=problem)

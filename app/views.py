from . import app
from . import models

@app.route('/')
@app.route('/courses/')
def showAllCourses():
    return "List of all courses"

###  Views for courses ###
@app.route('/courses/new/')
def newCourse():
    return "Page for creating a new course"

@app.route('/courses/<int:course_id>')
@app.route('/courses/<int:course_id>/psets/')
def showCourse(course_id):
    return "Page for course %s" % course_id

@app.route('/courses/<int:course_id>/edit')
def editCourse(course_id):
    return "Page for editing course %s" % course_id

@app.route('/courses/<int:course_id>/delete/')
def deleteCourse(course_id):
    return "Page for deleting course %s" % course_id

### Views for Problem Sets ###
@app.route('/courses/<int:course_id>/psets/new/')
def newPSet(course_id):
    return "create a new pset"

@app.route('/courses/<int:course_id>/psets/<int:pset_id>/')
@app.route('/course/<int:course_id>/psets/<int:pset_id>/problems/')
def showPSet(course_id,pset_id):
    return "Show pset %s" % pset_id 

@app.route('/courses/<int:course_id>/psets/<int:pset_id>/edit/')
def editPSet(course_id,pset_id):
    return "edit pset"

@app.route('/courses/<int:course_id>/psets/<int:pset_id>/delete/')
def deletePSet(course_id,pset_id):
    return "Delete PSet"

### Views for Problems ###
@app.route('/course/<int:course_id>/psets/<int:pset_id>/problems/new/')
def newProblem(course_id, pset_id, problem_id):
    return "Create a new Problem"

@app.route('/courses/<int:course_id>/psets/<int:pset_id>/problems/<int:problem_id>/')
def showProblem(course_id,pset_id,problem_id):
    return "Show Problem"

@app.route('/courses/<int:course_id>/psets/<int:pset_id>/problems/<int:problem_id>/edit/')
def editProblem(course_id,pset_id,problem_id):
    return "Edit Problem"

@app.route('/courses/<int:course_id>/psets/<int:pset_id>/problems/<int:problem_id>/delete/')
def deleteProblem(course_id,pset_id,problem_id):
    return "Delete Problem"

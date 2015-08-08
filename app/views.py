import json
import httplib2
import requests
from sympy import sympify, limit, oo, symbols
from flask import render_template, request, redirect, url_for, jsonify,make_response, session
from database import db_session
from . import app
from models import Course, ProblemSet, Problem, Requirement
from forms import ProblemSetForm, ProblemForm
from utils import bb_to_html, check_input, state_gen
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError, OAuth2Credentials 

PATH_TO_CLIENT_SECRET = 'instance/client_secret.json'

CLIENT_ID = json.loads(
    open(PATH_TO_CLIENT_SECRET, 'r').read())['web']['client_id']
APPLICATION_NAME = "Jaot"

@app.route('/')
@app.route('/courses/')
def showAllCourses():
    courses = db_session.query(Course).all()
    return render_template("showallcourses.html",courses=courses)
    
@app.route('/login/')
def showLogin():
    state = state_gen()
    session['state'] = state
    return render_template("login.html", STATE=state)
    
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data
    try:
        oauth_flow = flow_from_clientsecrets(PATH_TO_CLIENT_SECRET, scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
        
    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
        
    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response
    
    stored_credentials = session.get('credentials')
    stored_gplus_id = session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    session['credentials'] = credentials.to_json()
    session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    session['username'] = data['name']
    session['picture'] = data['picture']
    session['email'] = data['email']
    return "it's fine!"
    
    

@app.route('/gdisconnect')
def gdisconnect():
        # Only disconnect a connected user.
    credentials = OAuth2Credentials.from_json(session.get('credentials'))
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset the user's sesson.
        del session['credentials']
        del session['gplus_id']
        del session['username']
        del session['email']
        del session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response
        
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
    ten = 10
    for req in problem.requirements:
        cond = req.condition
        for key in request.form.keys():
            try:
                check_input(request.form[key])
                cond = cond.replace(key,request.form[key])
            except Exception as ext:
                print "Bad input catched!"
                print ext
                return jsonify(errors = ["Please check the input!",ext.__str__()])
        try:
            x,y = symbols('x y')
            check_input(cond)
            res = sympify(cond)
            if res:
                correct += 1
            else:
                messages.append(req.comment)
        except Exception as e:
            print "Sympify exception{e}".format(e=e)
            return jsonify(errors = ["Please check the input!"])

    return jsonify(messages = messages, rate = int((correct/total)*100))


from functools import wraps
import json
import httplib2
import requests
from sympy import sympify, limit, oo, symbols
from flask import render_template, request, redirect, url_for, jsonify,make_response, session, flash, abort, current_app
from database import db_session
from . import app
from models import Course, ProblemSet, Problem, Requirement, User
from forms import ProblemSetForm, ProblemForm, CourseForm, UserForm
from utils import bb_to_html, check_input, state_gen, create_user, load_user, get_user_id, check_permissions, login_manager
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError, OAuth2Credentials
from flask_oauth import OAuth
from flask_login import login_user, login_required, current_user, logout_user
from flask_principal import Principal, Permission, RoleNeed, identity_changed, identity_loaded, Identity, UserNeed


PATH_TO_CLIENT_SECRET = 'instance/client_secret.json'

CLIENT_ID = json.loads(
    open(PATH_TO_CLIENT_SECRET, 'r').read())['web']['client_id']
CLIENT_SECRET = json.loads(
    open(PATH_TO_CLIENT_SECRET, 'r').read())['web']['client_secret']
APPLICATION_NAME = "Jaot"

login_manager.init_app(app)
login_manager.login_view = 'login'

principals = Principal(app)
admin_permission = Permission(RoleNeed('admin'))
oauth = OAuth()
    
facebook = oauth.remote_app('facebook',
    base_url = "https://graph.facebook.com/v2.3/",
    request_token_url = None,
    access_token_url = "/oauth/access_token",
    authorize_url="https://www.facebook.com/dialog/oauth",
    consumer_key = app.config['FB_APP_KEY'],
    consumer_secret = app.config['FB_APP_SECRET'],
    request_token_params = {'scope':'email'}
    )

@facebook.tokengetter
def get_facebook_token(token=None):
    return session.get('facebook_token')

@app.route("/fblogin")
def fblogin():
    return facebook.authorize(callback = app.config['APP_DOMAIN']+'login_handler/')

@app.route("/login_handler/")
@facebook.authorized_handler
def loginHandler(resp):
    session['facebook_token'] = resp['access_token']
    r = requests.get("https://graph.facebook.com/v2.3/oauth/access_token"+
        "?client_id="+facebook.consumer_key+
        "&client_secret="+facebook.consumer_secret+
        "&grant_type=client_credentials")
    app_token = json.loads(r.text)["access_token"]
    r = requests.get("https://graph.facebook.com/debug_token"+
        "?input_token="+session['facebook_token']+
        "&access_token="+app_token)
    session["facebook_id"] = json.loads(r.text)["data"]["user_id"]
    r = requests.get(facebook.base_url+session['facebook_id']+"?access_token="+session['facebook_token']+"&fields=email,name")
    email = json.loads(r.text)["email"]

    try:
        user_id = get_user_id(email)
        user = load_user(user_id)
        login_user(user)
        flash("Logged in as "+current_user.email)
    except Exception as e:
        print "can't get user"
        print e
        try:
            user = create_user(email)
            login_user(user)
            flash("Wellcome")
        except Exception as e:
            print "can't create"
            print e
            abort(403)
    identity_changed.send(current_app._get_current_object(), identity=Identity(user.id))
    return redirect(url_for('showAllCourses'))
    
@app.route('/')
@app.route('/courses/')
@login_required
def showAllCourses():
    if current_user.type == "admin":
        courses = db_session.query(Course).all()
    else:
        courses = current_user.courses
    return render_template("showallcourses.html",courses=courses)
    
@app.route('/logout/')
@login_required
def logout():
    logout_user()
    for key in ('identity.name', 'identity.auth_type'):
        session.pop(key, None)
    flash("Logged out")
    return redirect(url_for('login'))

@app.route('/login/')
def login():
    if current_user.is_authenticated():
        flash("Already logged in")
        return redirect(url_for("showAllCourses"))
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

    try:
        session['user_id'] = get_user_id(session['email'])
        flash("Logged in as "+session['email'])
    except Exception as e:
        print "can't get user"
        print e
        try:
            user = create_user(session)
            session['user_id'] = user
            flash("Wellcome, "+session['username'])
        except Exception as e:
            print "can't create"
            flash("Sum Tin Wong")
            print e
    flash("Logged in as "+session["email"])
    return redirect(url_for('showAllCourses'))
   
    
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
        
@app.route('/users/')
@login_required
@admin_permission.require(http_exception=403)
def showUsers():
    users = db_session.query(User).all()
    courses = db_session.query(Course).all()
    return render_template("showusers.html", users=users,courses=courses)

@app.route('/users/<int:user_id>/delete/', methods=['POST','GET'])
@admin_permission.require(http_exception=403)
def deleteUser(user_id):
    user = db_session.query(User).get(user_id)
    if user == None:
        abort(404)
    if request.method == "POST":
        db_session.delete(user)
        db_session.commit()
        flash("User deleted")
        return redirect(url_for('showUsers'))
    return render_template('deleteuser.html')

@app.route('/users/<int:user_id>/edit/', methods=['POST','GET'])
@admin_permission.require(http_exception=403)
def editUser(user_id):
    user = db_session.query(User).get(user_id)
    if user == None:
        abort(404)
    form = UserForm(request.form,user)
    courses = db_session.query(Course).all()
    if request.method == "POST" and form.validate():
        user.type = form.type.data
        user.courses = []
        for field in request.form:
            if request.form[field] == "on":
                course = db_session.query(Course).get(int(field))
                user.courses.append(course)
        db_session.commit()
        return redirect(url_for("showUsers"))
    return render_template("edituser.html",user=user,courses=courses, form=form)
###  Views for courses ###
@app.route('/courses/new/', methods=['POST','GET'])
@admin_permission.require(http_exception=403)
def newCourse():
    form = CourseForm(request.form)
    if request.method == "POST" and form.validate():
        name = form.name.data
        course = Course(name=name)
        db_session.add(course)
        db_session.commit()
        return redirect(url_for('showAllCourses'))
    return render_template("newcourse.html",form=form)

@app.route('/courses/<int:course_id>/')
@app.route('/courses/<int:course_id>/psets/')
@login_required
def showCourse(course_id):
    course = db_session.query(Course).get(course_id)
    if course == None:
        abort(404)
    psets = course.problemsets
    return render_template("showcourse.html",course=course,psets=psets,perm=check_permissions(course.id,session['user_id']))

@app.route('/courses/<int:course_id>/edit', methods=['GET','POST'])
@login_required
@admin_permission.require(http_exception=403)
def editCourse(course_id):
    course = db_session.query(Course).get(course_id)
    if course == None:
        abort(404)
    if request.method == "POST":
        course.name = request.form['name']
        db_session.commit()
        return redirect(url_for("showCourse",course_id=course.id))
    return render_template("editcourse.html",course=course)

@app.route('/courses/<int:course_id>/delete/', methods=['GET','POST'])
@login_required
@admin_permission.require(http_exception=403)
def deleteCourse(course_id):
    course = db_session.query(Course).get(course_id)
    if course == None:
        abort(404)
    if request.method == "POST":
        db_session.delete(course)
        db_session.commit()
        return redirect(url_for("showAllCourses"))
    return render_template("deletecourse.html",course=course)

### Views for Problem Sets ###
@app.route('/courses/<int:course_id>/psets/new/', methods=['GET','POST'])
@login_required
@admin_permission.require(http_exception=403)
def newPSet(course_id):
    course = db_session.query(Course).get(course_id)
    if course == None:
        abort(404)
    form = ProblemSetForm(request.form)
    if request.method == "POST" and form.validate():
        pset = ProblemSet()
        pset.title = form.title.data
        pset.opens = form.opens.data
        pset.due = form.due.data
        pset.course_id=course.id
        course.problemsets.append(pset)
        db_session.commit()
        return redirect(url_for("showCourse",course_id=course.id))
    return render_template("newpset.html",course=course,form=form)

@app.route('/courses/<int:course_id>/psets/<int:pset_id>/')
@app.route('/courses/<int:course_id>/psets/<int:pset_id>/problems/')
@login_required
def showPSet(course_id,pset_id):
    course = db_session.query(Course).get(course_id)
    pset = db_session.query(ProblemSet).get(pset_id)
    if None in [pset,course] or pset.course_id != course_id:
        abort(404)
    if course not in current_user.courses and current_user.type == "student":
        abort(403)
    problems = pset.problems
    perm = "view" if current_user.type != "admin" else "edit"
    return render_template("showpset.html",course=course,pset=pset,problems=problems, perm=perm)

@app.route('/courses/<int:course_id>/psets/<int:pset_id>/edit/',methods=['POST','GET'])
@login_required
@admin_permission.require(http_exception=403)
def editPSet(course_id,pset_id):
    course = db_session.query(Course).get(course_id)
    pset = db_session.query(ProblemSet).get(pset_id)
    if None in [pset,course] or pset.course_id != course_id:
        abort(404)
    form = ProblemSetForm(request.form)
    if request.method == "POST" and form.validate():
        pset.title = form.title.data
        pset.opens = form.opens.data
        pset.due = form.due.data
        db_session.commit()
        return redirect(url_for('showPSet',course_id=course.id,pset_id=pset.id))
    return render_template("editpset.html",course=course,pset=pset)

@app.route('/courses/<int:course_id>/psets/<int:pset_id>/delete/', methods=["GET",'POST'])
@login_required
@admin_permission.require(http_exception=403)
def deletePSet(course_id,pset_id):
    pset = db_session.query(ProblemSet).get(pset_id)
    if pset == None or pset.course_id != course_id:
        abort(404)
    if request.method == "POST":
        db_session.delete(pset)
        db_session.commit()
        return redirect(url_for('showCourse',course_id=course_id))
    return render_template("deletepset.html",course=course,pset=pset)

### Views for Problems ###
@app.route('/courses/<int:course_id>/psets/<int:pset_id>/problems/new/', methods=['GET','POST'])
@login_required
@admin_permission.require(http_exception=403)
def newProblem(course_id, pset_id):
    course = db_session.query(Course).get(course_id)
    pset = db_session.query(ProblemSet).get(pset_id)
    if None in [pset,course] or pset.course_id != course_id:
        abort(404)
    form = ProblemForm(request.form)
    if request.method == "POST" and form.validate():
        problem = Problem(text=form.text.data)
        pset.problems.append(problem)
        for req in form.requirements:
            problem.requirements.append(Requirement(condition = req.condition.data, comment = req.comment.data))
        db_session.commit()
        return redirect(url_for('showPSet',course_id=course.id,pset_id=pset.id))
    return render_template("newproblem.html",course=course,pset=pset,form=form)

@app.route('/courses/<int:course_id>/psets/<int:pset_id>/problems/<int:problem_id>/')
@login_required
def showProblem(course_id,pset_id,problem_id):
    course = db_session.query(Course).get(course_id)
    pset = db_session.query(ProblemSet).get(pset_id)
    problem = db_session.query(Problem).get(problem_id)
    if None in [pset,course,problem] or pset.course_id != course_id or problem.problemset_id != pset_id:
        abort(404)
    if course not in current_user.courses and current_user.type == "student":
        abort(403)
    text = bb_to_html(problem.text)
    next_problem = problem_id+1 if len(pset.problems)>problem_id else None
        
    return render_template("showproblem.html",course=course,pset=pset,problem=problem,text=text,next_problem = next_problem)

@app.route('/courses/<int:course_id>/psets/<int:pset_id>/problems/<int:problem_id>/edit/', methods=['GET','POST'])
@login_required
@admin_permission.require(http_exception=403)
def editProblem(course_id,pset_id,problem_id):
    course = db_session.query(Course).get(course_id)
    pset = db_session.query(ProblemSet).get(pset_id)
    problem = db_session.query(Problem).get(problem_id)
    if None in [pset,course,problem] or pset.course_id != course_id or problem.problemset_id != pset_id:
        abort(404)
    form = ProblemForm(request.form,problem)
    print form.data
    if request.method == "POST" and form.validate():
        problem.text = form.text.data
        problem.requirements = []
        for req in form.requirements:
            problem.requirements.append(Requirement(condition = req.condition.data, comment = req.comment.data))
        db_session.commit()
        return redirect(url_for('showProblem',course_id=course.id,pset_id=pset.id,problem_id=problem.id))
    return render_template("editproblem.html",course=course,pset=pset,problem=problem,form=form)

@app.route('/courses/<int:course_id>/psets/<int:pset_id>/problems/<int:problem_id>/delete/', methods=["GET","POST"])
@login_required
@admin_permission.require(http_exception=403)
def deleteProblem(course_id,pset_id,problem_id):
    course = db_session.query(Course).get(course_id)
    pset = db_session.query(ProblemSet).get(pset_id)
    problem = db_session.query(Problem).get(problem_id)
    if None in [pset,course,problem] or pset.course_id != course_id or problem.problemset_id != pset_id:
        abort(404)
    if request.method == "POST":
        db_session.delete(problem)
        db_session.commit()
        return redirect(url_for('showPSet',course_id=course.id,pset_id=pset.id))
    return render_template("deleteproblem.html",course=course,pset=pset,problem=problem)


@app.route('/courses/<int:course_id>/psets/<int:pset_id>/problems/<int:problem_id>/check/', methods=["POST"])
@login_required
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
            except ValueError as ext:
                return jsonify(errors = ["Please check the input!",ext.__str__()])
            except Exception as ext:
                print ext
                return jsonify(errors = ["Please check the input!"])
        try:
            x,y = symbols('x y')
            check_input(cond)
            res = sympify(cond)
            if res:
                correct += 1
            else:
                messages.append(req.comment)
        except SympifyError as e:
            print "Sympify exception{e}".format(e=e)
            return jsonify(errors = ["Please check the input!"])
        except Exception as e:
            return jsonify(errors = ["Please check the input!"])

    return jsonify(messages = messages, rate = int((correct/total)*100))

@app.errorhandler(404)
def error404(e):
    return render_template('errors/404.html',e=e)
@app.errorhandler(403)
def error404(e):
    return render_template('errors/404.html',e=e)


@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    identity.user = current_user
    if hasattr(current_user, 'id'):
        identity.provides.add(UserNeed(current_user.id))

    # Assuming the User model has a list of roles, update the
    # identity with the roles that the user provides
    identity.provides.add(RoleNeed(current_user.type))


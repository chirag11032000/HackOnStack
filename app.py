import time
from flask import *
from flask_sqlalchemy import *
from passlib.hash import sha256_crypt
from config import *
from models.Users import User
from models.Questions import Question
from models.Answers import Answer

@app.route('/')
def homepage():
    qs = Question.query.all()
    return render_template("index.html",questions=qs)

@app.route('/login/', methods=['POST','GET'])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if not(user):
            flash("This Username doesn't exists!")
            return redirect(url_for('login'))
        else:
            password_correct = sha256_crypt.verify(password, user.password)
            if not(password_correct):
                flash("Wrong password entered!")
                return redirect(url_for('login'))
            else:
                flash("Logged in successfully:)")
                session['username'] = username
                session['u_id'] = user.u_id
                session['logged_in'] = True
        return redirect(url_for('homepage'))

@app.route('/logout/')
def logout():
    session.pop('username', None)
    session.pop('u_id', None)
    session.pop('logged_in', False)
    return redirect(url_for('homepage'))


@app.route('/register/', methods=['POST','GET'])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        username = request.form['username']
        for ch in username:
            if not (ch.isalpha() or ch.isdigit()):
                flash("Invalid Username!")
                return redirect(url_for('register'))
        if User.query.filter_by(username=username).first():
            flash("Username already taken, sorry!")
            return redirect(url_for('register'))
        else:
            password = request.form['password']
            hashed_password = sha256_crypt.hash(password)
            email = request.form['email']
            phone_no = request.form['phone_no']
            if len(phone_no)>12:
                flash("Invalid Phone no!")
                return redirect(url_for('register'))
            for ch in phone_no:
                if not ch.isdigit():
                    flash("Invalid Phone no!")
                    return redirect(url_for('register'))
            bio = request.form['bio']
            dob = request.form['dob']
            try:
              valid_date = time.strptime(dob,'%Y-%m-%d')
            except ValueError:
              flash("Invalid Date of Birth!")
              return redirect(url_for('register'))
            fav_topics = request.form['fav_topics']
            user = User(username = username,
                        password = hashed_password,
                        email = email,
                        phone_no = phone_no,
                        bio = bio,
                        dob = dob)
            db.session.add(user)
            db.session.commit()
            db.session.close()
            flash("Successfully registered!")
            return redirect(url_for('homepage'))

@app.route('/post/question/', methods=['POST','GET'])
def post_question():
    if not("logged_in" in session and session["logged_in"]):
        flash("You need to log in first!")
        return redirect(url_for('login'))
    else:
        if request.method == "GET":
            return render_template("ask_question.html")
        else:
            author_u_id = session['u_id']
            title = request.form['title']
            body = request.form['body']
            post_time = time.strftime('%Y-%m-%d %H:%M:%S')
            upvotes = 0
            question = Question(title = title,
                                body = body,
                                author_u_id = author_u_id,
                                post_time = post_time,
                                upvotes = upvotes)
            db.session.add(question)
            db.session.commit()
            db.session.close()
            flash("Your question has been posted!")
            return redirect(url_for('homepage'))

@app.route('/post/answer/<int:q_id>', methods=['POST'])
def post_answer(q_id):
    if not("logged_in" in session and session["logged_in"]):
        flash("You need to log in first!")
        return redirect(url_for('login'))
    answer_body = request.form["answer"]
    if answer_body != "":
        author_u_id = session["u_id"]
        post_time = time.strftime('%Y-%m-%d %H:%M:%S')
        upvotes = 0
        answer = Answer(q_id = q_id,
                        body = answer_body,
                        author_u_id = author_u_id,
                        post_time = post_time,
                        upvotes = upvotes)
        db.session.add(answer)
        db.session.commit()
        db.session.close()
        flash("Your answer has been posted!")
    else:
        flash("Answer can't be blank!")
    return redirect(url_for("question", q_id = q_id))

@app.route('/question/<int:q_id>')
def question(q_id):
    qs = Question.query.filter_by(q_id=q_id).first()
    ans = Answer.query.filter_by(q_id=q_id).all()
    return render_template("display_question.html", question=qs, answers=ans)

@app.route('/upvote/question/<int:q_id>/<int:u_id>')
def upvote_q(q_id, u_id):
    if not("logged_in" in session and session["logged_in"]):
        flash("You need to log in first!")
        return redirect(url_for('login'))
    qs = Question.query.filter_by(q_id=q_id).first()
    qs.upvotes += 1
    db.session.commit()
    db.session.close()
    return redirect(url_for('question',q_id=q_id))

@app.route('/downvote/question/<int:q_id>/<int:u_id>')
def downvote_q(q_id, u_id):
    if not("logged_in" in session and session["logged_in"]):
        flash("You need to log in first!")
        return redirect(url_for('login'))
    qs = Question.query.filter_by(q_id=q_id).first()
    qs.upvotes -= 1
    db.session.commit()
    db.session.close()
    return redirect(url_for('question',q_id=q_id))

@app.route('/upvote/answer/<int:a_id>/<int:u_id>')
def upvote_a(a_id, u_id):
    if not("logged_in" in session and session["logged_in"]):
        flash("You need to log in first!")
        return redirect(url_for('login'))
    ans = Answer.query.filter_by(a_id=a_id).first()
    ans.upvotes += 1
    q_id = ans.q_id
    db.session.commit()
    db.session.close()
    return redirect(url_for('question',q_id=q_id))


@app.route('/downvote/answer/<int:a_id>/<int:u_id>')
def downvote_a(a_id, u_id):
    if not("logged_in" in session and session["logged_in"]):
        flash("You need to log in first!")
        return redirect(url_for('login'))
    ans = Answer.query.filter_by(a_id=a_id).first()
    ans.upvotes -= 1
    q_id = ans.q_id
    db.session.commit()
    db.session.close()
    return redirect(url_for('question',q_id=q_id))


@app.route('/profile/<int:u_id>/')
def profile_page(u_id):
    return render_template("profile.html")

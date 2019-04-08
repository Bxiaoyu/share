# encoding: utf-8

from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from models import User, Question, Answer
from exts import db
import datetime
from decorators import login_required
from flask_ckeditor import CKEditor
from sqlalchemy import or_
from forms import RegisterForm, LoginForm, RichTextForm, ContentForm, EditForm
import config
import re

app = Flask(__name__)
app.config.from_object(config)
# 控制jinja2模板的空白
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
ckeditor = CKEditor(app)
db.init_app(app)  # 初始化app


@app.route('/')
def index():
    context = {
        'questions': Question.query.order_by('-create_time').all()
    }
    return render_template('index.html', **context)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'GET':
        return render_template('login.html', form=form)
    else:
        #telephone = request.form.get('telephone')
        #password = request.form.get('password')
        if form.validate_on_submit():
            telephone = form.telephone.data
            password = form.password.data
            user = User.query.filter(User.telephone == telephone).first()
                                    
            if user and user.check_password(password):
                session['user_id'] = user.id
                # 如果想在31天内不需重复登录,设置permanent为True
                session.permanent = True
                return redirect(url_for('index'))
            else:
                flash("账号或密码错误，请确认后再输入!")
                return redirect(url_for('login'))
    return render_template('login.html', form=form)
            #    return '账号或密码错误，请确认后再输入!'


@app.route('/regist/', methods=['GET', 'POST'])
def regist():
    form = RegisterForm()
    if request.method == 'GET':
        return render_template('regist.html', form=form)
    else:
        '''
        telephone = request.form.get('telephone')
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        '''
        if form.validate_on_submit():
            telephone = form.telephone.data
            username = form.username.data
            password1 = form.password1.data
            password2 = form.password2.data
            """
            if not re.findall(r'^(\+?0?86\-?)?1[345789]\d{9}$', telephone):
                flash('请输入有效的手机号码!')
                return redirect(url_for('regist'))
            """
            # 手机号码验证，如果被注册，就不能重复注册
            user = User.query.filter(User.telephone == telephone).first()
            if user:
                flash('该手机号码已被注册！')
                return redirect(url_for('regist'))
            # return '该手机号码已被注册!'
            else:
                # password1要和password2要相等
                if password1 != password2:
                    flash('两次密码不相等，请核对后再输入！')
                    return redirect(url_for('regist'))
                    #return '两次密码不相等，请核对后再输入!'
                else:
                    user = User(telephone=telephone, username=username, password=password1)
                    db.session.add(user)
                    db.session.commit()
                    return redirect(url_for('login'))
    return render_template('regist.html', form=form)


@app.route('/logout/')
def logout():
    # 三种方法可以注销
    # session.pop('user_id')
    # del session('user_id')
    session.clear()
    return redirect(url_for('login'))


@app.route('/question/', methods=['GET', 'POST'])
@login_required
def question():
    form = RichTextForm()
    if request.method == 'GET':
        return render_template('question.html', form=form)
    else:
        #title = request.form.get('title')
        #content = request.form.get('content')
        if form.validate_on_submit():
            title = form.title.data
            content = form.body.data
            question = Question(title=title, content=content)
            question.author = g.user
            db.session.add(question)
            db.session.commit()
            return redirect(url_for('index'))
            return render_template('post.html', title=title, body=content)
    return render_template('question.html', form=form)


@app.route('/review/<question_id>')
def review(question_id):
    form = ContentForm()
    user_id = session.get('user.id')
    question_model = Question.query.filter(Question.id == question_id).first()
    answer = Answer.query.filter(Question.id == question_id).all()
    return render_template('review.html', question=question_model, answer=answer, form=form)


@app.route('/add_answer/', methods=['POST'])
@login_required
def add_answer():
    # content = request.form.get('answer_content')
    question_id = request.form.get('question_id')
    form = ContentForm()
    content = form.body.data
    answer = Answer(content=content)
    answer.author = g.user
    question = Question.query.filter(Question.id == question_id).first()
    answer.question = question
    db.session.add(answer)
    db.session.commit()
    return redirect(url_for('review', question_id=question_id, form=form))


@app.route('/userinfo/')
def userinfo():
    user_id = session['user_id']
    question_id = request.form.get('question_id')
    user = User.query.filter(User.id == user_id).first()
    content = {
        'questions': Question.query.filter(Question.id == question_id, User.id == user_id).order_by('-create_time').all()
    }
    return render_template('userinfo.html', user=user, **content)


@app.route('/siteInfo/')
def siteInfo():
    user_id = session.get('user_id')
    question_id = request.form.get('question_id')
    date = datetime.datetime.now()
    question = Question.query.filter(Question.id == question_id, User.id == user_id, db.cast(Question.create_time, db.DATE) == db.cast(date, db.DATE)).all()
    if user_id:
        context = {
            'questions': Question.query.filter(Question.id == question_id, User.id == user_id).order_by('-create_time').all()
        }
        user = g.user
        return render_template('siteInfo.html', user=user, question=question, **context)


@app.route('/search')
def search():
    q = request.args.get('q')
    condition = or_(Question.title.contains(q), Question.content.contains(q))
    questions = Question.query.filter(condition).order_by('-create_time')
    return render_template('index.html', questions=questions)


@app.route('/show')
@login_required
def show():
    user_id = session.get('user_id')
    user = g.user
    questions = Question.query.filter(User.id == user_id).all()
    return render_template('list.html', user=user, questions=questions)


@app.route('/delete/<question_id>')
@login_required
def delete(question_id):
    question = Question.query.filter(Question.id == question_id).first()
    db.session.delete(question)
    db.session.commit()
    flash("删除成功")
    return redirect(url_for('show'))


@app.route('/edit/', methods=['GET', 'POST'])
@login_required
def edit():
    form = EditForm()
    user_id = session.get('user_id')
    user = User.query.filter(User.id == user_id).first()
    if request.method == 'GET':
        return render_template('edit.html', form=form)
    else:
        if form.validate_on_submit():
            username = form.username.data
            telephone = form.telephone.data
            about_me = form.about_me.data
            user.about_me = about_me
            user = User(telephone=telephone, username=username, password=str(user.password), about_me=about_me)
            db.session.commit()
            return redirect(url_for('usercenter'))
    return render_template('edit.html', form=form)


@app.route('/usercenter/')
@login_required
def usercenter():
    #user_id = session.get('user_id')
    #user = User.query.filter(User.id == user_id).all()
    user = g.user
    return render_template('usercenter.html', user=user)


@app.before_request
def my_before_request():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            g.user = user


@app.context_processor
def my_context_processor():
    if hasattr(g, 'user'):
        return {'user':g.user}
    return {}  # 钩子函数中，若用户不存在，也要返回一个空字典，不然会报错


if __name__ == "__main__":
    app.run()

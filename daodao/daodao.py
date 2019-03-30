# encoding: utf-8

from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import User, Question, Answer
from exts import db
from decorators import login_required
from flask_ckeditor import CKEditor
from forms import RegisterForm, LoginForm, RichTextForm, ContentForm
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
        'questions':Question.query.order_by('-create_time').all()
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
            user = User.query.filter(User.telephone == telephone,
                                    User.password == password).first()
            if user:
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

            if not re.findall(r'^(\+?0?86\-?)?1[345789]\d{9}$', telephone):
                flash('请输入有效的手机号码!')
                return redirect(url_for('regist'))

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
            user_id = session.get('user_id')
            user = User.query.filter(User.id == user_id).first()
            question.author = user
            db.session.add(question)
            db.session.commit()
            return redirect(url_for('index'))
            return render_template('post.html', title=title, body=content)
    return render_template('question.html', form=form)


@app.route('/review/<question_id>')
def review(question_id):
    form = ContentForm()
    question_model = Question.query.filter(Question.id == question_id).first()
    return render_template('review.html', question=question_model, form=form)


@app.route('/add_answer/', methods=['POST'])
@login_required
def add_answer():
    # content = request.form.get('answer_content')
    question_id = request.form.get('question_id')
    form = ContentForm()
    content = form.body.data
    answer = Answer(content=content)
    user_id = session['user_id']
    user = User.query.filter(User.id == user_id).first()
    answer.author = user
    question = Question.query.filter(Question.id == question_id).first()
    answer.question = question
    db.session.add(answer)
    db.session.commit()
    return redirect(url_for('review', question_id=question_id, form=form))


@app.context_processor
def my_context_processor():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            return {'user': user}
    return {}  # 钩子函数中，若用户不存在，也要返回一个空字典，不然会报错


if __name__ == "__main__":
    app.run()

# -*- coding: utf-8 -*-
from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Length, ValidationError, Regexp
from exts import MyBaseForm


class RegisterForm(MyBaseForm):
    telephone = StringField('电话号码', validators=[DataRequired(), Regexp('^(\+?0?86\-?)?1[345789]\d{9}$'),Length(11)], render_kw={'placeholder': '手机号码'})
    username = StringField('用户名', validators=[DataRequired(), Length(1, 20)], render_kw={'placeholder': '用户名'})
    password1 = PasswordField('密码', validators=[DataRequired(), Length(6, 128)], render_kw={'placeholder': '密码'})
    password2 = PasswordField('确认密码', validators=[DataRequired(), Length(6, 128)], render_kw={'placeholder': '确认密码'})
    submit = SubmitField('立即注册')


class LoginForm(MyBaseForm):
    telephone = StringField('电话号码', validators=[DataRequired(), Length(1, 11)], render_kw={'placeholder': '手机号码'})
    password = PasswordField('密码', validators=[DataRequired(), Length(6, 128)], render_kw={'placeholder': '密码'})
    remember = BooleanField('Remember me')
    submit = SubmitField('登录')


class RichTextForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(1, 100)], render_kw={'placeholder': '请输入标题'})
    body = CKEditorField('Body', validators=[DataRequired()])
    submit = SubmitField('立即发布')


class ContentForm(FlaskForm):
    body = TextAreaField('Body', validators=[DataRequired(),  Length(1, 500)], render_kw={'placeholder': '躁出你的观点'})
    submit = SubmitField('发布评论')


class EditForm(MyBaseForm):
    telephone = StringField('电话号码', validators=[DataRequired(), Regexp('^(\+?0?86\-?)?1[345789]\d{9}$'),Length(11)])
    username = StringField('用户名', validators=[DataRequired(), Length(1, 20)])
    about_me = TextAreaField('个人简介', validators=[DataRequired(), Length(1, 100)])
    submit = SubmitField('提交修改')
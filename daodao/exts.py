# encoding: utf-8

from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm

db = SQLAlchemy()


# 设置内置错误消息为中文
class MyBaseForm(FlaskForm):
    class Meta:
        locals = ['zh']
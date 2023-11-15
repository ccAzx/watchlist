#!/usr/bin/env python
# coding: utf-8

# In[ ]:

import os
import sys
import click

from flask import Flask,render_template
from flask import request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy

WIN = sys.platform.startswith('win')
if WIN: # 如果是 Windows 系统，使用三个斜线
	prefix = 'sqlite:///'
else: # 否则使用四个斜线
	prefix = 'sqlite:////'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # 关闭对模型修改的监控
# 在扩展类实例化前加载配置
db = SQLAlchemy(app)

class User(db.Model): # 表名将会是 user（自动生成，小写处理）
	id = db.Column(db.Integer, primary_key=True) # 主键
	name = db.Column(db.String(20)) # 名字

class movie_info(db.Model): 
	movie_id = db.Column(db.String(10), primary_key = True, nullable = False)
	movie_name = db.Column(db.String(20), nullable = False)
	release_date = db.Column(db.DateTime)
	country = db.Column(db.String(20))
	type = db.Column(db.String(10))
	year = db.Column(db.String(4))
	addresses = db.relationship('movie_actor_relation', backref='movie_info', lazy = True)

class move_box(db.Model):
	movie_id = db.Column(db.String(10), primary_key = True, nullable = False)
	box = db.Column(db.Float)

class actor_info(db.Model):
	actor_id = db.Column(db.String(10), primary_key = True, nullable = False)
	actor_name = db.Column(db.String(20), nullable = False)
	ender = db.Column(db.String(2), nullable = False)
	country = db.Column(db.String(20))
	addresses = db.relationship('movie_actor_relation', backref='actor_info', lazy = True)

class movie_actor_relation(db.Model):
	id = db.Column(db.String(10), primary_key = True, nullable = False)
	movie_id = db.Column(db.String(10), db.ForeignKey('movie_info.movie_id'), nullable = False)
	actor_id = db.Column(db.String(10), db.ForeignKey('actor_info.actor_id'), nullable = False)
	relation_type = db.Column(db.String(20))

@app.context_processor
def inject_user(): # 函数名可以随意修改
	user = User.query.first()
	return dict(user=user) # 需要返回字典，等同于return {'user': user}

@app.errorhandler(404) # 传入要处理的错误代码
def page_not_found(e): # 接受异常对象作为参数
	return render_template('404.html', user=user), 404 # 返回模板和状态码

@app.route('/')
def index():
	user = User.query.first()
	movies = movie_info.query.all()
	return render_template('index.html', user=user, movies=movies)

@app.route('/input', methods=['GET', 'POST'])
def input():
	user = User.query.first()
	movies = movie_info.query.all()
	return render_template('index.html', user=user, movies=movies)

@app.route('/movie_search', methods=['GET', 'POST'])
def m_search():
	movie_name ='请输入'
	movie_data= ''
	if request.method == 'POST':
		movie_name = request.form['movie_name']
		movie_data=movie_info.query.filter_by(movie_name=movie_name).first()
	return render_template('movie_search.html',movie_name=movie_name,movie_data=movie_data)


@app.route('/actor_search', methods=['GET', 'POST'])
def a_search():
	actor_name ='请输入'
	actor_data= ''
	if request.method == 'POST':
		actor_name = request.form['actor_name']
		actor_data=actor_info.query.filter_by(actor_name=actor_name).first()
	return render_template('actor_search.html',actor_name=actor_name,actor_data=actor_data)


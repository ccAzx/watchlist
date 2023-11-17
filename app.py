#!/usr/bin/env python
# coding: utf-8

# In[ ]:

import os
import sys
import click
import secrets

from flask import Flask,render_template
from flask import request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

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
app.secret_key = secrets.token_hex(16)
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
	boxes=move_box.query.all()
	return render_template('index.html', user=user, movies=movies,boxes=boxes)

@app.route('/index_a')
def index_a():
	user = User.query.first()
	actors = actor_info.query.all()
	return render_template('index_a.html', user=user, actors=actors)
@app.route('/index_r')
def index_r():
	user = User.query.first()
	movies = movie_info.query.all()
	actors = actor_info.query.all()
	relations = movie_actor_relation.query.all()
	return render_template('index_r.html', user=user, movies=movies,actors=actors,relations=relations)
#电影查询
@app.route('/movie_search', methods=['GET', 'POST'])
def m_search():
	movie_name ='请输入'
	movies=[]
	boxes=[]
	if request.method == 'POST':
		movie_name = request.form['movie_name']
		movies = movie_info.query.filter(movie_info.movie_name.like(f'%{movie_name}%')).all()
		if movies:
			for movie in movies:
				boxes.append(move_box.query.filter_by(movie_id=movie.movie_id).first())
	return render_template('movie_search.html',movie_name=movie_name,movies=movies,boxes=boxes)

#演员查询
@app.route('/actor_search', methods=['GET', 'POST'])
def a_search():
	actor_name ='请输入'
	actors=[]
	if request.method == 'POST':
		actor_name = request.form['actor_name']
		actors=actor_info.query.filter(actor_info.actor_name.like(f'%{actor_name}%')).all()
	return render_template('actor_search.html',actor_name=actor_name,actors=actors)

#关系查询
@app.route('/relation_search', methods=['GET', 'POST'])
def r_search():
	movie_name ='请输入'
	actor_name ='请输入'
	movie=''
	actor=''
	relations=[]
	if request.method == 'POST':
		movie_name = request.form['movie_name']
		actor_name = request.form['actor_name']
		movie = movie_info.query.filter_by(movie_name=movie_name).first()
		actor = actor_info.query.filter_by(actor_name=actor_name).first()
		if movie and actor:
			relations = movie_actor_relation.query.filter_by(movie_id=movie.movie_id, actor_id=actor.actor_id).all()
			

	return render_template('relation_search.html', movie_name=movie_name,movie=movie,actor=actor,relations=relations)

#电影编辑
@app.route('/movie_edit/<int:movie_id>', methods=['GET', 'POST'])
def m_edit(movie_id):
	movie = movie_info.query.get_or_404(movie_id)
	box = move_box.query.get_or_404(movie_id)
	if request.method == 'POST':
		movie.movie_name = request.form['movie_name']
		movie.year = request.form['year']
		movie.release_date = datetime.strptime(request.form['release_date'], '%Y-%m-%d')
		movie.country = request.form['country']
		movie.type = request.form['type']
		box.box=request.form['box']
		db.session.commit()
		flash('成功编辑！')
		return redirect(url_for('index'))
	return render_template('movie_edit.html', movie=movie,box=box)

#电影删除
@app.route('/movie/delete/<int:movie_id>', methods=['POST'])
def m_delete(movie_id):
	movie = movie_info.query.get_or_404(movie_id)
	db.session.delete(movie)
	db.session.commit()
	flash('Item deleted.')
	return redirect(url_for('index'))

#演员编辑
@app.route('/actor_edit/<int:actor_id>', methods=['GET', 'POST'])
def a_edit(actor_id):
	actor = actor_info.query.get_or_404(actor_id)
	if request.method == 'POST':
		actor.actor_name = request.form['actor_name']
		actor.ender = request.form['ender']
		actor.country = request.form['country']
		db.session.commit()
		flash('成功编辑！')
		return redirect(url_for('index_a'))
	return render_template('actor_edit.html', actor=actor)

#演员删除
@app.route('/actor/delete/<int:actor_id>', methods=['POST'])
def a_delete(actor_id):
	actor = actor_info.query.get_or_404(actor_id)
	db.session.delete(actor)
	db.session.commit()
	flash('Item deleted.')
	return redirect(url_for('a_index'))

#关系编辑
@app.route('/relation_edit/<int:relation_id>', methods=['GET', 'POST'])
def r_edit(relation_id):
	relation = movie_actor_relation.query.get_or_404(relation_id)
	movie=movie_info.query.filter_by(movie_id=relation.movie_id).first()
	actor=actor_info.query.filter_by(actor_id=relation.actor_id).first()
	
	if request.method == 'POST':
		movie_name=request.form['movie_name']
		actor_name=request.form['actor_name']
		relation.relation_type=request.form['relation_type']
		movie=movie_info.query.filter_by(movie_name=movie_name).first()
		actor=actor_info.query.filter_by(actor_name=actor_name).first()
		relation.movie_id=movie.movie_id
		relation.actor_id=actor.actor_id
		db.session.commit()
		flash('成功编辑！')
		return redirect(url_for('index_r'))
	return render_template('relation_edit.html', relation=relation,movie=movie,actor=actor)

#关系删除
@app.route('/relation/delete/<int:relation_id>', methods=['POST'])
def r_delete(relation_id):
	relation = movie_actor_relation.query.get_or_404(relation_id)
	db.session.delete(relation)
	db.session.commit()
	flash('Item deleted.')
	return redirect(url_for('r_index'))

#进入输入界面
@app.route('/input', methods=['GET', 'POST'])
def input():
	return render_template('input.html')
#电影输入
@app.route('/movie_input', methods=['GET', 'POST'])
def m_input():
	if request.method == 'POST':
		movie_id =  movie_info.query.count()+1001
		movie_name = request.form['movie_name']
		release_date = request.form['release_date']
		release_date = datetime.strptime(release_date, '%Y-%m-%d')
		country = request.form['country']
		type = request.form['type']
		year = request.form['year']
		box = request.form['box']
		movie=movie_info.query.filter_by(movie_name=movie_name).first()
		if movie:
			flash('已存在该电影！')
			return redirect(url_for('m_input'))
		else:
			new_movie = movie_info(movie_id=movie_id,movie_name=movie_name,release_date=release_date,country=country,type=type,year=year)
			new_box = move_box(movie_id=movie_id,box=box)
			db.session.add(new_movie)
			db.session.add(new_box)
			db.session.commit()
			return redirect(url_for('index'))  # 重定向回主页或其他页面
	return render_template('movie_input.html')

@app.route('/actor_input', methods=['GET', 'POST'])
def a_input():
	return render_template('actor_input.html')

@app.route('/relation_input', methods=['GET', 'POST'])
def r_input():
	return render_template('relation_input.html')

if __name__ == '__main__':
	app.run(debug=True)
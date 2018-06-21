from flask import Flask, render_template, abort
import os
import json
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import create_engine
from pymongo import MongoClient

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@localhost/xu'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
client = MongoClient('127.0.0.1',27017)
db = SQLAlchemy(app)
tag = client.xu.tag

class Category(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(80))
    def __init__(self,name):
        self.name = name
    def __repr__(self):
        return "<Category=%s>" %self.name

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80),unique= True)
    created_time = db.Column(db.DateTime)
    category_id = db.Column(db.Integer,db.ForeignKey('category.id'))
    category = db.relationship('Category')
    content = db.Column(db.Text)
    def add_tag(self, tag_name):
        name = tag.find_one({'id': self.id})
        if name:
            tags = name['tags']
            if not tag_name in tags:
                tags.append(tag_name)
                tag.update_one({'id': self.id},{'$set':{'tags': tags}})
        else:
            tag.insert_one({'id': self.id, 'tags': [tag_name]})

    def remove_tag(self, tag_name):
        name = tag.find_one({'id': self.id})
        if name:
            tags = name['tags']
            if tag_name in tags:
                tags.remove(tag_name)
                tag.update_one({'id': self.id}, {'$set':{'tags': tags}})
    @property
    def tags(self):
        return tag.find_one({'id':self.id})['tags']

    def __init__(self, title, created_time, category, content):
        self.title = title
        self.created_time = created_time
        self.category = category
        self.content = content

    def __repr__(self):
        return "<File=%s>" %self.name


@app.route('/')
def index():
    files = File.query.all()
    '''
    course={}
    names = engine.execute('select id,title from file').fetchall()
    for name in names:
        course[name[0]] = name[1] 
    '''
    return render_template('index.html', files=files)

@app.route('/files/<file_id>')
def file(file_id):
    f = File.query.get_or_404(file_id)
    #name = engine.execute('select file.*,category.name from file join category on file.id = category.id and file.id = ' + file_id).fetchall()
    return render_template('file.html', f=f)


@app.errorhandler(404)
def haha(error):
    return render_template('404.html'), 404


#!venv/bin/python
# -*- coding: utf-8 -*-
"""main file for wikiSearch"""
import os
import json

from flask import Flask, render_template, session, redirect, url_for, jsonify, make_response
from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField, SubmitField
from wtforms.validators import Required, URL
from flask_sqlalchemy import SQLAlchemy

import cachedSearch
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
# set key for some security functions
app.config['SECRET_KEY'] = 'ansdaerofbcp348p2M432023ML+#th5'
# SQLAlchemy configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
# cross-site request forgery protection
csrf = CSRFProtect(app)
# bootstrap for neat design
bootstrap = Bootstrap(app)
# for easy run
manager = Manager(app)
# SQLite database object
db = SQLAlchemy(app)

class UrlForm(FlaskForm):
    """Wikipedia form"""
    url = StringField('Enter a Wikipedia Url. May take some time to find him.', validators=[Required(), URL(message=u'Invalid URL.')])
    submit = SubmitField('Search')

class Distance(db.Model):
    """SQL Database for the distance to him"""
    __tablename__ = 'distance'
    id = db.Column(db.Integer, primary_key=True)
    distance = db.Column(db.Integer, unique=True)
    urls = db.relationship('UrlDb', backref='distance', lazy='dynamic')

    def __repr__(self):
        return '<Distance %r>' % self.distance


class UrlDb(db.Model):
    """SQL Database for found urls"""
    __tablename__ = 'urls'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.Unicode, unique=True)
    name = db.Column(db.Unicode(64))
    road = db.Column(db.Unicode)
    distance_id = db.Column(db.Integer, db.ForeignKey('distance.id'))

    def __repr__(self):
        return '<Name %r>' % self.name

@app.route('/', methods=['GET', 'POST'])
def index():
    form = UrlForm()
    if form.validate_on_submit():
        session['url'] = cachedSearch.mobile_to_desktop(form.url.data)
        url_obj = UrlDb.query.filter_by(url=session['url']).first()
        try:
            print(url_obj.road)
        except:
            print('No object defined')
        if url_obj:
            session['road'] = (url_obj.road
                               + '. Distance = ' + str(url_obj.distance.distance))
        else:
            #result_list = cachedSearch.hit_search(session['url'])
            cachedSearchObj = cachedSearch.cachedSearch(session['url'])
            cachedSearchObj.search()
            result_list = cachedSearchObj.getListOfSites()
            session['road'] = (result_list[-1].road
                               + '. Distance = ' + str(result_list[-1].distance))
            store_result(result_list)
        return redirect(url_for('index'))
    road = session.get('road', None)
    try:
        del session['road']
    except:
        pass
    return render_template('index.html', form=form, result=road)

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    form = UrlForm()
    if form.validate_on_submit():
        session['url'] = cachedSearch.mobile_to_desktop(form.url.data)
        url_obj = UrlDb.query.filter_by(url=session['url']).first()
        try:
            print(url_obj.road)
        except:
            print('No object defined')
        if url_obj:
            session['road'] = (url_obj.road
                               + '. Distance = ' + str(url_obj.distance.distance))
        else:
            #result_list = cachedSearch.hit_search(session['url'])
            cachedSearchObj = cachedSearch.cachedSearch(session['url'])
            cachedSearchObj.search()
            result_list = cachedSearchObj.getListOfSites()
            session['road'] = (result_list[-1].road
                               + '. Distance = ' + str(result_list[-1].distance))
            store_result(result_list)
        response = make_response(json.dumps(session['road']))
        response.content_type = 'application/json'
        return response

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

def store_result(result_list):
    for res in result_list:
        distance = Distance.query.filter_by(distance=res.distance).first()
        if not distance:
            distance = Distance(distance=res.distance)
            db.session.add(distance)
        print(res.url)
        url = UrlDb.query.filter_by(url=res.url).first()
        if not url:
            url = UrlDb(url=res.url, name=res.heading, road=res.road, distance=distance)
            db.session.add(url)
        #print(res.heading)
        #print(res.road)
        #print(res.distance)
    db.session.commit()

if __name__ == '__main__':
    db.create_all()
    manager.run()

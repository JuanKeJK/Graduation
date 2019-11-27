from flask import render_template, redirect, url_for, abort, request, current_app
from flask_login import current_user, login_required

from ..models import User, Student
from . import main
import re


@login_required
@main.route('/')
def index():
    if current_user.is_authenticated:
        # 分页显示
        page = request.args.get('page', 1, type=int)
        pagination = User.query.paginate(page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], error_out=False)
        users = pagination.items
        return render_template('index.html', pagination=pagination, users=users)
    else:
        return redirect(url_for('auth.login'))

@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    return render_template('auth/profile.html', user=user)

@main.route('/search')
def search():
    value = request.args.get('search')
    users = []
    if re.match('^\d{9}$', value) is not None:
        users = User.query.filter_by(student_id=value).all()
    elif re.match('^[\u4E00-\u9FA5\uf900-\ufa2d·s]{2,20}$', value) is not None:
        users = User.query.filter_by(username=value).all()
    return render_template('index.html', users=users)

@main.route('/profile')
def profile():
    user = User.query.filter_by(username='乔磊').first()
    return render_template('auth/profile.html', user=user)

@main.route('/show_students')
def show_students():
    page = request.args.get('page', 1, type=int)
    pagination = Student.query.paginate(page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], error_out=False)
    students = pagination.items
    return render_template('auth/show-students.html', pagination=pagination, students=students)
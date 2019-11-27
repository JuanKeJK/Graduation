from flask import render_template, flash, redirect, url_for, request
from ..models import User, db
from . import auth
from .forms import LoginForm, RegistrationForm, StudentProfileForm
from flask_login import login_user, logout_user, login_required, current_user
from ..email import send_email

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remeber_me.data)
            if not user.confirmed:
                # 确认令牌
                token = user.generate_confirmation_token()
                # send_email(user.email, 'Confirm Your Account', 'auth/email/confirm', user=user, token=token)
                flash('确认邮件已发送到您的邮箱，请注意查收')
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('邮箱或密码有误，请重新输入')
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已退出登录')
    return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, password=form.password.data)
        db.session.add(user)
        flash('您现在可以登录了')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form=form)

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('您已确认您的邮箱')
    else:
        flash('无效的链接或已超时')
    return redirect(url_for('main.index'))

@auth.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = StudentProfileForm()
    if form.validate_on_submit():
        current_user.username = form.name.data
        current_user.location = form.location.data
        db.session.add(current_user)
        return redirect(url_for('main.user', username=current_user.username))
    return render_template('auth/edit_profile.html', form=form)
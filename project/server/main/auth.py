from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from . import db
from flask_login import login_user, login_required, logout_user, current_user

Auth = Blueprint("Auth", __name__)


@Auth.route("/logout")
@login_required
def logout():
    logout_user()
    return(redirect(url_for("Auth.login")))


@Auth.route("/sign-up", methods=['GET', 'POST'])
def sign_up():
    if(request.method == 'POST'):
        email = request.form.get('email')
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        user = User.query.filter_by(email=email).first()
        if(user):
            flash('User with this email already exists', category='error')
        elif(len(email) < 4):
            flash("Email must be more than 3 characters", category='error')
        elif(len(username) < 2):
            flash("Name must be more than 2 characters", category='error')
        elif(password1 != password2):
            flash("Passwords must match", category='error')
        elif(len(password1) < 7):
            flash("Passwords must be at least 7 characters", category='error')
        else:
            new_user = User(email=email, username=username, password=generate_password_hash(
                password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            flash("Account created", category='success')
            user = User.query.filter_by(email=email).first()
            login_user(user, remember=True)
            return(redirect(url_for('Views.home')))
    return render_template("sign-up.html", user=current_user)

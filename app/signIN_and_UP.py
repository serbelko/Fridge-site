from flask import request, jsonify, render_template, flash, redirect, url_for
from app import db, app
import sqlalchemy as sa
from urllib.parse import urlsplit
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User
from app.forms import RegistrationForm, LoginForm

@app.route('/signup', methods=['GET', 'POST'])
def register(): # Регистрация нового пользователя
    if current_user.is_authenticated:
        return redirect(url_for('users'))
    form = RegistrationForm()
    
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        login_user(user) # модуль для сохранения сессии
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('login') # переход на эту страницу, если пользователь успешно зарегался
        return redirect(next_page)
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login(): #Вход пользователя 
  if current_user.is_authenticated:
    return redirect(url_for('users'))
  form = LoginForm()
  if form.validate_on_submit():
    user = db.session.scalar(
      sa.select(User).where(User.email == form.email.data))
    if user is None or not user.check_password(form.password.data):
        print('не работает')
        flash('Invalid username or password')
        return redirect(url_for('login'))
    login_user(user)
    print('Вошёл')
    return redirect(url_for('index'))
  return render_template('login.html', title='Sign In', form=form)
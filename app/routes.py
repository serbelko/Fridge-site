from flask import request, jsonify, render_template, flash, redirect, url_for
from app import db, app
from datetime import date, timedelta
import sqlalchemy as sa
from urllib.parse import urlsplit
from flask_login import current_user, login_user, logout_user, login_required
from app.models import Product, User, Fridge
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
    return redirect(url_for('users'))
  return render_template('login.html', title='Sign In', form=form)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fridge')
@login_required
def fridge():
    # Получаем все продукты в холодильнике пользователя
    fridge_items = db.session.query(Fridge, Product).join(Product).filter(Fridge.user_id == current_user.id).all()

    # Текущая дата и дата за 2 дня до окончания срока годности
    current_date = date.today()
    two_days_before_expiry = current_date + timedelta(days=2)

    return render_template(
        'fridge.html',
        fridge_items=fridge_items,
        current_date=current_date,
        two_days_before_expiry=two_days_before_expiry
    )


@app.route('/api/fridge/<int:product_id>', methods=['DELETE'])
@login_required
def delete_from_fridge(product_id):
    # Проверяем, есть ли продукт у текущего пользователя
    fridge_item = Fridge.query.filter_by(user_id=current_user.id, product_id=product_id).first()

    if not fridge_item:
        return jsonify({"error": "Продукт не найден в вашем холодильнике"}), 404

    # Удаляем продукт
    db.session.delete(fridge_item)
    db.session.commit()

    return jsonify({"message": "Продукт удалён", "product_id": product_id}), 200

@app.route('/shopping_list')
def shopping_list():
    return render_template('shopping_list.html')

@app.route('/scan')
def scan_qr():
    return render_template('scan_qr.html')

@app.route('/products')
def find_product():
    return render_template('find_product.html')

@app.route('/analytics')
def analytics():
    return render_template('analytics.html')



@app.route('/logout')
def logout(): # Выход пользователя из сессии
    logout_user()
    return redirect(url_for('login'))
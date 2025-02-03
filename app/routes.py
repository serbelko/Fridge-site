from flask import request, jsonify, render_template, flash, redirect, url_for
from app import db, app
from urllib.parse import urlsplit
from flask_login import current_user, login_user, logout_user
from app.models import Product, User
from app.forms import RegistrationForm
from datetime import datetime

@app.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([{
        'id': p.id, 'name': p.name, 'product_type': p.product_type,
        'manufacture_date': p.manufacture_date.strftime('%Y-%m-%d'),
        'expiration_date': p.expiration_date.strftime('%Y-%m-%d'),
        'quantity': p.quantity, 'unit': p.unit, 'nutrition_info': p.nutrition_info
    } for p in products])

@app.route('/api/products', methods=['POST'])
def add_product():
    data = request.get_json()
    new_product = Product(
        name=data['name'], 
        product_type=data['product_type'],
        manufacture_date=datetime.strptime(data['manufacture_date'], '%Y-%m-%d'),
        expiration_date=datetime.strptime(data['expiration_date'], '%Y-%m-%d'),
        quantity=data['quantity'], unit=data['unit'],
        nutrition_info=data.get('nutrition_info', '')
    )
    db.session.add(new_product)
    db.session.commit()
    return jsonify({'message': 'Продукт добавлен'}), 201

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = Product.query.get(product_id)
    if product:
        db.session.delete(product)
        db.session.commit()
        return jsonify({'message': 'Продукт удалён'})
    return jsonify({'error': 'Продукт не найден'}), 404


@app.route('/api/signup', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('register.html', title='Register', form=form)

@app.route('/api/users', methods=['GET'])
def users():
    products = User.query.all()
    return jsonify([{
        'id': p.id, 'name': p.username, "email": p.email
    } for p in products])




@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
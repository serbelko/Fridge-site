from flask import request, jsonify, render_template, flash, redirect, url_for
from app import db, app
import sqlalchemy as sa
from urllib.parse import urlsplit
from flask_login import current_user, login_user, logout_user, login_required
from app.models import Product, User, Fridge
from app.forms import RegistrationForm, LoginForm
from datetime import datetime

@app.route('/api/products', methods=['GET'])
def get_products(): # Вывод всех продуктов (пока не реализован)
    products = Product.query.all()
    return jsonify([{
        'id': p.id, 'name': p.name, 'product_type': p.product_type,
        'manufacture_date': p.manufacture_date.strftime('%Y-%m-%d'),
        'expiration_date': p.expiration_date.strftime('%Y-%m-%d'),
        'quantity': p.quantity, 'unit': p.unit, 'nutrition_info': p.nutrition_info
    } for p in products])

@app.route('/api/products', methods=['POST'])
def add_product(): #добавление нового продукта (пока не реализован)
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
def delete_product(product_id): # удаление продукта по его айди (пока не реализован)
    product = Product.query.get(product_id)
    if product:
        db.session.delete(product)
        db.session.commit()
        return jsonify({'message': 'Продукт удалён'})
    return jsonify({'error': 'Продукт не найден'}), 404

@app.route('/api/users', methods=['GET'])
def users(): # Вывод всех user в БД (для тестирования)
    products = User.query.all()
    return jsonify([{
        'id': p.id, 'name': p.username, "email": p.email
    } for p in products])


@app.route('/api/fridge/add', methods=['POST'])
def test_add_to_fridge():
    data = request.get_json()

    # Проверяем, есть ли все необходимые данные в запросе
    required_fields = ['product_id', 'create_from', 'create_until', 'count', 'user_id']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Отсутствуют обязательные поля"}), 400

    product_id = data['product_id']
    create_from = datetime.strptime(data['create_from'], "%Y-%m-%d").date()
    create_until = datetime.strptime(data['create_until'], "%Y-%m-%d").date()
    count = data.get('count', 1)
    user_id = data['user_id']

    # Проверяем, есть ли уже этот продукт в холодильнике пользователя
    fridge_item = Fridge.query.filter_by(user_id=user_id, product_id=product_id).first()

    if fridge_item and fridge_item.create_until == create_until:
        # Если продукт уже есть, увеличиваем `count`
        fridge_item.count += count
    else:
        # Если продукта нет, создаём новую запись
        fridge_item = Fridge(
            user_id=user_id,
            product_id=product_id,
            count=count,
            create_from=create_from,
            create_until=create_until
        )
        db.session.add(fridge_item)

    db.session.commit()

    return jsonify({"message": "Продукт успешно добавлен в холодильник", "product_id": product_id, "count": fridge_item.count}), 201


@app.route('/api/fridge/users/<int:user_id>', methods=['GET'])
def get_user_fridge(user_id):
    # Проверяем, есть ли такой пользователь в базе
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Пользователь не найден"}), 404

    # Получаем все продукты в холодильнике данного пользователя
    fridge_items = Fridge.query.filter_by(user_id=user_id).all()

    # Формируем JSON-ответ
    response = [
        {
            "product_id": item.product_id,
            "product_name": item.product.name,
            "product_type": item.product.product_type,
            "count": item.count,
            "create_from": item.create_from.strftime("%Y-%m-%d"),
            "create_until": item.create_until.strftime("%Y-%m-%d")
        }
        for item in fridge_items
    ]

    return jsonify(response), 200


@app.route('/generate_qr', methods=['POST'])
@login_required
def generate_qr():
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Отсутствуют данные для генерации QR-кода"}), 400

    return generate_qr_code(data)


import qrcode
import json
from io import BytesIO
from flask import send_file

def generate_qr_code(product_data):
    """
    Генерирует QR-код для переданных данных о продукте.
    :param product_data: dict с информацией о продукте.
    :return: HTTP-ответ с изображением QR-кода.
    """
    try:
        # Преобразуем словарь в JSON-строку
        qr_data = json.dumps(product_data, ensure_ascii=False)

        # Создаём QR-код
        qr = qrcode.make(qr_data)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        buffer.seek(0)

        return send_file(buffer, mimetype="image/png")
    
    except Exception as e:
        return {"error": f"Ошибка генерации QR-кода: {str(e)}"}, 500


@app.route('/generate_qr_page', methods=['GET', 'POST'])
@login_required
def generate_qr_page():
    if request.method == 'POST':
           # Получаем данные из формы
        product_id = request.form.get('product_id')
        create_from = request.form.get('create_from')
        create_until = request.form.get('create_until')
        count = request.form.get('count')

        # Проверяем, что все обязательные поля заполнены
        if not all([product_id, create_from, create_until, count]):
            return render_template('generate_qr.html', error="Заполните все обязательные поля!")

        # Формируем данные для QR-кода
        qr_data = {
            "product_id": product_id,
            "create_from": create_from,
            "create_until": create_until,
            "count": count,
            "user_id": current_user.id  # Текущий пользователь
        }

        # Генерация QR-кода
        qr_img = qrcode.make(qr_data)
        buffer = BytesIO()
        qr_img.save(buffer, format="PNG")
        buffer.seek(0)

        return send_file(buffer, mimetype='image/png', as_attachment=True, download_name='qr_code.png')

    return render_template('generate_qr.html')

@app.route('/get_user_id', methods=['GET'])
@login_required
def get_user_id():
    return jsonify({"user_id": current_user.id})
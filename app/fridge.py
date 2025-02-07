from flask import request, jsonify, render_template, flash, redirect, url_for
from app import db, app
import base64
from datetime import date, timedelta, datetime
import sqlalchemy as sa
import numpy as np
import cv2
import json
from urllib.parse import urlsplit
from flask_login import current_user, login_user, logout_user, login_required
from app.models import Product, Fridge, ShoppingList



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



@app.route('/fridge/add', methods=['POST'])
@login_required
def add_to_fridge():
    data = request.get_json()
    print('в холодильник добавлено')
    # Проверяем, есть ли все необходимые данные в запросе
    required_fields = ['product_id', 'create_from', 'create_until', 'count']
    if not all(field in data for field in required_fields):
        print(data.get('product_id'), data.get('create_until'), data.get('create_from'), data.get('count'))
        return jsonify({"error": "Отсутствуют обязательные поля :)"}), 400

    product_id = data['product_id']
    create_from = datetime.strptime(data['create_from'], "%Y-%m-%d").date()
    create_until = datetime.strptime(data['create_until'], "%Y-%m-%d").date()
    count = data.get('count', 1)
    user_id = current_user.id

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


# --- Перемещение товара в холодильник через форму ---
@app.route('/shopping_list/move_to_fridge/<int:product_id>', methods=['POST'])
@login_required
def move_to_fridge(product_id):
    shopping_item = ShoppingList.query.filter_by(user_id=current_user.id, product_id=product_id).first()

    if not shopping_item:
        flash("Продукт не найден в вашем списке покупок", "error")
        return redirect(url_for('shopping_list'))

    # Переносим продукт в холодильник (без даты)
    fridge_item = Fridge.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if fridge_item:
        fridge_item.count += shopping_item.count
    else:
        fridge_item = Fridge(user_id=current_user.id, product_id=product_id, count=shopping_item.count)
        db.session.add(fridge_item)

    # Удаляем продукт из списка покупок
    db.session.delete(shopping_item)
    db.session.commit()

    flash("Продукт перемещён в холодильник", "success")
    return redirect(url_for('shopping_list'))
from flask import render_template, flash, redirect, url_for, request, jsonify
from app import db, app
from urllib.parse import urlsplit
from flask_login import current_user, login_user, logout_user, login_required
from app.models import Product, Fridge, ShoppingList, Analytics

@app.route('/shopping_list/add', methods=['POST'])
@login_required
def add_to_shopping_list():
    data = request.get_json()

    # Проверяем обязательные поля
    if not data or 'product_id' not in data or 'count' not in data:
        return jsonify({"error": "Некорректные данные. Укажите product_id и count"}), 400

    product_id = data['product_id']
    count = data['count']
    user_id = current_user.id

    try:
        # Проверяем, есть ли уже этот продукт в списке покупок
        shopping_item = ShoppingList.query.filter_by(user_id=user_id, product_id=product_id).first()

        if shopping_item:
            # Если продукт уже есть, обновляем количество
            shopping_item.count += count
        else:
            # Если нет, добавляем новую запись
            shopping_item = ShoppingList(
                user_id=user_id,
                product_id=product_id,
                count=count
            )
            db.session.add(shopping_item)

        db.session.commit()
        return jsonify({"message": "Продукт успешно добавлен в список покупок"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500



@app.route('/shopping_list')
@login_required
def shopping_list():
    shopping_items = db.session.query(ShoppingList, Product).join(Product).filter(ShoppingList.user_id == current_user.id).all()
    return render_template('shopping_list.html', shopping_items=shopping_items)

@app.route('/shopping_list/remove', methods=['POST'])
@login_required
def remove_from_shopping_list():
    """Удаление продукта из списка покупок поштучно"""
    data = request.get_json()
    product_id = data.get("product_id")
    count_to_remove = data.get("count", 1)  # Количество для удаления, по умолчанию 1

    if not product_id:
        return jsonify({"error": "Отсутствует product_id"}), 400

    shopping_item = ShoppingList.query.filter_by(user_id=current_user.id, product_id=product_id).first()

    if not shopping_item:
        return jsonify({"error": "Продукт не найден в списке покупок"}), 404

    if shopping_item.count > count_to_remove:
        # Уменьшаем количество товара
        shopping_item.count -= count_to_remove
    else:
        # Если количество меньше или равно 0, удаляем запись
        db.session.delete(shopping_item)

    db.session.commit()

    return jsonify({
        "message": "Продукт обновлен в списке покупок",
        "remaining_count": shopping_item.count if shopping_item.count > 0 else 0
    }), 200




@app.route('/shopping_list/update', methods=['POST'])
@login_required
def update_shopping_list():
    try:
        data = request.get_json()
        if not data or 'product_id' not in data or 'count' not in data:
            return jsonify({"error": "Некорректные данные"}), 400

        product_id = data['product_id']
        count = data['count']
        user_id = current_user.id

        shopping_item = ShoppingList.query.filter_by(user_id=user_id, product_id=product_id).first()
        if shopping_item:
            shopping_item.count += count
            if shopping_item.count <= 0:
                db.session.delete(shopping_item)
            else:
                db.session.commit()
            return jsonify({"message": "Количество обновлено"}), 200
        else:
            return jsonify({"error": "Продукт не найден в списке покупок"}), 404
    except Exception as e:
        print(f"Ошибка: {e}")
        return jsonify({"error": "Произошла ошибка на сервере"}), 500

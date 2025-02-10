from flask import request, jsonify, render_template, flash, redirect, url_for
from app import db, app
from datetime import date, timedelta, datetime
from urllib.parse import urlsplit
from flask_login import current_user, login_user, logout_user, login_required
from app.models import Product, Fridge, ShoppingList, Analytics


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
    """удаление продукта"""
    # Проверяем, есть ли продукт у текущего пользователя
    fridge_item = Fridge.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    current_date = datetime.today().date()
    user_id = fridge_item.user_id
    count = fridge_item.count

    if not fridge_item:
        return jsonify({"error": "Продукт не найден в вашем холодильнике"}), 404
    
    analytics_entry = Analytics(
                user_id=user_id,
                product_id=product_id,
                action=0,  # 0 - удаление
                count=count,
                add_date=current_date
            )
    
    db.session.add(analytics_entry)
    db.session.delete(fridge_item)
    db.session.commit()

    return jsonify({"message": "Продукт удалён", "product_id": product_id}), 200


@app.route('/fridge/add', methods=['POST'])
@login_required
def add_to_fridge():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Данные не предоставлены"}), 400

    if not isinstance(data, list) or len(data) == 0:
        return jsonify({"error": "Некорректный формат запроса"}), 400

    response_data = []

    for item in data:
        # Проверяем наличие всех обязательных полей
        required_fields = ['product_id', 'create_from', 'create_until', 'count']
        if not all(field in item for field in required_fields):
            return jsonify({"error": f"Отсутствуют обязательные поля в объекте {item}"}), 400

        try:
            product_id = item['product_id']
            create_from = datetime.strptime(item['create_from'], "%Y-%m-%d").date()
            create_until = datetime.strptime(item['create_until'], "%Y-%m-%d").date()
            count = item.get('count', 1)
            user_id = current_user.id
            current_date = datetime.today().date()

            # Проверяем, есть ли уже этот продукт в холодильнике пользователя
            fridge_item = Fridge.query.filter_by(user_id=user_id, product_id=product_id).first()

            if fridge_item and fridge_item.create_until == create_until:
                fridge_item.count += count  # Увеличиваем количество
            else:
                fridge_item = Fridge(
                    user_id=user_id,
                    product_id=product_id,
                    count=count,
                    create_from=create_from,
                    create_until=create_until
                )
                db.session.add(fridge_item)

            # Добавляем запись в аналитику
            analytics_entry = Analytics(
                user_id=user_id,
                product_id=product_id,
                action=1,  # 1 - добавление
                count=count,
                add_date=current_date
            )
            db.session.add(analytics_entry)

            response_data.append({
                "product_id": product_id,
                "count": fridge_item.count,
                "message": "Продукт успешно добавлен"
            })

        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Ошибка при добавлении товара {item}: {str(e)}"}), 500

    db.session.commit()  # Сохраняем изменения в базе данных
    return jsonify(response_data), 201


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
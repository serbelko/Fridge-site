from flask import render_template, flash, redirect, url_for, request, jsonify
from app import db, app
from datetime import datetime, timedelta
from urllib.parse import urlsplit
from flask_login import current_user, login_user, logout_user, login_required
from app.models import Product, Fridge, ShoppingList, Analytics


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/products')
@login_required
def find_product():
    products = Product.query.all()
    fridge_items = {item.product_id for item in Fridge.query.filter_by(user_id=current_user.id).all()}  # ID продуктов в холодильнике
    
    return render_template('find_product.html', products=products, fridge_items=fridge_items)


@app.route('/products_shop')
@login_required
def find_product_shop():
    products = Product.query.all()
    fridge_items = {item.product_id for item in Fridge.query.filter_by(user_id=current_user.id).all()}  # ID продуктов в холодильнике
    
    return render_template('find_product_shop.html', products=products, fridge_items=fridge_items)


@app.route('/analytics', methods=['GET'])
@login_required
def analytics():
    # Получаем параметры даты из GET-запроса (по умолчанию - последние 7 дней)
    start_date = request.args.get('start_date', (datetime.today().date() - timedelta(days=7)).strftime("%Y-%m-%d"))
    end_date = request.args.get('end_date', datetime.today().strftime("%Y-%m-%d"))

    try:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        return render_template("analytics.html", error="Некорректный формат даты")

    # Запрос данных аналитики за указанный период
    analytics_data = (
        db.session.query(Analytics, Product)
        .join(Product)
        .filter(
            Analytics.add_date >= start_date,
            Analytics.add_date <= end_date,
            Analytics.user_id == current_user.id
        )
        .order_by(Analytics.add_date.desc())  # Сортируем по убыванию даты
        .all()
    )

    # Преобразуем в структуру с разделением на добавленные и удалённые продукты
    analytics_results = {
        "added": [],
        "removed": []
    }

    for analytics_entry, product in analytics_data:
        entry = {
            "product_name": product.name,
            "product_type": product.product_type,
            "count": analytics_entry.count,
            "date": analytics_entry.add_date.strftime("%Y-%m-%d"),
        }
        if analytics_entry.action == 1:
            analytics_results["added"].append(entry)  # Добавленные продукты
        else:
            analytics_results["removed"].append(entry)  # Удалённые продукты

    return render_template(
        "analytics.html",
        analytics_data=analytics_results,
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d")
    )


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



@app.route('/logout')
def logout(): # Выход пользователя из сессии
    logout_user()
    return redirect(url_for('login'))
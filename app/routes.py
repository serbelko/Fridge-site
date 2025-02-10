from flask import render_template, flash, redirect, url_for, request, jsonify
from app import db, app
from datetime import datetime, timedelta
from urllib.parse import urlsplit
from flask_login import current_user, login_user, logout_user, login_required
from app.models import Product, Fridge, Analytics


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


@app.route('/notifications', methods=['GET'])
@login_required
def get_notifications():
    """Возвращает уведомления о продуктах в холодильнике."""
    notifications = []
    current_date = datetime.today().date()

    # Запрос всех продуктов в холодильнике текущего пользователя
    fridge_items = db.session.query(Fridge, Product).join(Product).filter(Fridge.user_id == current_user.id).all()

    for fridge, product in fridge_items:
        days_until_expiry = (fridge.create_until - current_date).days

        if days_until_expiry == 3:
            notifications.append({
                "message": f"Срок годности продукта '{product.name}' истекает через 3 дня ({fridge.create_until})."
            })
        elif days_until_expiry == 1:
            notifications.append({
                "message": f"Продукт '{product.name}' истекает завтра ({fridge.create_until})."
            })
        elif days_until_expiry == 0:
            notifications.append({
                "message": f"Срок годности продукта '{product.name}' истекает сегодня ({fridge.create_until})."
            })
        elif days_until_expiry < 0:
            notifications.append({
                "message": f"Продукт '{product.name}' уже испортился ({fridge.create_until})."
            })

    return jsonify(notifications)


@app.route('/logout')
def logout(): # Выход пользователя из сессии
    logout_user()
    return redirect(url_for('login'))



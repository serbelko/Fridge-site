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


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/products')
@login_required
def find_product():
    products = Product.query.all()
    fridge_items = {item.product_id for item in Fridge.query.filter_by(user_id=current_user.id).all()}  # ID продуктов в холодильнике
    
    return render_template('find_product.html', products=products, fridge_items=fridge_items)



@app.route('/analytics')
def analytics():
    return render_template('analytics.html')


@app.route('/shopping_list')
@login_required
def shopping_list():
    shopping_items = db.session.query(ShoppingList, Product).join(Product).filter(ShoppingList.user_id == current_user.id).all()
    return render_template('shopping_list.html', shopping_items=shopping_items)

# --- Удаление товара из списка покупок через форму ---
@app.route('/shopping_list/delete/<int:product_id>', methods=['POST'])
@login_required
def delete_from_shopping_list(product_id):
    shopping_item = ShoppingList.query.filter_by(user_id=current_user.id, product_id=product_id).first()

    if not shopping_item:
        flash("Продукт не найден в вашем списке покупок", "error")
        return redirect(url_for('shopping_list'))

    db.session.delete(shopping_item)
    db.session.commit()
    flash("Продукт удалён из списка покупок", "success")
    return redirect(url_for('shopping_list'))



@app.route('/logout')
def logout(): # Выход пользователя из сессии
    logout_user()
    return redirect(url_for('login'))
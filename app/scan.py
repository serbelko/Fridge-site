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


@app.route('/scan')
@login_required
def scan_qr():
    return render_template('scan_qr.html')

@app.route('/scan_qr_camera', methods=['POST'])
def scan_qr_camera():
    data = request.json.get("image")

    if not data:
        return jsonify({"error": "Изображение не передано"}), 400

    # Декодируем изображение из base64
    image_data = data.split(",")[1]
    image = np.frombuffer(base64.b64decode(image_data), np.uint8)
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)

    # Сканируем QR-код
    detector = cv2.QRCodeDetector()
    qr_data, vertices_array, _ = detector.detectAndDecode(image)

    if not qr_data:
        return jsonify({"error": "QR-код не найден"}), 400

    try:
        # Парсим данные из QR-кода
        product_data = json.loads(qr_data.replace("'", "\""))

        # Проверяем, что user_id совпадает с текущим пользователем
        if product_data.get("user_id") != current_user.id:
            return jsonify({"error": "Этот QR-код принадлежит другому пользователю"}), 403

        return jsonify(product_data)
    except json.JSONDecodeError:
        return jsonify({"error": "Ошибка декодирования QR-кода"}), 400
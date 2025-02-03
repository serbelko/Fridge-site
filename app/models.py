from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import Mapped, mapped_column
import sqlalchemy as sa
from flask_login import UserMixin
from app import login
from app import db


class Product(db.Model):
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    product_type: Mapped[str] = mapped_column(sa.String(50), nullable=False)
    manufacture_date: Mapped[sa.Date] = mapped_column(sa.Date, nullable=False)
    expiration_date: Mapped[sa.Date] = mapped_column(sa.Date, nullable=False)
    quantity: Mapped[float] = mapped_column(sa.Float, nullable=False)
    unit: Mapped[str] = mapped_column(sa.String(20), nullable=False)  # кг, шт, л и т. д.
    nutrition_info: Mapped[str] = mapped_column(sa.Text, nullable=True)
    allergens: Mapped[bool] = mapped_column(sa.Boolean, default=False)

    def __repr__(self):
        return f'<Product {self.name}>'

    

class User(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(sa.String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(sa.String(120), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(sa.String(256), nullable=False)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


@login.user_loader
def load_user(id):
  return db.session.get(User, int(id))
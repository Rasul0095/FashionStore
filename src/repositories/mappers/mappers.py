from src.models import (
    AddressOrm,
    BrandOrm,
    CartItemOrm,
    CartOrm,
    CategoryOrm,
    OrderItemOrm,
    OrderOrm,
    ProductOrm,
    ReviewOrm,
    RoleOrm,
    UserOrm,
)
from src.repositories.mappers.base import DataMapper
from src.schemas.addresses import Address
from src.schemas.brands import Brand
from src.schemas.cart_items import CartItem
from src.schemas.carts import Cart
from src.schemas.categories import Category
from src.schemas.order_items import OrderItem
from src.schemas.orders import Order
from src.schemas.products import Product
from src.schemas.reviews import Review
from src.schemas.roles import Role
from src.schemas.users import User


class AddressDataMapper(DataMapper):
    db_model = AddressOrm
    schema = Address


class BrandDataMapper(DataMapper):
    db_model = BrandOrm
    schema = Brand


class CartItemDataMapper(DataMapper):
    db_model = CartItemOrm
    schema = CartItem


class CartDataMapper(DataMapper):
    db_model = CartOrm
    schema = Cart


class CategoryDataMapper(DataMapper):
    db_model = CategoryOrm
    schema = Category


class OrderItemDataMapper(DataMapper):
    db_model = OrderItemOrm
    schema = OrderItem


class OrderDataMapper(DataMapper):
    db_model = OrderOrm
    schema = Order


class ProductDataMapper(DataMapper):
    db_model = ProductOrm
    schema = Product


class ReviewDataMapper(DataMapper):
    db_model = ReviewOrm
    schema = Review


class RoleDataMapper(DataMapper):
    db_model = RoleOrm
    schema = Role


class UserDataMapper(DataMapper):
    db_model = UserOrm
    schema = User

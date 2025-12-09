from enum import Enum


class Permission(str, Enum):
    # Products
    VIEW_PRODUCTS = "view_products"
    CREATE_PRODUCTS = "create_products"
    EDIT_PRODUCTS = "edit_products"
    DELETE_PRODUCTS = "delete_products"

    # Orders
    VIEW_ORDERS = "view_orders"
    MANAGE_ORDERS = "manage_orders"
    CANCEL_ORDERS = "cancel_orders"

    # Users
    VIEW_USERS = "view_users"
    EDIT_USERS = "edit_users"
    DELETE_USERS = "delete_users"

    # Reviews
    VIEW_REVIEWS = "view_reviews"
    MODERATE_REVIEWS = "moderate_reviews"

    # Cart
    MANAGE_CART = "manage_cart"

    # Categories/Brands
    MANAGE_CATEGORIES = "manage_categories"
    MANAGE_BRANDS = "manage_brands"

    # Analytics
    VIEW_ANALYTICS = "view_analytics"


# Наборы прав для каждой роли
ROLE_PERMISSIONS = {
    "admin": [
        Permission.VIEW_PRODUCTS,
        Permission.CREATE_PRODUCTS,
        Permission.EDIT_PRODUCTS,
        Permission.DELETE_PRODUCTS,
        Permission.VIEW_ORDERS,
        Permission.MANAGE_ORDERS,
        Permission.VIEW_USERS,
        Permission.EDIT_USERS,
        Permission.DELETE_USERS,
        Permission.MANAGE_CATEGORIES,
        Permission.MANAGE_BRANDS,
        Permission.VIEW_ANALYTICS,
        Permission.MODERATE_REVIEWS,
    ],
    "manager": [
        Permission.VIEW_PRODUCTS,
        Permission.CREATE_PRODUCTS,
        Permission.EDIT_PRODUCTS,
        Permission.VIEW_ORDERS,
        Permission.MANAGE_ORDERS,
        Permission.VIEW_USERS,
        Permission.MANAGE_CATEGORIES,
        Permission.MANAGE_BRANDS,
        Permission.VIEW_ANALYTICS,
        Permission.MODERATE_REVIEWS,
    ],
    "user": [
        Permission.VIEW_PRODUCTS,
        Permission.VIEW_ORDERS,
        Permission.MANAGE_CART,
    ]
}
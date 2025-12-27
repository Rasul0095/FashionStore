from enum import Enum


class Permission(str, Enum):
    # Products
    VIEW_PRODUCTS = "view_products"
    CREATE_PRODUCTS = "create_products"
    EDIT_PRODUCTS = "edit_products"
    DELETE_PRODUCTS = "delete_products"
    MANAGE_PRODUCT_IMAGES = "manage_product_images"  # загрузка изображений


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
    CREATE_REVIEWS = "create_reviews"  # пользователи могут создавать
    DELETE_REVIEWS = "delete_reviews"  # свои отзывы

    # Cart
    MANAGE_CART = "manage_cart"

    # Categories/Brands
    VIEW_CATEGORIES = "view_categories"
    VIEW_BRANDS = "view_brands"
    MANAGE_CATEGORIES = "manage_categories"
    MANAGE_BRANDS = "manage_brands"
    DELETE_CATEGORIES = "delete_categories"
    DELETE_BRANDS = "delete_brands"

    # Analytics
    VIEW_ANALYTICS = "view_analytics"

    # Addresses
    VIEW_ADDRESSES = "view_addresses"
    MANAGE_ADDRESSES = "manage_addresses"  # создание/редактирование своих
    DELETE_ADDRESSES = "delete_addresses"

    # Cart Items
    VIEW_CART_ITEMS = "view_cart_items"
    MANAGE_CART_ITEMS = "manage_cart_items"  # добавление/удаление из корзины

    # Order Items (обычно вместе с заказами)
    VIEW_ORDER_ITEMS = "view_order_items"

    # Dashboard/Admin
    VIEW_DASHBOARD = "view_dashboard"
    MANAGE_SITE_SETTINGS = "manage_site_settings"


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
        Permission.VIEW_CATEGORIES,
        Permission.VIEW_BRANDS,
        Permission.DELETE_CATEGORIES,
        Permission.DELETE_BRANDS,
        Permission.MANAGE_CATEGORIES,
        Permission.MANAGE_BRANDS,
        Permission.VIEW_ANALYTICS,
        Permission.VIEW_REVIEWS,
        Permission.MODERATE_REVIEWS,
        Permission.VIEW_ADDRESSES,
        Permission.MANAGE_ADDRESSES,
        Permission.VIEW_CART_ITEMS,
        Permission.MANAGE_CART_ITEMS,
        Permission.VIEW_ORDER_ITEMS,
        Permission.CREATE_REVIEWS,
        Permission.DELETE_REVIEWS,
        Permission.MANAGE_PRODUCT_IMAGES,
        Permission.VIEW_DASHBOARD,
        Permission.MANAGE_SITE_SETTINGS,
    ],
    "manager": [
        Permission.VIEW_PRODUCTS,
        Permission.CREATE_PRODUCTS,
        Permission.EDIT_PRODUCTS,
        Permission.VIEW_ORDERS,
        Permission.MANAGE_ORDERS,
        Permission.VIEW_USERS,
        Permission.VIEW_CATEGORIES,
        Permission.VIEW_BRANDS,
        Permission.MANAGE_CATEGORIES,
        Permission.MANAGE_BRANDS,
        Permission.VIEW_ANALYTICS,
        Permission.VIEW_REVIEWS,
        Permission.MODERATE_REVIEWS,
        Permission.VIEW_ADDRESSES,
        Permission.MANAGE_ADDRESSES,
        Permission.VIEW_CART_ITEMS,
        Permission.MANAGE_CART_ITEMS,
        Permission.VIEW_ORDER_ITEMS,
        Permission.CREATE_REVIEWS,
        Permission.DELETE_REVIEWS,
        Permission.MANAGE_PRODUCT_IMAGES,
        Permission.VIEW_DASHBOARD,
    ],
    "user": [
        Permission.VIEW_PRODUCTS,
        Permission.VIEW_ORDERS,
        Permission.VIEW_REVIEWS,
        Permission.VIEW_CATEGORIES,
        Permission.VIEW_BRANDS,
        Permission.MANAGE_CART,
        Permission.MANAGE_ADDRESSES,  # свои адреса
        Permission.MANAGE_CART_ITEMS,  # свою корзину
        Permission.CREATE_REVIEWS,     # свои отзывы
        Permission.DELETE_REVIEWS,     # свои отзывы
        Permission.VIEW_ADDRESSES,
        Permission.VIEW_CART_ITEMS,
    ]
}
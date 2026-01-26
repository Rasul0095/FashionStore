from fastapi import HTTPException


class FashionStoreException(Exception):
    detail = "Неожиданная ошибка"

    def __init__(self, *args, **kwargs):
        super().__init__(self.detail, *args, **kwargs)


class ObjectNotFoundException(FashionStoreException):
    detail = "Объект не найден"

class ObjectAlreadyExistsException(FashionStoreException):
    detail = "Похожий объект уже существует"

class UserAlreadyExistsException(FashionStoreException):
    detail = "Пользователь уже существует"

class RoleNotExistsException(FashionStoreException):
    detail = "Роль не существует"

class CartNotExistsException(FashionStoreException):
    detail = "Корзины не существует"

class CartItemNotFoundException(FashionStoreException):
    detail = "Элемент корзины не найден"

class ReviewNotFoundException(FashionStoreException):
    detail = "Отзыв не найден"

class ProductNotFoundException(FashionStoreException):
    detail = "Товар не найден"

class AddressNotFoundException(FashionStoreException):
    detail = "Адрес не найден"

class BrandNotFoundException(FashionStoreException):
    detail = "Бранд не найден"

class CategoryNotFoundException(FashionStoreException):
    detail = "Категория не найдена"

class UserRoleNotAssignedException(FashionStoreException):
    detail = "У данного пользователя не назначена роль"

class UserNotFoundException(FashionStoreException):
    detail = "Пользователь не найден"

class EmailNotRegisteredException(FashionStoreException):
    detail = "Пользователь с таким email не зарегистрирован"

class IncorrectPasswordException(FashionStoreException):
    detail = "Неверный логин или пароль"

class IncorrectTokenException(FashionStoreException):
    detail = "Некорректный токен"


class FashionStoreHTTPException(HTTPException):
    status_code = 500
    detail = "Ошибка: {text}"

    def __init__(self, text: str = None, **kwargs):
        detail = self.detail.format(text=text, **kwargs)
        super().__init__(status_code=self.status_code, detail=detail)


class PermissionDeniedHTTPException(HTTPException):
    def __init__(self, permission: str):
        super().__init__(
            status_code=403,
            detail=f"Недостаточно прав. Требуется: {permission}"
        )


class UserRoleNotAssignedHTTPException(FashionStoreHTTPException):
    status_code = 400
    detail = "У данного пользователя не назначена роль"


class RoleNotExistsHTTPException(FashionStoreHTTPException):
    status_code = 404
    detail = "Роль не существует"


class NoAccessTokenHTTPException(FashionStoreHTTPException):
    status_code = 401
    detail = "Вы не предоставили токен доступа"


class IncorrectTokenHTTPException(FashionStoreHTTPException):
    status_code = 401
    detail = "Некорректный токен"


class TokenExpiredHTTPException(FashionStoreHTTPException):
    status_code = 401
    detail = "Токен доступа истек"


class WrongTokenTypeHTTPException(FashionStoreHTTPException):
    status_code = 401
    detail = "Неправильный тип токена"


class UserEmailAlreadyExistsHTTPException(FashionStoreHTTPException):
    status_code = 409
    detail = "Пользователь с такой почтой уже существует"


class EmailNotRegisteredHTTPException(FashionStoreHTTPException):
    status_code = 401
    detail = "Пользователь с таким email не зарегистрирован"


class UserNotFoundHTTPException(FashionStoreHTTPException):
    status_code = 404
    detail = "Пользователь не найден"


class CannotDeleteSelfHTTPException(FashionStoreHTTPException):
    status_code = 400
    detail = "Нельзя удалить свой аккаунт"


class IncorrectPasswordHTTPException(FashionStoreHTTPException):
    status_code = 401
    detail = "Неверный логин или пароль"

class UnableDeleteRoleHTTPException(FashionStoreHTTPException):
    status_code = 400
    detail = "Невозможно удалить роль: Данную роль имеют немалое количество пользователей"

class ReviewNotFoundHTTPException(FashionStoreHTTPException):
    status_code = 404
    detail = "Отзыв не найден"

class ProductNotFoundHTTPException(FashionStoreHTTPException):
    status_code = 404
    detail = "Товар не найден"

class BrandNotFoundHTTPException(FashionStoreHTTPException):
    status_code = 404
    detail = "Бранд не найден"

class CategoryNotFoundHTTPException(FashionStoreHTTPException):
    status_code = 404
    detail = "Категория не найдена"

class CartNotExistsHTTPException(FashionStoreHTTPException):
    status_code = 404
    detail = "Корзины не существует"

class CartItemNotFoundHTTPException(FashionStoreHTTPException):
    status_code = 404
    detail = "Элемент корзины не найден"

class AddressNotFoundHTTPException(FashionStoreHTTPException):
    status_code = 404
    detail = "Адрес не найден"

class AddressInUseHTTPException(FashionStoreHTTPException):
    status_code = 400
    detail = "Адрес используется в заказах: {text}. Сначала удалите или измените эти заказы."

    def __init__(self, order_ids: list[int]):
        super().__init__(text=str(order_ids))


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
    detail = None

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


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

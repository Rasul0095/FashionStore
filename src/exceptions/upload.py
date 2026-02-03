from fastapi import HTTPException


class FileUploadHTTPException(HTTPException):
    """Базовая ошибка загрузки файлов"""

    pass


class InvalidFileExtensionHTTPException(FileUploadHTTPException):
    def __init__(self, filename: str, allowed_extensions: set):
        super().__init__(
            status_code=400,
            detail=f"Недопустимое расширение файла {filename}. "
            f"Допустимые: {', '.join(allowed_extensions)}",
        )


class FileTooLargeHTTPException(FileUploadHTTPException):
    def __init__(self, filename: str, max_size_mb: int):
        super().__init__(
            status_code=400,
            detail=f"Файл {filename} слишком большой. Максимум: {max_size_mb} MB",
        )


class TooManyFilesHTTPException(FileUploadHTTPException):
    def __init__(self, max_files: int):
        super().__init__(
            status_code=400, detail=f"Слишком много файлов. Максимум: {max_files}"
        )


class NoFilesUploadedHTTPException(FileUploadHTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Не загружены файлы")

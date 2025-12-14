from pydantic import BaseModel


class BrandsAdd(BaseModel):
    name: str
    description: str | None

class Brand(BrandsAdd):
    id: int


from pydantic import BaseModel, Field


class BrandsAdd(BaseModel):
    name: str
    description: str | None

class Brand(BrandsAdd):
    id: int

class BrandsPatch(BaseModel):
    name: str | None = Field(None)
    description: str | None = Field(None)




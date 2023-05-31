from typing import Union
from pydantic import BaseModel


class ItemCreate(BaseModel):
    pass


class Item(BaseModel):
    type: str
    description: str
    aditional: str
    config: str
    campus: str
    tab: str
    
    class Config:
        orm_mode = True


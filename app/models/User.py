from typing import Optional

from pydantic import BaseModel, Field

from app.models.base.PydanticObjectId import PydanticObjectId
from app.models.base.Model import Model


class User(BaseModel, Model):
    id:  Optional[PydanticObjectId] = Field(None, alias="_id")
    name: str
    lastname: str
    email: str

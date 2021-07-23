from typing import Optional

from pydantic import BaseModel, Field

from app.models.base.PydanticObjectId import PydanticObjectId
from app.models.base.Model import Model


class Cert(BaseModel, Model):
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    name: str
    extension: str
    filename: str
    path: str
    provider: str
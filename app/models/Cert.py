from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.base.PydanticObjectId import PydanticObjectId
from app.models.base.Model import Model


class Pub(BaseModel, Model):
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    path: str
    bucket: str


class Key(BaseModel, Model):
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    path: str
    bucket: str


class Crt(BaseModel, Model):
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    path: str
    bucket: str


class Cert(BaseModel, Model):
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    extension: str
    filename: str
    path: str
    pub: Pub
    key: Key
    crt: Crt
    provider: str
    bucket: str
    created_at: datetime

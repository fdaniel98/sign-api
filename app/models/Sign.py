from datetime import datetime
from typing import Optional

from pydantic import Field, BaseModel

from app.models.Cert import Cert
from app.models.base.PydanticObjectId import PydanticObjectId
from app.models.User import User
from app.models.base.Model import Model


class Sign(BaseModel, Model):
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    url: str
    cert: Optional[Cert]
    user: Optional[User]
    date_added: Optional[datetime]
    date_updated: Optional[datetime]


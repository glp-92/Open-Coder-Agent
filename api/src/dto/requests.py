from typing import List

from pydantic import BaseModel, ConfigDict


class _List(BaseModel):
    id: str
    name: str
    model_config = ConfigDict(extra="ignore")


class _Included(BaseModel):
    lists: List[_List] = []
    model_config = ConfigDict(extra="ignore")


class _Item(BaseModel):
    id: str
    type: str
    name: str
    description: str
    listId: str
    model_config = ConfigDict(extra="ignore")


class _Data(BaseModel):
    item: _Item
    included: _Included
    model_config = ConfigDict(extra="ignore")


class _User(BaseModel):
    id: str
    username: str
    model_config = ConfigDict(extra="ignore")


class CardMovedWebhookRequest(BaseModel):
    event: str
    data: _Data
    user: _User
    model_config = ConfigDict(extra="ignore")

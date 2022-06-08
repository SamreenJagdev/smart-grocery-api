import uuid
from marshmallow import Schema, fields, post_load, EXCLUDE
import datetime as dt
from api.schemas.listItem import ListItemSchema
from api.services.utils import Utils


class List:
    def __init__(self, id, name, creation_timestamp, items):
        self.id = id
        self.name = name
        self.creation_timestamp = creation_timestamp
        self.items = items

    def __repr__(self):
        return "<ListWithItem(id={self.id!r}, name={self.name!r})>".format(self=self)


class ListSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    model_class = List

    id = fields.String(required=False)
    name = fields.String(required=True)
    creation_timestamp = fields.String(required=False)
    items = fields.Nested(ListItemSchema, many=True, required=False)

    @post_load
    def make_list(self, data, **kwargs):
        id = uuid.uuid4().__str__() if "id" not in data else data["id"]
        name = data["name"]
        creation_timestamp = (
            str(Utils.timenow())
            if "creation_timestamp" not in data
            else data["creation_timestamp"]
        )
        items = []
        if "items" in data:
            items = data["items"]

        return List(id, name, creation_timestamp, items)

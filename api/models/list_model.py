import uuid
from marshmallow import Schema, fields, post_load, EXCLUDE
import datetime as dt

from api.services.utils import Utils


class ListModel:
    def __init__(self, id, name, creation_timestamp, item_ids):
        self.id = id
        self.name = name
        self.creation_timestamp = creation_timestamp
        self.item_ids = item_ids

    def __repr__(self):
        return "<ListModel(id={self.id!r}, name={self.name!r})>".format(self=self)


class ListModelSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    model_class = ListModel

    id = fields.String(required=False)
    name = fields.String(required=True)
    creation_timestamp = fields.String(required=False)
    item_ids = fields.List(fields.String, required=False)

    @post_load
    def make_list(self, data, **kwargs):
        id = uuid.uuid4().__str__() if "id" not in data else data["id"]
        name = data["name"]
        creation_timestamp = (
            str(Utils.timenow())
            if "creation_timestamp" not in data
            else data["creation_timestamp"]
        )
        item_ids = [] if "item_ids" not in data else data["item_ids"]

        return ListModel(id, name, creation_timestamp, item_ids)

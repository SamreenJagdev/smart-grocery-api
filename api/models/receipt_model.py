import uuid
from marshmallow import Schema, fields, post_load, EXCLUDE, pre_dump
import datetime as dt
from api.schemas.receiptItem import ReceiptItemSchema
from api.services.utils import Utils


class ReceiptModel:
    def __init__(self, id, name, creation_timestamp, merchant_name, item_ids):
        self.id = id
        self.name = name
        self.creation_timestamp = creation_timestamp
        self.merchant_name = merchant_name
        self.item_ids = item_ids

    def __repr__(self):
        return "<ReceiptModel(id={self.id!r}, name={self.name!r})>".format(self=self)


class ReceiptModelSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = fields.String(required=False)
    name = fields.String(required=True)
    creation_timestamp = fields.String(required=False)
    merchant_name = fields.String(required=False)
    item_ids = fields.List(fields.String(), required=False)

    @post_load
    def make_receipt(self, data, **kwargs):
        id = uuid.uuid4().__str__() if "id" not in data else data["id"]
        name = data["name"]
        creation_timestamp = (
            str(Utils.timenow())
            if "creation_timestamp" not in data
            else data["creation_timestamp"]
        )
        merchant_name = None if "merchant_name" not in data else data["merchant_name"]
        item_ids = [] if "item_ids" not in data else data["item_ids"]

        return ReceiptModel(id, name, creation_timestamp, merchant_name, item_ids)

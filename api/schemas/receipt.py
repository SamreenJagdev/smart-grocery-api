import uuid
from marshmallow import Schema, fields, post_load, EXCLUDE
import datetime as dt
from api.schemas.receiptItem import ReceiptItemSchema
from api.services.utils import Utils


class Receipt:
    def __init__(self, id, name, creation_timestamp, merchant_name, items):
        self.id = id
        self.name = name
        self.creation_timestamp = creation_timestamp
        self.merchant_name = merchant_name
        self.items = items

    def __repr__(self):
        return "<Receipt(id={self.id!r}, name={self.name!r})>".format(self=self)


class ReceiptSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = fields.String(required=False)
    name = fields.String(required=True)
    creation_timestamp = fields.String(required=False)
    merchant_name = fields.String(required=False)
    items = fields.List(fields.Nested(ReceiptItemSchema), required=False)

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
        items = [] if "items" not in data else data["items"]

        return Receipt(id, name, creation_timestamp, merchant_name, items)

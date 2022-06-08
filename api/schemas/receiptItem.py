import uuid
from marshmallow import Schema, fields, post_load, EXCLUDE


class ReceiptItem:
    def __init__(self, id, name, quantity, price, total_price):
        self.id = id
        self.name = name
        self.quantity = quantity
        self.price = price
        self.total_price = total_price

    def __repr__(self):
        return "<ReceiptItem(id={self.id!r}, name={self.name!r})>".format(self=self)


class ReceiptItemSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = fields.String(required=False)
    name = fields.String(required=True)
    quantity = fields.Float(required=False)
    price = fields.Float(required=False)
    total_price = fields.Float(required=False)

    @post_load
    def make_receipt_item(self, data, **kwargs) -> ReceiptItem:
        id = uuid.uuid4().__str__() if "id" not in data else data["id"]
        name = data["name"]
        quantity = 0 if "quantity" not in data else data["quantity"]
        price = 0 if "price" not in data else data["price"]
        total_price = 0 if "total_price" not in data else data["total_price"]

        return ReceiptItem(id, name, quantity, price, total_price)

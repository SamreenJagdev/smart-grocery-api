import uuid
from marshmallow import Schema, fields, post_load, EXCLUDE


class ListItem:
    def __init__(self, id, name, quantity, category):
        self.id = id
        self.name = name
        self.quantity = quantity
        self.category = category

    def __repr__(self):
        return "<ListItem(id={self.id!r}, name={self.name!r})>".format(self=self)


class ListItemSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    model_class = ListItem

    id = fields.String(required=False)
    name = fields.String(required=True)
    quantity = fields.Float(required=False)
    price = fields.Float(required=False)
    category = fields.String(required=False)
    total_price = fields.Float(required=False)

    @post_load
    def make_list_item(self, data, **kwargs) -> ListItem:
        id = uuid.uuid4().__str__() if "id" not in data else data["id"]
        name = data["name"]
        quantity = 0 if "quantity" not in data else data["quantity"]
        category = 0 if "category" not in data else data["category"]

        return ListItem(id, name, quantity, category)

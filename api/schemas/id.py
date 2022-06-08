from marshmallow import Schema, fields


class Id:
    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return "<Id(id={self.id!r})>".format(self=self)


class IdSchema(Schema):
    id = fields.Str()

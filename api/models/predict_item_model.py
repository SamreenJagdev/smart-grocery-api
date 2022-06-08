import uuid
from marshmallow import Schema, fields, post_load, EXCLUDE, pre_load
import datetime as dt


class PredictItemModel:
    def __init__(self, name, category, creation_timestamp):
        self.name = name
        self.creation_timestamp = creation_timestamp
        self.category = category

    def __repr__(self):
        return "<PredictItemModel(id={self.id!r}, name={self.name!r})>".format(
            self=self
        )


class PredictItemModelSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    model_class = PredictItemModel

    name = fields.String(required=True)
    category = fields.String(required=True)
    creation_timestamp = fields.DateTime(required=False)

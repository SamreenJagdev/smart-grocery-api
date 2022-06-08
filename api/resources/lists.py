from unicodedata import name
from flask_restful import Resource
from flask import request
from marshmallow import ValidationError
from api.schemas.id import Id, IdSchema
from api.models.list_model import ListModel, ListModelSchema
from api.schemas.listItem import ListItemSchema
from api.schemas.list import List, ListSchema
from api.services.mongo_db import DBService
from flask_jwt_extended import jwt_required, get_current_user


class Lists(Resource):
    @jwt_required()
    def get(self):
        user = get_current_user()
        db = DBService.getInstance()
        collection = db.get_collection("lists")

        results = collection.aggregate(
            [
                {"$match": {"user": user}},
                {
                    "$lookup": {
                        "from": "items",
                        "localField": "item_ids",
                        "foreignField": "id",
                        "as": "items",
                    }
                },
                {
                    "$project": {
                        "id": 1,
                        "name": 1,
                        "creation_timestamp": 1,
                        "items.id": 1,
                        "items.name": 1,
                        "items.category": 1,
                        "items.quantity": 1,
                        "_id": 0,
                    }
                },
            ]
        )

        lists = ListSchema(many=True).load(list(results))

        return {"lists": ListSchema(many=True).dump(lists)}, 200

    @jwt_required()
    def post(self):
        user = get_current_user()
        req = request.json
        try:
            list: List = ListSchema().load(req)
        except ValidationError as err:
            return err.messages, 400

        db = DBService.getInstance()
        item_ids = []
        for item in list.items:
            items_collection = db.get_collection("items")
            items_collection.insert_one(ListItemSchema().dump(item))
            item_ids.append(item.id)

        collection = db.get_collection("lists")

        list_to_save = ListModelSchema().dump(
            ListModel(list.id, list.name, list.creation_timestamp, item_ids)
        )
        list_to_save["user"] = user
        collection.insert_one(list_to_save)

        return IdSchema().dump(Id(list.id)), 201

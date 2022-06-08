from flask_restful import Resource
from flask import request
from marshmallow import ValidationError
from api.schemas.id import Id, IdSchema
from api.schemas.listItem import ListItem, ListItemSchema
from api.services.mongo_db import DBService
from flask_jwt_extended import jwt_required, get_current_user


class Items(Resource):
    @jwt_required()
    def get(self, list_id):
        user = get_current_user()
        db = DBService.getInstance()
        collection = db.get_collection("lists")

        results = collection.aggregate(
            [
                {"$match": {"id": list_id, "user": user}},
                {
                    "$lookup": {
                        "from": "items",
                        "localField": "item_ids",
                        "foreignField": "id",
                        "as": "items_lookup",
                    }
                },
                {"$unwind": "$items_lookup"},
                {
                    "$project": {
                        "id": "$items_lookup.id",
                        "name": "$items_lookup.name",
                        "quantity": "$items_lookup.quantity",
                        "category": "$items_lookup.category",
                        "_id": 0,
                    }
                },
            ]
        )
        items = ListItemSchema(many=True).load(list(results))
        return {"items": ListItemSchema(many=True).dump(items)}, 200

    @jwt_required()
    def post(self, list_id):
        user = get_current_user()
        try:
            item: ListItem = ListItemSchema().load(request.json)
        except ValidationError as err:
            return err.messages, 400

        db = DBService.getInstance()
        collection = db.get_collection("items")
        collection.insert_one(ListItemSchema().dump(item))

        collection = db.get_collection("lists")
        filter = {"id": list_id, "user": user}
        newvalues = {"$addToSet": {"item_ids": item.id}}
        collection.update_one(filter, newvalues)

        return IdSchema().dump(Id(item.id)), 201

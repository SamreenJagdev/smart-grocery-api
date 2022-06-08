from flask_restful import Resource
from flask import request
from marshmallow import ValidationError
from api.schemas.listItem import ListItem, ListItemSchema
from api.services.mongo_db import DBService
from flask_jwt_extended import jwt_required


class ItemsId(Resource):
    @jwt_required()
    def delete(self, list_id, item_id):
        db = DBService.getInstance()
        collection = db.get_collection("items")
        result = collection.delete_one({"id": item_id})

        if result.deleted_count != 1:
            return {}, 404

        collection = db.get_collection("lists")
        filter = {"id": list_id}
        newvalues = {"$pull": {"item_ids": item_id}}
        collection.update_one(filter, newvalues)

        return {}, 200

    @jwt_required()
    def put(self, list_id, item_id):
        try:
            item: ListItem = ListItemSchema().load(request.json)
        except ValidationError as err:
            return err.messages, 400

        db = DBService.getInstance()
        list_collection = db.get_collection("lists")
        item_not_present = (
            list_collection.find_one(
                {"id": list_id, "item_ids": {"$elemMatch": {"$eq": item_id}}}
            )
            is None
        )

        if item_not_present:
            return {}, 404

        items_collection = db.get_collection("items")
        find_result = items_collection.find_one({"id": item_id})
        if find_result is not None:
            result = items_collection.update_one(
                {"id": item_id},
                {
                    "$set": {
                        "name": item.name,
                        "category": item.category,
                        "quantity": item.quantity,
                    }
                },
            )
            if result.acknowledged:
                return {}, 200
            else:
                return {}, 500
        else:
            return {}, 404

from logging import log
from flask_restful import Resource
from flask import request
from marshmallow import ValidationError
from api.models.list_model import ListModel, ListModelSchema
from api.schemas.list import List, ListSchema
from api.schemas.listItem import ListItemSchema
from api.services.mongo_db import DBService
from flask_jwt_extended import jwt_required, get_current_user


class ListsId(Resource):
    @jwt_required()
    def delete(self, list_id):
        user = get_current_user()
        db = DBService.getInstance()
        list_collection = db.get_collection("lists")

        find_result = list_collection.find_one({"id": list_id, "user": user})
        if find_result is not None:

            list: ListModel = ListModelSchema().load(find_result)
            item_collection = db.get_collection("items")
            for item_id in list.item_ids:
                try:
                    item_collection.delete_one({"id": item_id})
                except:
                    print("WARNING: Invalid item id reference while deleting the list")
            delete_result = list_collection.delete_one({"id": list_id, "user": user})
            if delete_result.deleted_count == 1:
                return {}, 200
            else:
                return {}, 404
        else:
            return {}, 404

    @jwt_required()
    def put(self, list_id):
        user = get_current_user()
        req = request.json
        req["user"] = user
        try:
            new_list: List = ListSchema().load(req)
        except ValidationError as err:
            return err.messages, 400

        db = DBService.getInstance()
        collection = db.get_collection("lists")
        find_result = collection.find_one({"id": list_id, "user": user})

        if find_result is not None:
            list: ListModel = ListModelSchema().load(find_result)
            item_collection = db.get_collection("items")
            if len(new_list.items) > 0:
                for item_id in list.item_ids:
                    try:
                        item_collection.delete_one({"id": item_id})
                    except:
                        print(
                            "WARNING: Invalid item id reference while deleting the list"
                        )

                item_ids = []
                for item in new_list.items:
                    item_collection.insert_one(ListItemSchema().dump(item))
                    item_ids.append(item.id)

                list_to_save = ListModelSchema(
                    exclude=["id", "creation_timestamp"]
                ).dump(
                    ListModel(
                        list_id, new_list.name, new_list.creation_timestamp, item_ids
                    )
                )
            else:
                list_to_save = ListModelSchema(
                    exclude=["id", "creation_timestamp", "item_ids"]
                ).dump(ListModel("", new_list.name, new_list.creation_timestamp, []))
            list_to_save["user"] = user
            collection.update_one({"id": list_id, "user": user}, {"$set": list_to_save})

            return {}, 200

        else:
            return {}, 404

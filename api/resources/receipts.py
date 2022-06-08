from flask import request
from flask_restful import Resource
from marshmallow import ValidationError
from api.models.receipt_model import ReceiptModel, ReceiptModelSchema
from api.schemas.id import Id, IdSchema
from flask_jwt_extended import jwt_required, get_current_user

from api.schemas.receipt import Receipt, ReceiptSchema
from api.schemas.receiptItem import ReceiptItemSchema
from api.services.mongo_db import DBService


class Receipts(Resource):
    @jwt_required()
    def get(self):
        user = get_current_user()
        db = DBService.getInstance()
        collection = db.get_collection("receipts")

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
                        "merchant_name": 1,
                        "items.id": 1,
                        "items.name": 1,
                        "items.quantity": 1,
                        "items.price": 1,
                        "items.total_price": 1,
                        "_id": 0,
                    }
                },
            ]
        )

        receipts = ReceiptSchema(many=True).load(list(results))

        return {"receipts": ReceiptSchema(many=True).dump(receipts)}, 200

    @jwt_required()
    def post(self):
        user = get_current_user()
        req = request.json
        try:
            receipt: Receipt = ReceiptSchema().load(req)
        except ValidationError as err:
            return err.messages, 400

        db = DBService.getInstance()
        item_ids = []
        for item in receipt.items:
            items_collection = db.get_collection("items")
            items_collection.insert_one(ReceiptItemSchema().dump(item))
            item_ids.append(item.id)

        collection = db.get_collection("receipts")

        receipt_to_save = ReceiptModelSchema().dump(
            ReceiptModel(
                receipt.id,
                receipt.name,
                receipt.creation_timestamp,
                receipt.merchant_name,
                item_ids,
            )
        )
        receipt_to_save["user"] = user
        collection.insert_one(receipt_to_save)

        return IdSchema().dump(Id(receipt.id)), 201

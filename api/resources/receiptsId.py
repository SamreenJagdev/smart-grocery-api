from flask_restful import Resource
from api.models.receipt_model import ReceiptModel, ReceiptModelSchema
from flask_jwt_extended import jwt_required, get_current_user
from api.services.mongo_db import DBService


class ReceiptsId(Resource):
    @jwt_required()
    def delete(self, receipt_id):
        user = get_current_user()
        db = DBService.getInstance()
        receipt_collection = db.get_collection("receipts")

        find_result = receipt_collection.find_one({"id": receipt_id, "user": user})
        if find_result is not None:

            receipt: ReceiptModel = ReceiptModelSchema().load(find_result)
            item_collection = db.get_collection("items")
            for item_id in receipt.item_ids:
                try:
                    item_collection.delete_one({"id": item_id})
                except:
                    print("WARNING: Invalid item id reference while deleting the list")

            delete_result = receipt_collection.delete_one(
                {"id": receipt_id, "user": user}
            )
            if delete_result.deleted_count == 1:
                return {}, 200
            else:
                return {}, 404
        else:
            return {}, 404

from flask import request
from flask_restful import Resource, abort
from api.schemas.receipt import Receipt, ReceiptSchema
from api.services.azure_form_reco import AzureFormReco
from api.services.utils import Utils
from flask_jwt_extended import jwt_required


class ReceiptsScan(Resource):
    @jwt_required()
    def post(self):

        if "file" not in request.files:
            return abort(400, message="receipt.file.missing")

        file = request.files["file"]
        if file and Utils.has_allowed_extension(file.filename):
            receipt: Receipt = AzureFormReco.analyze_document(file)
        else:
            abort(400, message="invalid.file.extension")

        return ReceiptSchema(exclude=["items.id", "id", "name"]).dump(receipt), 200

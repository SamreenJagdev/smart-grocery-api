from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from api.resources.lists import Lists
from api.resources.listsId import ListsId
from api.resources.listsPredict import ListsPredict
from api.resources.receiptsId import ReceiptsId
from api.resources.receiptsScan import ReceiptsScan
from api.resources.receipts import Receipts
from flask_jwt_extended import JWTManager
from api.services.utils import Utils
import urllib3
from api.resources.items import Items
from api.resources.itemsId import ItemsId


app = Flask(__name__)
api = Api(app)
CORS(app)

urllib3.disable_warnings()

BASE_URL = "/v1"
api.add_resource(Lists, BASE_URL + "/lists")
api.add_resource(ListsId, BASE_URL + "/lists/<list_id>")
api.add_resource(ListsPredict, BASE_URL + "/lists/predict")
api.add_resource(Items, BASE_URL + "/lists/<list_id>/items")
api.add_resource(ItemsId, BASE_URL + "/lists/<list_id>/items/<item_id>")
api.add_resource(Receipts, BASE_URL + "/receipts")
api.add_resource(ReceiptsId, BASE_URL + "/receipts/<receipt_id>")
api.add_resource(ReceiptsScan, BASE_URL + "/receipts/scan")

app.config["JWT_ALGORITHM"] = "RS256"
app.config["JWT_PUBLIC_KEY"] = Utils.getJwtPublicKey()
jwt = JWTManager(app)


@jwt.user_lookup_loader
def user_lookup(header, payload):
    return payload["preferred_username"]


if __name__ == "__main__":
    app.run(debug=True)

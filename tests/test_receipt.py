import json
import tempfile
from api.schemas.receipt import ReceiptSchema
from api.services.utils import Utils
from api.services.azure_form_reco import AzureFormReco
import pytest
import mongomock
from api.services.mongo_db import DBService

TEST_USER = "test-user"


@pytest.fixture(autouse=True)
def setup(monkeypatch):
    db = mongomock.MongoClient()

    def fake_mongo():
        return db

    def no_verify_jwt(*args, **kwargs):
        pass

    def fake_get_user(*args, **kwargs):
        return TEST_USER

    def fake_rsa_public_key():
        pass

    def fake_scan(*args, **kwargs):
        scanned_receipt = {
            "id": "some-id",
            "name": "temp-receipt-name",
            "creation_timestamp": "2022-03-18 22:54:28.303959",
            "merchant_name": "Milton Sobeys Extra",
            "items": [
                {
                    "id": "some-id-1",
                    "price": 0.0,
                    "name": "Plastic Pull Bags",
                    "total_price": 0.1,
                    "quantity": 2.0
                },
                {
                    "id": "some-id-1",
                    "price": 0.0,
                    "name": "Rolo King",
                    "total_price": 2.19,
                    "quantity": 0.0
                }
            ]

        }
        return ReceiptSchema().load(scanned_receipt)

    monkeypatch.setattr("api.services.mongo_db.DBService.getDB", fake_mongo)
    monkeypatch.setattr(
        "flask_jwt_extended.view_decorators.verify_jwt_in_request", no_verify_jwt
    )
    monkeypatch.setattr("flask_jwt_extended.get_current_user", fake_get_user)
    monkeypatch.setattr(Utils, "getJwtPublicKey", fake_rsa_public_key)
    monkeypatch.setattr(AzureFormReco, "analyze_document", fake_scan)
    # from api.services.azure_form_reco import AzureFormReco


def test_get_all_receipts():
    # Setup
    from app import app

    db_instance = DBService.getInstance()
    list_collection = db_instance.get_collection("receipts")
    list_collection.insert_one(
        {
            "id": "temp-UUID-1",
            "name": "temp-name-1",
            "user": TEST_USER,
            "creation_timestamp": "temp-timestamp-1",
            "item_ids": ["item-1", "item-2"],
            "merchant_name": "Milton Sobeys Extra",
        }
    )
    list_collection.insert_one(
        {
            "id": "temp-UUID-2",
            "name": "temp-name-2",
            "user": TEST_USER,
            "creation_timestamp": "temp-timestamp-2",
            "item_ids": [],
            "merchant_name": "Freshco",
        }
    )
    list_collection.insert_one(
        {
            "id": "temp-UUID-2",
            "name": "temp-name-2",
            "user": "some-other-user",
            "creation_timestamp": "temp-timestamp-2",
            "item_ids": [],
            "merchant_name": "Freshco",
        }
    )

    item_collection = db_instance.get_collection("items")
    item_collection.insert_one(
        {"id": "item-1", "name": "Carrot",
            "quantity": 2, "price": 2, "total_price": 4}
    )
    item_collection.insert_one(
        {"id": "item-2", "name": "Banana",
            "quantity": 3, "price": 2, "total_price": 6}
    )

    # Execute
    app.testing = True
    response = app.test_client().get("/v1/receipts")
    res = json.loads(response.data.decode("utf-8")).get("receipts")

    # Assert
    assert response.status_code == 200
    assert res is not None
    receipts = ReceiptSchema(many=True).load(res)
    assert len(receipts) == 2
    assert receipts[0].id == "temp-UUID-1"
    assert receipts[0].name == "temp-name-1"
    assert receipts[0].creation_timestamp == "temp-timestamp-1"
    assert receipts[0].merchant_name == "Milton Sobeys Extra"
    assert len(receipts[0].items) == 2
    assert receipts[1].id == "temp-UUID-2"
    assert receipts[1].name == "temp-name-2"
    assert receipts[1].creation_timestamp == "temp-timestamp-2"
    assert receipts[1].merchant_name == "Freshco"
    assert len(receipts[1].items) == 0


def test_create_new_receipt():
    # Setup
    from app import app

    db_instance = DBService.getInstance()
    collection = db_instance.get_collection("receipts")

    # Execute
    app.testing = True
    response = app.test_client().post(
        "/v1/receipts",
        json={
            "name": "temp-name-1",
            "creation_timestamp": "2021-11-16 18:09:00.000000",
            "merchant_name": "Milton Sobeys Extra",
            "items": [{"id": "item-1", "name": "Carrot", "quantity": 2, "price": 2, "total_price": 4}],
        },
    )
    id = json.loads(response.data.decode("utf-8")).get("id")

    # Assert
    assert response.status_code == 201
    receipt = collection.find_one({"id": id})
    assert receipt is not None
    assert receipt["name"] == "temp-name-1"
    assert receipt["creation_timestamp"] == "2021-11-16 18:09:00.000000"
    assert receipt["merchant_name"] == "Milton Sobeys Extra"
    assert receipt["item_ids"] is not None
    item_collection = db_instance.get_collection("items")
    for id in receipt["item_ids"]:
        item = item_collection.find_one({"id": id})
        assert item["name"] == "Carrot"
        assert item["quantity"] == 2
        assert item["price"] == 2
        assert item["total_price"] == 4


def test_delete_receipt():
    # Setup
    from app import app

    db_instance = DBService.getInstance()
    list_collection = db_instance.get_collection("receipts")
    list_collection.insert_one(
        {
            "id": "temp-UUID-2",
            "name": "temp-name-2",
            "user": TEST_USER,
            "creation_timestamp": "2021-11-16 18:09:00.000000",
            "item_ids": ["item-1"],
            "merchant_name": "Freshco",
        }
    )

    item_collection = db_instance.get_collection("items")
    item_collection.insert_one(
        {"id": "item-1", "name": "Carrot",
            "quantity": 2, "price": 2, "total_price": 4}
    )

    # Execute
    app.testing = True
    response = app.test_client().delete("/v1/receipts/temp-UUID-2")

    # Assert
    assert response.status_code == 200
    receipt = list_collection.find_one({"id": "temp-UUID-2"})
    assert receipt is None

    item = item_collection.find_one({"id": "item-1"})
    assert item is None

def test_scan_receipt():
    # Setup
    from app import app

    # Execute
    app.testing = True
    
    with tempfile.NamedTemporaryFile(suffix=".png") as file:
        file.write(b'Hello world!')
        response = app.test_client().post("/v1/receipts/scan", data = {
            "file": file
        })

    scanned_receipt = json.loads(response.data.decode("utf-8"))

    assert scanned_receipt is not None
    assert "id" not in scanned_receipt
    assert "name" not in scanned_receipt
    assert scanned_receipt["merchant_name"] == "Milton Sobeys Extra"
    assert scanned_receipt["creation_timestamp"] == "2022-03-18 22:54:28.303959"
    assert "id" not in scanned_receipt["items"][0]
    assert scanned_receipt["items"][0]["name"] == "Plastic Pull Bags"
    assert scanned_receipt["items"][0]["price"] == 0.0
    assert scanned_receipt["items"][0]["total_price"] == 0.1
    assert scanned_receipt["items"][0]["quantity"] == 2.0
    assert "id" not in scanned_receipt["items"][1]
    assert scanned_receipt["items"][1]["name"] == "Rolo King"
    assert scanned_receipt["items"][1]["price"] == 0.0
    assert scanned_receipt["items"][1]["total_price"] == 2.19
    assert scanned_receipt["items"][1]["quantity"] == 0.0

   


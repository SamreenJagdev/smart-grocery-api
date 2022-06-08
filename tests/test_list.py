import json

import pytz
from api.schemas.list import ListSchema
from api.services.utils import Utils
from datetime import datetime
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

    def fake_now():
        tz = pytz.timezone('America/Toronto')
        return datetime.strptime("2022-03-20 12:39:04.451519", "%Y-%m-%d %H:%M:%S.%f").replace(tzinfo=tz)

    monkeypatch.setattr("api.services.mongo_db.DBService.getDB", fake_mongo)
    monkeypatch.setattr(
        "flask_jwt_extended.view_decorators.verify_jwt_in_request", no_verify_jwt
    )
    monkeypatch.setattr("flask_jwt_extended.get_current_user", fake_get_user)
    monkeypatch.setattr(Utils, "getJwtPublicKey", fake_rsa_public_key)
    monkeypatch.setattr(Utils, "timenow", fake_now)


def test_get_all_lists():
    # Setup
    from app import app

    db_instance = DBService.getInstance()
    list_collection = db_instance.get_collection("lists")
    list_collection.insert_one(
        {
            "id": "temp-UUID-1",
            "name": "temp-name-1",
            "user": TEST_USER,
            "creation_timestamp": "temp-timestamp-1",
            "item_ids": ["item-1", "item-2"],
        }
    )
    list_collection.insert_one(
        {
            "id": "temp-UUID-2",
            "name": "temp-name-2",
            "user": TEST_USER,
            "creation_timestamp": "temp-timestamp-2",
            "item_ids": [],
        }
    )

    item_colllection = db_instance.get_collection("items")
    item_colllection.insert_one(
        {"id": "item-1", "name": "Carrot", "category": "Veggie", "quantity": 2}
    )
    item_colllection.insert_one(
        {"id": "item-2", "name": "Banana", "category": "Fruit", "quantity": 3}
    )

    # Execute
    app.testing = True
    response = app.test_client().get("/v1/lists")
    res = json.loads(response.data.decode("utf-8")).get("lists")

    # Assert
    assert response.status_code == 200
    assert res is not None
    lists = ListSchema(many=True).load(res)
    assert lists[0].id == "temp-UUID-1"
    assert lists[0].name == "temp-name-1"
    assert lists[0].creation_timestamp == "temp-timestamp-1"
    assert len(lists[0].items) == 2
    assert lists[1].id == "temp-UUID-2"
    assert lists[1].name == "temp-name-2"
    assert lists[1].creation_timestamp == "temp-timestamp-2"
    assert len(lists[1].items) == 0


def test_create_new_list():
    # Setup
    from app import app

    db_instance = DBService.getInstance()
    collection = db_instance.get_collection("lists")

    # Execute
    app.testing = True
    response = app.test_client().post(
        "/v1/lists",
        json={
            "name": "temp-name-1",
            "creation_timestamp": "temp-timestamp-1",
            "items": [{"category": "Veggie", "quantity": 6.3, "name": "Carrot"}],
        },
    )
    id = json.loads(response.data.decode("utf-8")).get("id")

    # Assert
    assert response.status_code == 201
    list = collection.find_one({"id": id})
    assert list is not None
    assert list["name"] == "temp-name-1"
    assert list["creation_timestamp"] == "temp-timestamp-1"
    assert list["item_ids"] is not None
    item_collection = db_instance.get_collection("items")
    for id in list["item_ids"]:
        item = item_collection.find_one({"id": id})
        assert item["name"] == "Carrot"
        assert item["category"] == "Veggie"
        assert item["quantity"] == 6.3


def test_update_list():
    # Setup
    from app import app

    db_instance = DBService.getInstance()
    collection = db_instance.get_collection("lists")
    collection.insert_one(
        {
            "id": "temp-UUID-1",
            "name": "temp-name-1",
            "user": TEST_USER,
            "creation_timestamp": "temp-timestamp-1",
            "item_ids": [],
        }
    )

    # Execute
    app.testing = True
    response = app.test_client().put(
        "/v1/lists/temp-UUID-1",
        json={"name": "new-name-1", "creation_timestamp": "new-timestamp-1", "items": [
            {"category": "Veggie", "quantity": 6.7, "name": "Carrot"}, {"category": "Fruit", "quantity": 2, "name": "Apple"}]},
    )

    # Assert
    assert response.status_code == 200
    list = collection.find_one({"id": "temp-UUID-1"})
    assert list is not None
    assert list["name"] == "new-name-1"
    assert list["creation_timestamp"] != "new-timestamp-1"
    assert len(list["item_ids"]) == 2


def test_delete_list():
    # Setup
    from app import app

    db_instance = DBService.getInstance()
    collection = db_instance.get_collection("lists")
    collection.insert_one(
        {
            "id": "temp-UUID-1",
            "name": "temp-name-1",
            "user": TEST_USER,
            "creation_timestamp": "temp-timestamp-1",
            "item_ids": ["item-1", "item-2"],
        }
    )

    # Execute
    app.testing = True
    response = app.test_client().delete("/v1/lists/temp-UUID-1")

    # Assert
    assert response.status_code == 200
    list = collection.find_one({"id": "temp-UUID-1"})
    assert list is None


def test_predict_list():
    # Setup
    from app import app

    db_instance = DBService.getInstance()
    list_collection = db_instance.get_collection("lists")
    item_colllection = db_instance.get_collection("items")

    # List 1
    list_collection.insert_one(
        {
            "id": "temp-UUID-1",
            "name": "temp-name-1",
            "user": TEST_USER,
            "creation_timestamp": "2022-03-20 12:39:04.451519",
            "item_ids": ["item-1", "item-2", "item-3", "item-4"],
        }
    )
    item_colllection.insert_one(
        {"id": "item-1", "name": "Carrot", "category": "Veggie", "quantity": 2}
    )
    item_colllection.insert_one(
        {"id": "item-2", "name": "Banana", "category": "Fruit", "quantity": 3}
    )
    item_colllection.insert_one(
        {"id": "item-3", "name": "Apple", "category": "Fruit", "quantity": 4}
    )
    item_colllection.insert_one(
        {"id": "item-4", "name": "Peach", "category": "Fruit", "quantity": 2}
    )

    # List 2
    list_collection.insert_one(
        {
            "id": "temp-UUID-2",
            "name": "temp-name-2",
            "user": TEST_USER,
            "creation_timestamp": "2022-03-20 12:39:04.451519",
            "item_ids": ["item-5", "item-6", "item-7"],
        }
    )
    item_colllection.insert_one(
        {"id": "item-5", "name": "Spinach", "category": "Veggie", "quantity": 2}
    )
    item_colllection.insert_one(
        {"id": "item-6", "name": "Banana", "category": "Fruit", "quantity": 3}
    )
    item_colllection.insert_one(
        {"id": "item-7", "name": "Mango", "category": "Fruit", "quantity": 1}
    )

    # List 3
    list_collection.insert_one(
        {
            "id": "temp-UUID-3",
            "name": "temp-name-3",
            "user": TEST_USER,
            "creation_timestamp": "2022-02-02 12:39:04.451519",
            "item_ids": ["item-8", "item-9", "item-10"],
        }
    )
    item_colllection.insert_one(
        {"id": "item-8", "name": "Spinach", "category": "Veggie", "quantity": 2}
    )
    item_colllection.insert_one(
        {"id": "item-9", "name": "Tomato", "category": "Veggie", "quantity": 3}
    )
    item_colllection.insert_one(
        {"id": "item-10", "name": "Potato", "category": "Veggie", "quantity": 1}
    )

    # List 4
    list_collection.insert_one(
        {
            "id": "temp-UUID-4",
            "name": "temp-name-4",
            "user": TEST_USER,
            "creation_timestamp": "2022-03-02 12:39:04.451519",
            "item_ids": ["item-11", "item-12", "item-13", "item-14", "item-15", "item-16", "item-17", "item-18", "item-19", "item-20"],
        }
    )
    item_colllection.insert_one(
        {"id": "item-11", "name": "Spinach", "category": "Veggie", "quantity": 2}
    )
    item_colllection.insert_one(
        {"id": "item-12", "name": "Tomato", "category": "Veggie", "quantity": 3}
    )
    item_colllection.insert_one(
        {"id": "item-13", "name": "Beet", "category": "Veggie", "quantity": 1}
    )
    item_colllection.insert_one(
        {"id": "item-14", "name": "Spinach", "category": "Veggie", "quantity": 2}
    )
    item_colllection.insert_one(
        {"id": "item-15", "name": "Apple", "category": "Fruit", "quantity": 3}
    )
    item_colllection.insert_one(
        {"id": "item-16", "name": "Carrot", "category": "Veggie", "quantity": 1}
    )
    item_colllection.insert_one(
        {"id": "item-17", "name": "Mango", "category": "Fruit", "quantity": 3}
    )
    item_colllection.insert_one(
        {"id": "item-18", "name": "Grapes", "category": "Fruit", "quantity": 1}
    )
    item_colllection.insert_one(
        {"id": "item-19", "name": "Blueberries",
            "category": "Fruit", "quantity": 1}
    )
    item_colllection.insert_one(
        {"id": "item-20", "name": "Watermelon", "category": "Fruit", "quantity": 1}
    )

    # Execute
    app.testing = True
    response = app.test_client().post("/v1/lists/predict")
    items = json.loads(response.data.decode("utf-8")).get("items")

    # Assert
    assert response.status_code == 200
    assert items is not None
    assert items[0]["category"] == "Veggie"
    assert items[0]["name"] == "Spinach"
    assert items[1]["category"] == "Veggie"
    assert items[1]["name"] == "Carrot"
    assert items[2]["category"] == "Fruit"
    assert items[2]["name"] == "Banana"
    assert items[3]["category"] == "Fruit"
    assert items[3]["name"] == "Apple"
    assert items[4]["category"] == "Fruit"
    assert items[4]["name"] == "Mango"
    assert items[5]["category"] == "Fruit"
    assert items[5]["name"] == "Peach"
    assert items[6]["category"] == "Veggie"
    assert items[6]["name"] == "Tomato"
    assert items[7]["category"] == "Veggie"
    assert items[7]["name"] == "Beet"
    assert items[8]["category"] == "Fruit"
    assert items[8]["name"] == "Grapes"
    assert items[9]["category"] == "Fruit"
    assert items[9]["name"] == "Blueberries"

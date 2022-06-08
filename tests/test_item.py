import json
from api.models.list_model import ListModel, ListModelSchema
from api.schemas.listItem import ListItem, ListItemSchema
from api.schemas.list import ListSchema
from api.services.utils import Utils

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

    monkeypatch.setattr("api.services.mongo_db.DBService.getDB", fake_mongo)
    monkeypatch.setattr(
        "flask_jwt_extended.view_decorators.verify_jwt_in_request", no_verify_jwt
    )
    monkeypatch.setattr("flask_jwt_extended.get_current_user", fake_get_user)
    monkeypatch.setattr(Utils, "getJwtPublicKey", fake_rsa_public_key)


def test_get_all_items_for_list():
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

    item_colllection = db_instance.get_collection("items")
    item_colllection.insert_one(
        {"id": "item-1", "name": "Carrot", "category": "Veggie", "quantity": 2}
    )
    item_colllection.insert_one(
        {"id": "item-2", "name": "Banana", "category": "Fruit", "quantity": 3}
    )

    # Execute
    app.testing = True
    response = app.test_client().get("/v1/lists/temp-UUID-1/items")
    fetched_items = json.loads(response.data.decode("utf-8"))
    # Assert
    assert response.status_code == 200
    assert fetched_items is not None
    items = ListItemSchema(many=True).load(fetched_items["items"])
    assert items[0].id == "item-1"
    assert items[0].name == "Carrot"
    assert items[0].category == "Veggie"
    assert items[0].quantity == 2
    assert items[1].id == "item-2"
    assert items[1].name == "Banana"
    assert items[1].category == "Fruit"
    assert items[1].quantity == 3


def test_create_new_item_for_list():
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
            "item_ids": [],
        }
    )

    # Execute
    app.testing = True
    response = app.test_client().post(
        "/v1/lists/temp-UUID-1/items",
        json={"category": "Fruits", "name": "Banana", "quantity": 10},
    )
    id = json.loads(response.data.decode("utf-8")).get("id")
    # Assert
    assert response.status_code == 201

    item_collection = db_instance.get_collection("items")
    created_item: ListItem = ListItemSchema().load(item_collection.find_one({"id": id}))
    assert created_item.name == "Banana"
    assert created_item.category == "Fruits"
    assert created_item.quantity == 10

    list: ListModel = ListModelSchema().load(
        list_collection.find_one({"id": "temp-UUID-1"})
    )
    assert list.item_ids[0] == id


def test_update_item_for_list():
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
            "item_ids": ["item-1"],
        }
    )
    item_colllection = db_instance.get_collection("items")
    item_colllection.insert_one(
        {"id": "item-1", "name": "Carrot", "category": "Veggie", "quantity": 2}
    )

    # Execute
    app.testing = True
    response = app.test_client().put(
        "/v1/lists/temp-UUID-1/items/item-1",
        json={"category": "Fruits", "name": "Apple", "quantity": 4},
    )

    # Assert
    assert response.status_code == 200

    item_collection = db_instance.get_collection("items")
    created_item: ListItem = ListItemSchema().load(
        item_collection.find_one({"id": "item-1"})
    )
    assert created_item.name == "Apple"
    assert created_item.category == "Fruits"
    assert created_item.quantity == 4


def test_delete_item_for_list():
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
            "item_ids": ["item-1"],
        }
    )
    item_colllection = db_instance.get_collection("items")
    item_colllection.insert_one(
        {"id": "item-1", "name": "Carrot", "category": "Veggie", "quantity": 2}
    )

    # Execute
    app.testing = True
    response = app.test_client().delete("/v1/lists/temp-UUID-1/items/item-1")

    # Assert
    assert response.status_code == 200

    item_collection = db_instance.get_collection("items")
    find_item = item_collection.find_one({"id": "item-1"})
    assert find_item is None

    list = ListModelSchema().load(list_collection.find_one({"id": "temp-UUID-1"}))
    assert len(list.item_ids) == 0

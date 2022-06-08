from flask_restful import Resource
import pytz
from api.models.predict_item_model import PredictItemModelSchema
from api.services.mongo_db import DBService
from flask_jwt_extended import jwt_required, get_current_user
from datetime import datetime, timedelta

from api.services.utils import Utils


class ListsPredict(Resource):
    @jwt_required()
    def post(self):
        user = get_current_user()
        db = DBService.getInstance()
        collection = db.get_collection("lists")

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
                {"$unwind": "$items"},
                {
                    "$project": {
                        "name": "$items.name",
                        "category": "$items.category",
                        "creation_timestamp": "$creation_timestamp",
                        "_id": 0,
                    }
                },
            ]
        )

        items = PredictItemModelSchema(many=True).load(list(results))

        # Select all the unique items in past 30 days and record their count
        date_now = Utils.timenow()
        date_limit = date_now - timedelta(days=30)
        filtered_items = {}
        tz = pytz.timezone('America/Toronto')
        for item in items:
            if item["creation_timestamp"].replace(tzinfo=tz) >= date_limit:
                if (item["name"], item["category"]) in filtered_items:
                    filtered_items[(item["name"], item["category"])] = (
                        filtered_items[(item["name"], item["category"])] + 1
                    )
                else:
                    filtered_items[(item["name"], item["category"])] = 1

        # Sort the items by count, most frequent at the top
        sorted_items = []
        for (a, b) in filtered_items:
            sorted_items.append(
                {"name": a, "category": b, "count": filtered_items[(a, b)]}
            )
        sorted_items.sort(key=lambda x: x["count"], reverse=True)

        # Return list of top 10 items in sorted list
        return {
            "items": PredictItemModelSchema(
                many=True, exclude=["creation_timestamp"]
            ).load(sorted_items[:10])
        }, 200

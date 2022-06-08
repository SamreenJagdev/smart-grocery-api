import requests
from jwt.algorithms import RSAAlgorithm
import os
import json
from datetime import datetime
import pytz


ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg", "gif"}


class Utils:
    def has_allowed_extension(filename):
        return (
            "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
        )

    def getJwtPublicKey():
        jwks_uri = requests.get(os.getenv("JWKS_URI"), verify=False).json()
        return RSAAlgorithm.from_jwk(json.dumps(jwks_uri["keys"][1]))

    def timenow():
        tz = pytz.timezone('America/Toronto')
        return datetime.now(tz)

    def get_timestamp(date, time):
        result = ""
        if date is not None:
            if time is not None:
                result = datetime.combine(date,time)
                return result.strftime("%Y-%m-%d %H:%M:%S.%f")
            result = date
            return result.strftime("%Y-%m-%d %H:%M:%S.%f")
        return None

from . import api_v1
from werkzeug.exceptions import HTTPException
import json


@api_v1.app_errorhandler(HTTPException)
def generic_error(e):
    response = e.get_response()
    response.data = json.dumps({
        "success": False,
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response

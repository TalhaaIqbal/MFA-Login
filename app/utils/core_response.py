from fastapi.responses import JSONResponse
from logging_config import logger
from bson import ObjectId
from fastapi.encoders import jsonable_encoder



async def core_response(
    message: str,
    status_code: int,
    data: dict | list | None = None
):
    safe_data = jsonable_encoder(data, custom_encoder={ObjectId: str})

    response_dict = {
        "message": message,
        "success": 1,
        "data": safe_data
    }
    if not status_code in [200, 201]:
        response_dict["success"] = 0
        
        # Log error responses
        if 300 <= status_code < 400:
            logger.warning(f"[HTTP {status_code}] Redirect response - Status: {status_code}, Message: {message}")
        elif 400 <= status_code < 500:
            logger.error(f"[HTTP {status_code}] Client error - Status: {status_code}, Message: {message}")
        elif 500 <= status_code < 600:
            logger.error(f"[HTTP {status_code}] Server error - Status: {status_code}, Message: {message}")

    return JSONResponse(
        status_code=status_code,
        content=response_dict
    )
        


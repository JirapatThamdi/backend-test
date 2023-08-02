import cv2
import numpy as np
from PIL import Image
import io
import base64
from enum import IntEnum
from bson import ObjectId
from model.model import ImageModel, ImageResponseModel
from config import database
from fastapi import APIRouter, Depends, Body, status, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import Annotated
from core.auth import validate_user

# Create API router
router = APIRouter(tags=["face"])
mongodb_obj = database.MongoDbInterface("images")
mongodb_user = database.MongoDbInterface("users")

class SortModel(IntEnum):
    Newest_to_Oldest = 1
    Oldest_to_Newest = -1

def base642image(base64str: str, use_opencv: bool = False):
    """
    Convert base64 string to image
    Parameters:
        base64str: str
        use_opencv: bool
    Returns:
        image: np.array or PIL.Image
    """
    image = None
    if use_opencv:
        data_bytes = np.frombuffer(base64.b64decode(base64str), np.uint8)
        image = cv2.imdecode(data_bytes, cv2.IMREAD_COLOR)
    else:
        image_bytes = base64.b64decode(base64str)
        image = Image.open(io.BytesIO(image_bytes))
    return image


def detect_faces(image: np.array):
    """
    Detect faces in an image using the Haar Cascade classifier
    Parameters:
        image: np.array

    Returns:
        image: np.array
    """

    # Load the Haar Cascade classifier for face detection
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    # Convert the image to grayscale for face detection
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect faces in the image using the Haar Cascade classifier
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

    # Draw bounding boxes around the detected faces
    for x, y, w, h in faces:
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

    return image

async def add_access_to_dict(user_id: str) -> list[dict]:
    """
    Add access information to document dict.
    """
    user_id_obj = ObjectId(user_id)
    access = [
        {
            "userId": user_id_obj,
        }
    ]

    return access


# Define the FastAPI endpoint
@router.post("/detect_faces")
async def detect_faces_endpoint(user_auth: Annotated[dict, Depends(validate_user)], image_base64: ImageModel = Body(...)):
    image_dict = jsonable_encoder(image_base64)
    # Convert base64 string to image
    image = base642image(image_dict['base64'], use_opencv=True)

    # Detect faces in the image
    image_out = detect_faces(image)
    
    # Convert the image to base64 string
    _, buffer = cv2.imencode(".jpg", image_out)
    b64str_out = base64.b64encode(buffer).decode('utf-8')
    image_dict["base64"] = b64str_out
    image_dict["access"] = await add_access_to_dict(user_auth['user_id'])

    user = await mongodb_user.get_document_by_id(user_auth['user_id'])

    if user_auth['api_quota_limit'] > 0:
        create_image = await mongodb_obj.create_document(image_dict)
        await mongodb_user.update_document_by_id(user_auth['user_id'], {"api_quota_limit":user['api_quota_limit']-1})
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Your quota out of limit.")

    cv2.imwrite("output/result.jpg", image_out)

    return JSONResponse(status_code=status.HTTP_201_CREATED,
                        content=jsonable_encoder(ImageResponseModel(**create_image)))

@router.get('/', response_model=list[ImageResponseModel])
async def get_all_images(user_auth: Annotated[dict, Depends(validate_user)], sort_value: SortModel = 1):

    if sort_value == SortModel.Newest_to_Oldest:
        query = {"access.userId": ObjectId(user_auth["user_id"])}
        images = await mongodb_obj.get_documents(query, 1)
    
    if sort_value == SortModel.Oldest_to_Newest:
        query = {"access.userId": ObjectId(user_auth["user_id"])}
        images = await mongodb_obj.get_documents(query, -1)

    if images is None:
        raise HTTPException(status_code=404, detail="No image found")
    return images

@router.get('/{id}', response_model=ImageResponseModel)
async def get_images_specific_id(user_auth: Annotated[dict, Depends(validate_user)], id:str):

    image = await mongodb_obj.get_document_by_id(id)

    if image:
        return image
    raise HTTPException(status_code=404, detail=f"No image found")

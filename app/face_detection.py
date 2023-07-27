import cv2
import numpy as np
from PIL import Image
import io
import base64
from fastapi import APIRouter

# Create API router
router = APIRouter(tags=["face"])


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


# Define the FastAPI endpoint
@router.post("/detect_faces")
def detect_faces_endpoint(image_base64: str):
    # Convert base64 string to image
    image = base642image(image_base64, use_opencv=True)

    # Detect faces in the image
    image_out = detect_faces(image)

    # Convert the image to base64 string
    _, buffer = cv2.imencode(".jpg", image_out)
    b64str_out = base64.b64encode(buffer)

    return {"result": b64str_out}

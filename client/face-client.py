import requests
import base64
from PIL import Image
from io import BytesIO
import io
import cv2
import numpy as np


def image2base64(image_file_path: str, use_opencv: bool = False):
    """
    Convert image to base64 string
    Parameters:
        image_file_path: str
        use_opencv: bool
    Returns:
        base64str: str
    Note:
        The image format fixed to JPEG but it also suport on other format too
    """
    base64str = ""
    if use_opencv:
        image = cv2.imread(image_file_path)
        _, buffer = cv2.imencode(".jpg", image)
        base64str = base64.b64encode(buffer)
    else:
        with open(image_file_path, "rb") as image_file:
            image = Image.open(image_file).convert("RGB")
            buffered = BytesIO()
            image.save(buffered, format="JPEG")
            base64str = base64.b64encode(buffered.getvalue())
    return base64str.decode("utf-8")


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


# Read the image file
b64str = image2base64("client/test_image.png", use_opencv=True)

url = "http://0.0.0.0:8000/detect_faces"
params = {"image_base64": b64str}
headers = {"accept": "application/json"}

response = requests.post(url, params=params, headers=headers)
image = base642image(response.json()["result"], use_opencv=True)
cv2.imwrite("output/result.jpg", image)

from jose import JWTError, jwt, ExpiredSignatureError
from fastapi import APIRouter, Body, HTTPException, status, Response, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from datetime import datetime, timedelta
import pymongo

router = APIRouter()
security = HTTPBearer()

# Secret key for signing and verifying tokens (keep it secret!)
SECRET_KEY = 'your_secret_key_here'

# Function to generate a JWT token
async def generate_token(data, expiration_minutes=30) -> str:
    payload = {
        "exp": datetime.utcnow() + timedelta(minutes=expiration_minutes),
        "iat": datetime.utcnow(),
        "user_id": str(data["_id"]),
        "email": data["email"],
        "created_at": data["createdAt"],
        "token_type": "access_token"
    }
    encode_jwt = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return encode_jwt

async def generate_refresh_token(data: dict) -> str:
    """
    Generate refresh token.
    """
    expire = datetime.utcnow() + timedelta(minutes=data["maxRefreshTokenMins"])
    payload_to_encode = {
        "exp": expire,
        "iat": datetime.utcnow(),
        "user_id": str(data["_id"]),
        "email": data["email"],
        "created_at": data["createdAt"],
        "token_type": "refresh_token"
    }
    encoded_jwt = jwt.encode(
        payload_to_encode, SECRET_KEY, algorithm='HS256')
    return encoded_jwt


# Function to verify and decode a JWT token
async def verify_token(token:str) -> dict:
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        # check if token is expired
        if datetime.utcnow() > datetime.fromtimestamp(decoded_token["exp"]):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Token expired")
        return decoded_token

    except ExpiredSignatureError:
        return 'Token has expired.'
    except JWTError:
        return 'Invalid token.'

async def validate_user(authorization_header: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    user = await verify_token(authorization_header.credentials)

    return user

from model.model import UserModel, UserLoginModel, UserResponseModel, RefreshTokenModel, verify_password
from config import database
from fastapi import (APIRouter, Body,
                     HTTPException, status,
                     Response, Depends,
                     Request, Security,
                     Header)
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from core.auth import (generate_refresh_token, generate_token, verify_token)

router = APIRouter()
mongodb_obj = database.MongoDbInterface("users")

@router.post("/register")
async def sign_up(user: UserModel = Body(...)):

    user_dict: dict = jsonable_encoder(user, exclude={"password"})

    created_user = await mongodb_obj.create_document(user_dict)
    if created_user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="User creation failed, Email already exists")

    return JSONResponse(status_code=status.HTTP_201_CREATED,
                        content=jsonable_encoder(UserResponseModel(**created_user),
                                                 by_alias=False))

@router.post("/login")
async def login(user: UserLoginModel = Body(...)):
    user_dict: dict = jsonable_encoder(user)

    check_user = await mongodb_obj.get_document({"email":user_dict['email']})
    if check_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not Found.")

    if not verify_password(user_dict['password'], check_user["hashedPassword"]):
        raise HTTPException(status_code=status.HTTP_401_NOT_FOUND, detail="Password incorrect.")

    access_token = await generate_token(check_user)
    refresh_token = await generate_refresh_token(check_user)

    await mongodb_obj.update_document_by_id(check_user["_id"],{"refreshToken":refresh_token})

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"access_token": access_token,
                                 "refresh_token": refresh_token})

@router.post('/refreshtoken')
async def get_refresh_token(refresh_token: RefreshTokenModel):
    """
    Refresh access token using refresh token.
    """
    # convert pydantic object to dict
    refresh_token_dict: dict = jsonable_encoder(refresh_token)
    # verify refresh token
    decoded_token = await verify_token(refresh_token_dict["refreshToken"])

    # get user from db and check if refresh token is same
    user_from_db = await mongodb_obj.get_document_by_id(decoded_token["user_id"])
    if user_from_db is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Refresh token not available")

    if user_from_db["refreshToken"] != refresh_token_dict["refreshToken"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid refresh token")

    # generate and return access token
    access_token = await generate_token(user_from_db)
    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"access_token": access_token})




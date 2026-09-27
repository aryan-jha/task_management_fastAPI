from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from fastapi import BackgroundTasks, HTTPException, Request, status
from jwt import InvalidTokenError
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from app.common.utils import sendEmail
from app.core.config import settings
from app.modules.users.model import UserModel
from app.modules.users.schema import UserLoginSchema, UserPublicSchema, UserSchema

password_hash: PasswordHash = PasswordHash.recommended()


def hashPassword(password: str):
    return password_hash.hash(password)


def verifyPassword(plainPassword: str, hashedPassword: str) -> bool:

    return password_hash.verify(plainPassword, hashedPassword)


async def register(data: UserSchema, db: Session, bg_task: BackgroundTasks) -> Any:

    is_username_exists: UserModel | None = (
        db.query(UserModel).filter(data.username == UserModel.username).first()
    )

    if is_username_exists:
        raise HTTPException(400, "Username already exists")

    is_email_exists: UserModel | None = (
        db.query(UserModel).filter(data.email == UserModel.email).first()
    )

    if is_email_exists:
        raise HTTPException(400, "User email already exists")

    hashed_password = hashPassword(data.password)

    new_user = UserModel(
        name=data.name,
        email=data.email,
        username=data.username,
        hased_password=hashed_password,
        mobile_number=data.mobile_number,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    bg_task.add_task(sendEmail, [data.email], name=data.name)
    return {
        "status": status.HTTP_201_CREATED,
        "message": "User registered successfully",
        "data": new_user,
    }


def login(data: UserLoginSchema, db: Session):

    user: UserModel | None = (
        db.query(UserModel).filter(data.email == UserModel.email).first()
    )

    if not user:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, "Entered email doesn't exists!"
        )

    if not verifyPassword(data.password, user.hased_password):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, "Entered password is incorrect!"
        )

    expiry_time: datetime = datetime.now(UTC) + timedelta(days=settings.EXPIRY_TIME)
    print(expiry_time)
    userToken: str = jwt.encode(
        {"id": user.id, "exp": expiry_time.timestamp()},
        settings.SECRET_KEY,
        settings.TOKEN_ALGO,
    )

    return {
        "status": status.HTTP_200_OK,
        "message": "User logged in successfully",
        "data": {
            **UserPublicSchema.model_validate(user).model_dump(),
            "token": userToken,
        },
    }


def is_authenticated(request: Request, db: Session):

    try:
        user_token: str = request.headers.get("Authorization", "").split(" ")[-1]

        decoded_token: Any | None = jwt.decode(
            user_token, settings.SECRET_KEY, settings.TOKEN_ALGO
        ).get("id")

        user: UserModel | None = (
            db.query(UserModel).filter(UserModel.id == decoded_token).first()
        )

        if not user:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "You are unauthorized!")

        return {
            "status": status.HTTP_200_OK,
            "message": "User details fetched successfully",
            "data": {
                **UserPublicSchema.model_validate(user).model_dump(),
                "token": user_token,
            },
        }

    except InvalidTokenError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "You are unauthorized!")

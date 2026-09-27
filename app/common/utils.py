from typing import Annotated, Any

import jwt
from fastapi import Depends, HTTPException, Request, status
from jwt import InvalidTokenError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.connection import get_db
from app.modules.users.model import UserModel
from app.modules.users.schema import UserPublicSchema


def is_authenticated(request: Request, db: Annotated[Session, Depends(get_db)]):

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

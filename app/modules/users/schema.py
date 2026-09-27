import pydantic.config
from pydantic import BaseModel, ConfigDict


class UserSchema(BaseModel):
    name: str
    username: str
    email: str
    password: str
    mobile_number: str


class UserPublicSchema(BaseModel):
    model_config: ConfigDict = ConfigDict(from_attributes=True)
    id: int
    name: str
    username: str
    email: str
    mobile_number: str


class UserResponseSchema(BaseModel):
    status: int
    message: str
    data: UserPublicSchema


class UserLoginSchema(BaseModel):
    email: str
    password: str


class UserPublicLoginSchema(BaseModel):
    model_config: ConfigDict = ConfigDict(from_attributes=True)

    id: int
    name: str
    username: str
    email: str
    mobile_number: str
    token: str


class UserResponseLoginSchema(BaseModel):
    status: int
    message: str
    data: UserPublicLoginSchema

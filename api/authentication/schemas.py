from pydantic import BaseModel,Field,validator
from tortoise.contrib.pydantic import pydantic_model_creator
from api.models.models import User

class UserPOST(BaseModel):
    username:str = Field(...,max_length=200)
    first_name:str = Field(...,max_length=200)
    last_name:str = Field(...,max_length=200)
    phone:str = Field(...,max_length=200)
    password1:str = Field(max_length=200)
    password2:str = Field(max_length=200)

    @validator('*', pre=True)
    def check_fields(cls, value):
        if value is None:
            raise ValueError("All fields must have a value")
        return value

    @validator('username')
    def validate_username(cls,username):
        if len(username) < 4:
            raise ValueError("username is too short")
        return username
    
    @validator('phone')
    def validate_phone(cls,phone):
        bphone = phone.replace('+','',1)
        if not bphone.isdigit():
            raise ValueError("Wrong format of phone number")
        return phone

    @validator('password2')
    def password_matches(cls,password2,values):
        if 'password1' in values and password2 != values['password1']:
            raise ValueError("Passwords do not match")
        return password2

class UserGET(BaseModel):
    username:str = Field(...,max_length=200)
    first_name:str = Field(...,max_length=200)
    last_name:str = Field(...,max_length=200)
    phone:str = Field(...,max_length=200)


class TokenGET(BaseModel):
    access_token:str = Field(...,max_length=200)
    token_type:str = Field(...,max_length=50)

GetUser = pydantic_model_creator(User,name="user")
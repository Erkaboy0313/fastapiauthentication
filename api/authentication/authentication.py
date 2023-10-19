from fastapi import Depends,HTTPException,status,APIRouter
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from jose import JWTError,jwt
from passlib.context import CryptContext
from .schemas import TokenGET,UserPOST

from datetime import datetime,timedelta
from typing import Annotated
from config import settings


from api.models.models import User

pwd_context = CryptContext(schemes=['bcrypt'],deprecated = "auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/auth/login/')

auth_router = APIRouter(prefix='/api/auth',tags=['authenticate'])

async def check_password(plain_password:str,hashed_password:str) -> bool:
    """
    checks user's entered plain password with hashed password in db
    """
    return await pwd_context.verify(plain_password,hashed_password)

async def get_user(username: str) -> User:
    """
    Gets user from database which username matchs to given username. If not found raises Exception.
    """
    try:
        user = await User.get(username = username)
        return user
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")

async def authenticate_user(username:str,password:str) -> User:
    print(username)
    user = await get_user(username)
    print(user)
    if pwd_context.verify(password,user.password):
        return user
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def create_access_token(data:dict, life_time: timedelta | None):
    """
    Creates access token
    """
    if not life_time:
        life_time = timedelta(minutes=30)
    expire = datetime.utcnow() + life_time
    data.update({"exp":expire})
    token = jwt.encode(data,settings.SECRET_KEY,algorithm=settings.ALGORITHM)
    return token

async def get_current_user(token: Annotated[str,Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token,settings.SECRET_KEY,algorithms=settings.ALGORITHM)
        username:str = payload.get('username')
        if username is None:
            raise credentials_exception
    except:
        raise credentials_exception
    user = User.get(username = username)
    return user

@auth_router.post('/login/',response_model=TokenGET)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = await authenticate_user(form_data.username,form_data.password)
    data = {
        "username":user.username
    }
    token_expire_time = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(data,token_expire_time)
    data = {"access_token": access_token, "token_type": "bearer"}
    return TokenGET(**data)

@auth_router.post('/register/',status_code=status.HTTP_200_OK)
async def register(data:UserPOST):
    try:
        userdata = UserPOST(**data.model_dump())
        hashed_password = pwd_context.hash(userdata.password1)
        userdata = userdata.model_dump()
        userdata.update({"password":hashed_password})
        await User.create(**userdata)
        return {"detail":"user created"}
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="all field must have value")



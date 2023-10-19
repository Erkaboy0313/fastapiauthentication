from fastapi import FastAPI,status,Depends
from api.authentication.authentication import auth_router,get_current_user
from tortoise.contrib.fastapi import register_tortoise
from api.authentication.schemas import UserGET,GetUser
from typing import Annotated

app = FastAPI()
app.include_router(auth_router)

register_tortoise(
    app=app,
    db_url="sqlite://authentication.db",
    add_exception_handlers=True,
    generate_schemas=True,
    modules={"models":['api.models.models']}
)

@app.get('/',status_code=status.HTTP_200_OK)
async def home():
    return {'info':"Authentication app is running"}

@app.get('/user-info/',response_model=UserGET)
async def user_info(user:Annotated[UserGET, Depends(get_current_user)]):
    return await GetUser.from_queryset_single(user)
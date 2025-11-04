from app.models.user_model import Token, UserPublic
from fastapi import APIRouter, Depends 
from app.dependencies import user_dependency
 
router = APIRouter() 
@router.post("/", response_model=UserPublic) 
async def register(register_user: UserPublic = Depends(user_dependency.register)): 
    return register_user 


@router.post("/login/", response_model=Token) 
async def login(token: Token = Depends(user_dependency.login)): 
    return token 

@router.get("/", response_model=UserPublic) 
async def get_user(get_user: UserPublic = Depends(user_dependency.get_user)): 
    return get_user 

@router.patch("/", response_model=UserPublic)
async def update(update_user: UserPublic = Depends(user_dependency.update_user)): 
    return update_user
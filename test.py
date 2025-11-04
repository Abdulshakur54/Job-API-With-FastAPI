from fastapi import FastAPI, Depends, HTTPException, status
from typing import Annotated
from pydantic import BaseModel
import jwt
from jwt import InvalidTokenError
from pwdlib import PasswordHash
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from dotenv import load_dotenv
import os
from datetime import datetime, timezone, timedelta

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

app = FastAPI()

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$argon2id$v=19$m=65536,t=3,p=4$wagCPXjifgvUFBzq4hqe3w$CYaIb8sB+wtD+Vu/P4uod1+Qof8h+1g7bbDlBID48Rc",
        "disabled": False,
    }
}


class Token(BaseModel):
    access_token: str
    token_type: str


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str


def get_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credential_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except InvalidTokenError:
        raise credential_error
    username = decoded_token.get('sub')
    if username is None:
        raise credential_error
    user = fake_users_db.get(username)
    if username.disabled:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User is inactive"
        )
    return user


def generate_token(data) -> str:
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def authenticate_user(db, username: str, password: str):
    if username in db:
        user = db[username]
        if password_hash.verify(password, user['hashed_password']):
            return user
    return False


@app.post("/login")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username and Password not matching",
            headers={"WWW-Authenticate": "Bearer"},
        )
    expiry = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = generate_token({"sub": user['username'], "exp": expiry})
    return Token(access_token=token, token_type="bearer")


@app.get("/users/me")
async def read_user_me(user: Annotated[User, Depends(get_user)]) -> User:
    return user


@app.get("/users/me/items/")
async def read_own_items(
    user: Annotated[User, Depends(get_user)],
):
    return [{"item_id": "Foo", "owner": user.username}]

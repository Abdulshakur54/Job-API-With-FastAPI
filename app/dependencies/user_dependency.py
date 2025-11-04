from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.db import get_session
from ..models.user_model import Token, User, UserCreate, UserPublic, UserUpdate
from pwdlib import PasswordHash
from datetime import datetime, timezone, timedelta
import os
import jwt
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="user/login")


def get_username(token: Annotated[str, Depends(oauth2_scheme)]) -> str:
    """Extract username from JWT token."""
    credential_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.InvalidTokenError:
        raise credential_error

    username = decoded_token.get("sub")
    if username is None:
        raise credential_error
    return username


async def get_user(
    username: Annotated[str, Depends(get_username)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserPublic:
    result = await session.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserPublic(**user.model_dump())


async def authenticate_user(
    session: AsyncSession, username: str, password: str
) -> User | None:
    """Check if username/password is correct."""
    result = await session.execute(select(User).where(User.username == username.lower()))
    user = result.scalars().first()
    if user and password_hash.verify(password, user.hashed_password):
        return user
    return None


def generate_token(data: dict) -> str:
    """Generate JWT token with data payload."""
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Token:
    """Authenticate user and return access token."""
    user = await authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username and password do not match",
            headers={"WWW-Authenticate": "Bearer"},
        )

    expiry = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = generate_token({"sub": user.username, "exp": int(expiry.timestamp())})

    return Token(access_token=token, token_type="bearer")


async def get_existing_user(session: AsyncSession, username: str) -> User | None:
    return (
        (await session.execute(select(User).where(User.username == username)))
        .scalars()
        .first()
    )


async def register(
    session: Annotated[AsyncSession, Depends(get_session)], user: UserCreate
) -> UserPublic:
    try:
        # Check username
        existing_user = await get_existing_user(session, user.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Username already exists"
            )

        # Check email (optional)
        existing_email = (
            (await session.execute(select(User).where(User.email == user.email)))
            .scalars()
            .first()
        )
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
            )

        val_user = User(
            full_name=user.full_name,
            email=user.email,
            username=user.username.lower(),
            hashed_password=password_hash.hash(user.password),
        )

        session.add(val_user)
        await session.commit()
        await session.refresh(val_user)

        return UserPublic(**val_user.model_dump())

    except HTTPException:
        # Re-raise intentional HTTP errors
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}",
        )


async def update_user(
    session: Annotated[AsyncSession, Depends(get_session)],
    user: UserUpdate,
    username: Annotated[str, Depends(get_username)],
) -> UserPublic:
    try:
        existing_user = await get_existing_user(session, username)
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        user_data = user.model_dump(exclude_unset=True)
        existing_user.sqlmodel_update(user_data)
        session.add(existing_user)
        await session.commit()
        await session.refresh(existing_user)

        return UserPublic(**existing_user.model_dump())

    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}",
        )

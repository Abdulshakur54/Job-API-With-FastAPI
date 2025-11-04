from app.models.user_model import Token, UserPublic, UserCreate, UserUpdate
from fastapi import APIRouter, Depends, status
from app.dependencies import user_dependency

router = APIRouter(
    prefix="/users",
    responses={404: {"description": "Not found"}},
)

@router.post(
    "/",
    response_model=UserPublic,
    summary="Register a new user",
    description="""
### 🧾 Register a New User
This endpoint allows a new user to create an account.  
Provide a full name, email, username, and password.
    """,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "User registered successfully"},
        400: {"description": "Bad request — invalid input data"},
        409: {"description": "Conflict — username or email already exists"},
        500: {"description": "Internal server error — registration failed"},
    },
    tags=['public']
)
async def register(
    register_user: UserCreate = Depends(user_dependency.register),
):
    """
    Create a new user account and return the public user information.
    """
    return register_user


@router.post(
    "/login/",
    response_model=Token,
    summary="Login a user and get access token",
    description="""
### 🔐 User Login
Provide your credentials (username and password) to obtain an access token.
    """,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Login successful — access token returned"},
        401: {"description": "Unauthorized — invalid username or password"},
        500: {"description": "Internal server error — authentication failed"},
    },
    tags=['public']
)
async def login(
    token: Token = Depends(user_dependency.login),
):
    """
    Authenticate a user and return an access token.
    """
    return token


@router.get(
    "/",
    response_model=UserPublic,
    summary="Get user details",
    description="""
### 👤 Get User Info
Retrieve the currently authenticated user's public profile information.
    """,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "User details retrieved successfully"},
        401: {"description": "Unauthorized — invalid or expired token"},
        404: {"description": "User not found"},
        500: {"description": "Internal server error"},
    },
    tags=['private']
)
async def get_user(
    get_user: UserPublic = Depends(user_dependency.get_user),
):
    """
    Return the public profile information of the logged-in user.
    """
    return get_user


@router.patch(
    "/",
    response_model=UserPublic,
    summary="Update user profile",
    description="""
### ✏️ Update User Profile
Update your user information.  
You can modify your name, email, or username.
    """,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "User updated successfully"},
        400: {"description": "Bad request — invalid input"},
        401: {"description": "Unauthorized — invalid or expired token"},
        404: {"description": "User not found"},
        500: {"description": "Internal server error — update failed"},
    },
    tags=['private']
)
async def update(
    update_user: UserUpdate = Depends(user_dependency.update_user),
):
    """
    Update the authenticated user's details and return updated user info.
    """
    return update_user

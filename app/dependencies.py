from typing import Annotated
from sqlmodel import Session
from .dependencies.db import get_session
from fastapi import Depends

SessionDep = Annotated[Session, Depends(get_session)]

# controllers as dependencies
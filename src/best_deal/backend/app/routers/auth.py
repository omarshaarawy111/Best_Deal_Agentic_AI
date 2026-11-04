"""
Authentication routes and security helpers for the Best Deal application.

Description:
    This module handles user registration, login, token creation, and
    authentication dependencies for protected routes.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
import os
from starlette import status
from typing import Annotated
from sqlalchemy.orm import Session
from ..models import Users
from ..database import get_db
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import timedelta, datetime, timezone

"""
Configurations
"""
router = APIRouter(
     prefix='/auth',
     tags=['auth']
)
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("EBCRYPRION_SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is not configured")
ALGORITHM = "HS256"
oauth2_bearer = OAuth2PasswordBearer(tokenUrl= "auth/token")
db_dependency = Annotated[Session, Depends(get_db)]
form_dependency = Annotated[OAuth2PasswordRequestForm, Depends()]
token_dependency = Annotated[str, Depends(oauth2_bearer)]

class CreateUserRequest(BaseModel):
    """
    Validate data required to create a user account.
    """
    email: EmailStr
    username: str
    password: str
    preferred_category: list[str] | None = None
    preferred_product: list[str] | None = None
    preferred_country_market: list[str] | None = None

class Token(BaseModel):
      """
      Represent an OAuth2 bearer token response.
      """
      access_token: str
      token_type: str


@router.post("/create-user", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, user_request: CreateUserRequest):
    """
    Create and persist a new user account.

    Args:
        db: Database session.
        user_request: Validated account details.

    Returns:
        A success message after the account is created.
    """
    existing_user = db.query(Users).filter((Users.email == user_request.email) |(Users.username == user_request.username)).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email or username already exists"
        )
    
    new_user = Users(
        email=user_request.email,
        username=user_request.username,
        hashed_password=bcrypt_context.hash(user_request.password),
        preferred_category=user_request.preferred_category,
        preferred_product=user_request.preferred_product,
        preferred_country_market=user_request.preferred_country_market  
    )
    db.add(new_user)
    db.commit()
    return {"message": "User created successfully", "user_id": new_user.id}

def authenticate_user(username: str, password: str, db):
      """
      Authenticate a user with a username and password.

      Args:
          username: Account username.
          password: Plain-text password to verify.
          db: Database session.

      Returns:
          The matching user or False when authentication fails.
      """
      user = db.query(Users).filter(Users.username == username).first()
      if not user:
            return False
      if not bcrypt_context.verify(password, user.hashed_password):
            return False

      return user

def create_access_token(username: str, user_id:int, expires_delta: timedelta):
      """
      Create a signed JWT access token.

      Args:
          username: Authenticated account username.
          user_id: Authenticated account identifier.
          expires_delta: Token lifetime.

      Returns:
          An encoded JWT string.
      """
      encode = {
            "sub": username,
            "id": user_id,
            "exp": datetime.now(timezone.utc) + expires_delta
      }
      return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/token", status_code=status.HTTP_200_OK, response_model=Token)
async def login_for_access_token(form_data: form_dependency, db: db_dependency):
      """
      Authenticate a user and issue an access token.

      Args:
          form_data: OAuth2 username and password form.
          db: Database session.

      Returns:
          A bearer token response.
      """
      user = authenticate_user(form_data.username, form_data.password, db)
      if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect username or password')
      token = create_access_token(user.username, user.id, timedelta(minutes=30))
      return {"access_token": token, "token_type": "bearer"}

async def get_current_user(token: token_dependency):
      """
      Decode an access token and return its user claims.

      Args:
          token: Bearer token supplied by the request.

      Returns:
          User identity claims extracted from the token.

      Raises:
          HTTPException: If the token is invalid or incomplete.
      """
      try:
          payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
          username: str = payload.get("sub")
          user_id: int = payload.get("id")

          if username is None or user_id is None:
               raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token payload')
          return {'username': username, 'id': user_id}

      except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token')
from datetime import timedelta
import logging
from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.utils.auth import ACCESS_TOKEN_EXPIRE_MINUTES, authenticate_user, create_access_token, get_current_user, pwd_context
from backend.utils.db import User, get_db

router = APIRouter()

# initialize logger
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
log = logging.getLogger(__name__)


# see current user from username/password input
@router.get("/users/me")
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

# register and receive token
@router.post("/register")
def register(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(form_data.password)
    user = User(username=form_data.username, password=hashed_password)
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        log.error(f"Username {form_data.username} already registered")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Username already registered")
    db.refresh(user)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# generate token from user/pass
@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not pwd_context.verify(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post('/register/github')
async def register_github_user(user_data: dict, db: Session = Depends(get_db)):
    # Extract the necessary data from the user_data dictionary
    username = user_data.get('username')
    email = user_data.get('email')
    github_id = user_data.get('github_id')

    # Check if the user already exists in the database
    existing_user = db.query(User).filter(
        (User.username == username) | (User.email == email) | (User.github_id == github_id)
    ).first()

    if existing_user:
        # User already exists, handle accordingly
        return {'message': 'User already exists'}

    # Create a new user instance
    new_user = User(username=username, email=email, github_id=github_id)

    # Add the new user to the database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {'message': 'User registered successfully'}

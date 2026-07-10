from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database import engine, get_db, Base
import models
import schemas
import auth

# Creates auth.db and the tables the first time this file runs
Base.metadata.create_all(bind=engine)

app = FastAPI(title="FastAPI Authentication Demo")


@app.get("/")
def root():
    return {"message": "Auth API is running. Visit /docs to try it out."}


# ---------------------------------------------------------------------------
# 1. REGISTER
# ---------------------------------------------------------------------------
@app.post("/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(
        (models.User.username == user.username) | (models.User.email == user.email)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered",
        )

    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=auth.hash_password(user.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# ---------------------------------------------------------------------------
# 2. LOGIN
# OAuth2PasswordRequestForm expects form-data with fields: username, password
# This is what lets Postman/Swagger send it as x-www-form-urlencoded.
# ---------------------------------------------------------------------------
@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()

    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# 3. LOGOUT
# ---------------------------------------------------------------------------
@app.post("/logout", response_model=schemas.MessageResponse)
def logout(
    token: str = Depends(auth.oauth2_scheme),
    current_user: dict = Depends(auth.get_current_user), # Note: changing model type reference to dict matches auth.py layout
    db: Session = Depends(get_db),
):
    already_blacklisted = db.query(models.BlacklistedToken).filter(
        models.BlacklistedToken.token == token
    ).first()
    if not already_blacklisted:
        db.add(models.BlacklistedToken(token=token))
        db.commit()

    # FIX: Change current_user.username to current_user["username"]
    return {"message": f"User '{current_user['username']}' logged out successfully"}
@app.get("/me")
def read_users_me(current_user: dict = Depends(auth.get_current_user)):
    # Returns the logged-in user profile dictionary directly
    return current_user
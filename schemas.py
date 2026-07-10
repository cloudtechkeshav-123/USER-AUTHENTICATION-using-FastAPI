from pydantic import BaseModel, Field

# Schema used when a new user registers
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=6)

# Schema used when returning user data (hides the password!)
class UserOut(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True  # Allows Pydantic to read SQLAlchemy models directly

# Schema for the Login Request
class UserLogin(BaseModel):
    username: str
    password: str

# Schema for returning JWT Tokens
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Schema for simple message responses (like logout)
class MessageResponse(BaseModel):
    message: str
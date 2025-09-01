from fastapi import APIRouter, Depends, status
from models import User
from db import get_db
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional


router =  APIRouter(prefix="/users", tags=["users"], responses={404: {"description": "Not found"}})



'''
POST /users
Request Body:
{
  "username": "string",
  "email": "string",
  "password": "string",
  "phone_number": "string"
}
Response: 201 Created

'''



class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    phone_number: str


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    user = User(**user_data.dict())
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "User created successfully", "user_id": user.id}


'''
GET /users/{user_id}
Response: 200 OK
{
  "user_id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "phone_number": "+1234567890",
  "balance": 150.50,
  "created_at": "2024-01-01T00:00:00Z"
}
'''

@router.get("/{user_id}", status_code = status.HTTP_200_OK)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"error": "User not found"}
    return {
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "phone_number": user.phone_number,
        "balance": user.balance,
        "created_at": user.created_at,
    }, 



'''
PUT /users/{user_id}
Request Body:
{
  "username": "string",
  "phone_number": "string"
}
Response: 200 OK

'''

class UserUpdate(BaseModel):
    username: Optional[str]
    phone_number: Optional[str]


@router.put("/{user_id}", status_code=status.HTTP_200_OK)
def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"error": "User not found"}
    if user_data.username:
        user.username = user_data.username
    if user_data.phone_number:
        user.phone_number = user_data.phone_number
    db.commit()
    db.refresh(user)
    return {"message": "User updated successfully"}



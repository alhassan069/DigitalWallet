from fastapi import APIRouter, Depends, status
from models import User, Transaction
from db import get_db
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal


router =  APIRouter(prefix="/wallet", tags=["wallet"], responses={404: {"description": "Not found"}})



'''
GET /wallet/{user_id}/balance
Response: 200 OK
{
  "user_id": 1,
  "balance": 150.50,
  "last_updated": "2024-01-01T12:30:00Z"
}

'''

class WalletBalanceResponse(BaseModel):
    user_id: int
    balance: float
    last_updated: datetime

# Error pydantic_core._pydantic_core.ValidationError: 1 validation error for WalletBalanceResponse
# last_updated
#   Input should be a valid string [type=string_type, input_value=datetime.datetime(2025, 9, 1, 12, 27, 49), input_type=datetime]
#     For further information visit https://errors.pydantic.dev/2.11/v/string_type
#

@router.get("/{user_id}/balance", response_model=WalletBalanceResponse, status_code=status.HTTP_200_OK)
def get_wallet_balance(user_id: int, db: Session = Depends(get_db)):
    # Logic to retrieve wallet balance
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"error": "User not found"}
    return WalletBalanceResponse(
        user_id=user_id,
        balance=user.balance,
        last_updated=user.updated_at
    )


'''
POST /wallet/{user_id}/add-money
Request Body:
{
  "amount": 100.00,
  "description": "Added money to wallet"
}
Response: 201 Created
{
  "transaction_id": 123,
  "user_id": 1,
  "amount": 100.00,
  "new_balance": 250.50,
  "transaction_type": "CREDIT"
}

'''


class AddMoneyRequest(BaseModel):
    amount: Decimal
    description: Optional[str] = None

@router.post("/{user_id}/add-money", status_code=status.HTTP_201_CREATED)
def add_money_to_wallet(user_id: int, add_money_request: AddMoneyRequest, db: Session = Depends(get_db)):

    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"error": "User not found"}
        user.balance = user.balance + add_money_request.amount

        new_transaction = Transaction(
            user_id=user.id,
            amount=add_money_request.amount,
            description=add_money_request.description,
            transaction_type="CREDIT"
        )
        db.add(new_transaction)
        db.commit()
        db.refresh(user)
        return {
            "transaction_id": new_transaction.id,
            "user_id": user.id,
            "amount": add_money_request.amount,
            "new_balance": user.balance,
            "transaction_type": "CREDIT"
        }
    except Exception as e:
        db.rollback()
        return {"error": str(e)}


'''
POST /wallet/{user_id}/withdraw
Request Body:
{
  "amount": 50.00,
  "description": "Withdrew money from wallet"
}
Response: 201 Created / 400 Bad Request (insufficient balance)

'''

class WithdrawRequest(BaseModel):
    amount: Decimal
    description: Optional[str] = None

@router.post("/{user_id}/withdraw", status_code=status.HTTP_201_CREATED)
def withdraw_money_from_wallet(user_id: int, withdraw_request: WithdrawRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"error": "User not found"}
    if user.balance < withdraw_request.amount:
        return {"error": "Insufficient balance"}
    user.balance = user.balance - withdraw_request.amount

    new_transaction = Transaction(
        user_id=user.id,
        amount=withdraw_request.amount,
        description=withdraw_request.description,
        transaction_type="DEBIT"
    )
    db.add(new_transaction)
    db.commit()
    db.refresh(user)
    return {
        "transaction_id": new_transaction.id,
        "user_id": user.id,
        "amount": withdraw_request.amount,
        "new_balance": user.balance,
        "transaction_type": "DEBIT"
    }

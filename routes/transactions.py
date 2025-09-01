from fastapi import APIRouter, Depends, status
from models import User, Transaction
from db import get_db
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal


router =  APIRouter(prefix="/transactions", tags=["transactions"], responses={404: {"description": "Not found"}})



'''
GET /transactions/{user_id}?page=1&limit=10
Response: 200 OK
{
  "transactions": [
    {
      "transaction_id": 123,
      "transaction_type": "CREDIT",
      "amount": 100.00,
      "description": "Added money",
      "created_at": "2024-01-01T12:30:00Z"
    }
  ],
  "total": 50,
  "page": 1,
  "limit": 10
}

'''
@router.get("/{user_id}", status_code=status.HTTP_200_OK)
def get_user_transactions(user_id: int, page: int, limit: int, db: Session = Depends(get_db)):

    transactions = db.query(Transaction).filter(Transaction.user_id == user_id).offset((page - 1) * limit).limit(limit).all()
    total = db.query(Transaction).filter(Transaction.user_id == user_id).count()
    return {
        "user_id": user_id,
        "transactions": transactions,
        "total": total,
        "page": page,
        "limit": limit
    }

'''
GET /transactions/detail/{transaction_id}
Response: 200 OK
{
  "transaction_id": 123,
  "user_id": 1,
  "transaction_type": "TRANSFER_OUT",
  "amount": 25.00,
  "description": "Transfer to jane_doe",
  "recipient_user_id": 2,
  "reference_transaction_id": 124,
  "created_at": "2024-01-01T12:30:00Z"
}

'''

@router.get("/detail/{transaction_id}", status_code=status.HTTP_200_OK)
def get_transaction_detail(transaction_id: int, db: Session = Depends(get_db)):
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        return {"error": "Transaction not found"}
    return {
        "transaction_id": transaction.id,
        "user_id": transaction.user_id,
        "transaction_type": transaction.transaction_type,
        "amount": transaction.amount,
        "description": transaction.description,
        "recipient_user_id": transaction.recipient_user_id,
        "reference_transaction_id": transaction.reference_transaction_id,
        "created_at": transaction.created_at
    }

from fastapi import APIRouter, Depends, status
from models import User, Transaction
from db import get_db
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal


router =  APIRouter(prefix="/transfer", tags=["transfer"], responses={404: {"description": "Not found"}})


'''
POST /transfer
Request Body:
{
  "sender_user_id": 1,
  "recipient_user_id": 2,
  "amount": 25.00,
  "description": "Payment for dinner"
}
Response: 201 Created
{
  "transfer_id": "unique_transfer_id",
  "sender_transaction_id": 123,
  "recipient_transaction_id": 124,
  "amount": 25.00,
  "sender_new_balance": 125.50,
  "recipient_new_balance": 75.00,
  "status": "completed"
}

Response: 400 Bad Request
{
  "error": "Insufficient balance",
  "current_balance": 10.00,
  "required_amount": 25.00
}

'''

class TransferCreate(BaseModel):
    sender_user_id: int
    recipient_user_id: int
    amount: Decimal
    description: Optional[str] = None

class TransferResponse(BaseModel):
    transfer_id: int
    sender_transaction_id: int
    recipient_transaction_id: int
    amount: Decimal
    sender_new_balance: Decimal
    recipient_new_balance: Decimal
    status: str

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_transfer(transfer: TransferCreate, db: Session = Depends(get_db)):
    # Logic to create a transfer

    try:
        sender = db.query(User).filter(User.id == transfer.sender_user_id).first()
        recipient = db.query(User).filter(User.id == transfer.recipient_user_id).first()

        if not sender or not recipient:
            return {"error": "User not found"}

        if sender.balance < transfer.amount:
            return {
                "error": "Insufficient balance",
                "current_balance": sender.balance,
                "required_amount": transfer.amount
            }

        # Simulate successful transfer
        sender.balance -= transfer.amount
        recipient.balance += transfer.amount

        sender_transaction = Transaction(
            user_id=transfer.sender_user_id,
            transaction_type="TRANSFER_OUT",
            amount=transfer.amount,
            description=transfer.description,
            recipient_user_id=transfer.recipient_user_id,
            
        )

        recipient_transaction = Transaction(
            user_id=transfer.recipient_user_id,
            recipient_user_id=transfer.recipient_user_id,
            amount=transfer.amount,
            description=transfer.description,
            transaction_type="TRANSFER_IN",
            
        )

        db.add(sender_transaction)
        db.add(recipient_transaction)

        sender_transaction.reference_transaction_id = recipient_transaction.id
        recipient_transaction.reference_transaction_id = sender_transaction.id
        db.commit()

        return TransferResponse(
            transfer_id=sender_transaction.id,
            sender_transaction_id=sender_transaction.id,
            recipient_transaction_id=recipient_transaction.id,
            amount=transfer.amount,
            sender_new_balance=sender.balance,
            recipient_new_balance=recipient.balance,
            status="completed"
        )

    except Exception as e:
        # Handle exceptions (e.g., insufficient funds)
        return {"error": str(e)}



'''
GET /transfer/{transfer_id}
Response: 200 OK
{
  "transfer_id": "unique_transfer_id",
  "sender_user_id": 1,
  "recipient_user_id": 2,
  "amount": 25.00,
  "description": "Payment for dinner",
  "status": "completed",
  "created_at": "2024-01-01T12:30:00Z"
}

'''

@router.get("/{transfer_id}", status_code=status.HTTP_200_OK)
def get_transfer(transfer_id: str, db: Session = Depends(get_db)):
    transfer = db.query(Transaction).filter(Transaction.id == transfer_id).first()
    if not transfer:
        return {"error": "Transfer not found"}

    return {
        "transfer_id": transfer.id,
        "sender_user_id": transfer.sender_id,
        "recipient_user_id": transfer.recipient_id,
        "amount": transfer.amount,
        "description": transfer.description,
        "status": transfer.status,
        "created_at": transfer.created_at
    }
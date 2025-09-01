'''
-- Users Table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    phone_number VARCHAR(15),
    balance DECIMAL(10,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Transactions Table
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    transaction_type VARCHAR(20) NOT NULL, -- 'CREDIT', 'DEBIT', 'TRANSFER_IN', 'TRANSFER_OUT'
    amount DECIMAL(10,2) NOT NULL,
    description TEXT,
    reference_transaction_id INTEGER REFERENCES transactions(id), -- For linking transfer transactions
    recipient_user_id INTEGER REFERENCES users(id), -- For transfers
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
'''

from sqlalchemy import Column, Integer, String, Numeric, Text, ForeignKey, TIMESTAMP, DateTime
from sqlalchemy.orm import relationship
from db import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(15))
    balance: Mapped[float] = mapped_column(Numeric(10, 2), default=0.00)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    transactions: Mapped[list["Transaction"]] = relationship("Transaction", back_populates="user")

class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    transaction_type: Mapped[str] = mapped_column(String(20), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    description: Mapped[str] = mapped_column(Text)
    reference_transaction_id: Mapped[int] = mapped_column(Integer, ForeignKey("transactions.id"), nullable=True)
    recipient_user_id: Mapped[int] = mapped_column(Integer, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())

    user: Mapped["User"] = relationship("User", back_populates="transactions")
    reference_transaction: Mapped["Transaction"] = relationship("Transaction", remote_side=[id])
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, Enum, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import enum

class BaseTransactionType(str, enum.Enum):
    bet = "bet"
    win = "win"

class TransactionType(str, enum.Enum):
    init = "init"
    bet = "bet"
    win = "win"

Base = declarative_base()

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    value = Column(Integer, nullable=False)
    type = Column(Enum(TransactionType), nullable=False)

DATABASE_URL = "sqlite:///./transactions.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TransactionCreate(BaseModel):
    amount: int
    transaction_type: BaseTransactionType

def add_transaction(amount: int, transaction_type: TransactionType):
    with SessionLocal() as db:
        new_transaction = Transaction(value=amount, type=transaction_type)
        db.add(new_transaction)
        db.commit()
        return new_transaction

@app.post("/transactions/")
async def create_transaction(transaction: TransactionCreate):
    try:
        result = add_transaction(transaction.amount, transaction.transaction_type)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/balance/")
async def get_balance():
    with SessionLocal() as db:
        balance = sum(t.value for t in db.query(Transaction).all())
        return {"balance": balance}

if __name__ == "__main__":
    if not SessionLocal().query(Transaction).filter_by(type=TransactionType.init).first():
        add_transaction(100, TransactionType.init)

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
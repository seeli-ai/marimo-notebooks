
from typing import Optional
from datetime import date

from sqlmodel import Field, SQLModel


# Define your models
class Trade(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    symbol: str
    trade_date: date
    trade_type: int  # 1 = Long or -1 = Short
    last_close: Optional[float]
    atr30:  Optional[float]
    quantity:  Optional[int]
    open: Optional[float]
    close: Optional[float]
    profit: Optional[float]
    gap_in_atr: Optional[float]
    limit_touched: Optional[bool]
    limit: Optional[float]
    notes: Optional[str] = None
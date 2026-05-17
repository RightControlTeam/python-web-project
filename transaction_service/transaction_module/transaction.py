from sqlalchemy import Column, Integer, Boolean
from transaction_service.core.database import Base

class Transaction(Base):
    __tablename__ = 'transaction'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, nullable=False, index=True)
    user_id = Column(Integer, nullable=False)
    is_success = Column(Boolean, nullable=False, default=False)
    cost = Column(Integer, nullable=False)

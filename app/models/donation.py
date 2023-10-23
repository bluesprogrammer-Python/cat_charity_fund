from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy.sql import false

from app.core.db import Base


class Donation(Base):
    user_id = Column(Integer, ForeignKey('user.id'))
    comment = Column(Text)
    full_amount = Column(Integer, nullable=False)
    invested_amount = Column(Integer, default=0)
    fully_invested = Column(Boolean, default=false())
    create_date = Column(DateTime, default=datetime.now)
    close_date = Column(DateTime)

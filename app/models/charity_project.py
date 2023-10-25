from datetime import datetime

from sqlalchemy import (Boolean, CheckConstraint, Column, DateTime, Integer,
                        String, Text)
from sqlalchemy.sql import false

from app.core.db import Base


class CharityProject(Base):
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=False)
    full_amount = Column(Integer, nullable=False)
    invested_amount = Column(Integer, CheckConstraint("invested_amount >= 0"),
                             default=0)
    fully_invested = Column(Boolean, default=false())
    create_date = Column(DateTime, default=datetime.now)
    close_date = Column(DateTime)

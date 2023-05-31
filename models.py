from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, index=False)
    description = Column(String, index=False)
    aditional = Column(String, index=False)
    config = Column(String, index=False)
    campus = Column(String, index=True)
    tab = Column(String, index=False)
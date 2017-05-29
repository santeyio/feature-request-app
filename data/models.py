import uuid

from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import relationship
from sqlalchemy_utils import UUIDType
from data.db import Base


class Feature(Base):

    __tablename__ = 'feature'

    id = Column(UUIDType, primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    client = Column(String, nullable=False)
    client_priority = Column(Integer, nullable=False)
    target_date = Column(Date, nullable=False)
    product_area = Column(String, nullable=False)

import uuid
from typing import List

from sqlalchemy import TEXT, Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from models.base import Base


class User(Base):
    __tablename__ = "user"
    # as_uuid = Trueが必要
    # https://stackoverflow.com/questions/47429929/attributeerror-uuid-object-has-no-attribute-replace-when-using-backend-agno
    id: uuid.UUID = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )  # dialectには型アノテーションが必要
    name = Column(String)

    posts: List["Post"] = relationship(
        "Post", back_populates="user"
    )  # relationにも型アノテーションが必要


class Post(Base):
    __tablename__ = "blog"
    id: uuid.UUID = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )  # dialectには型アノテーションが必要
    title = Column(String)
    text = Column(TEXT)

    user_id: uuid.UUID = Column(
        UUID(as_uuid=True), ForeignKey("user.id")
    )  # dialectには型アノテーションが必要
    user: "User" = relationship("User", back_populates="posts")  # relationにも型アノテーションが必要

from typing import List
from typing import Optional
from datetime import date, datetime
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    
    username: Mapped[str] = mapped_column(String(10), primary_key=True)
    # later add nullable=False to password_hash, but now ok for testing
    password_hash: Mapped[str] = mapped_column(String(255))
    avatar: Mapped[Optional[str]]
    fullname: Mapped[Optional[str]] = mapped_column(String(80))
    birthday: Mapped[Optional[date]]
    location: Mapped[Optional[str]] = mapped_column(String(80))
    something_fun: Mapped[Optional[str]] = mapped_column(String(250))
    posts: Mapped[List["Post"]] = relationship(back_populates="author")


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    author_username: Mapped[str] = mapped_column(ForeignKey("users.username"), nullable=False)
    content: Mapped[str] = mapped_column(String(5000), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    author: Mapped[User] = relationship(back_populates="posts")

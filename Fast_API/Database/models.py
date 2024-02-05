from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Role(Base):
    __tablename__ = "role"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now(), nullable=False)
    users = relationship("User", backref="role", lazy=True)


class Like(Base):
    __tablename__ = "like"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    note_id = Column(Integer, ForeignKey("note.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now())


class Note(Base):
    __tablename__ = "note"

    id = Column(Integer, primary_key=True)
    data = Column(String(10000))
    date = Column(DateTime(timezone=True), default=datetime.now())
    user_id = Column(Integer, ForeignKey("user.id"))
    likes = relationship(
        "Like", backref="note", lazy=True, cascade="all, delete-orphan"
    )


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(150))
    last_name = Column(String(150))
    email = Column(String(150), unique=True)
    password = Column(String(150))
    is_active = Column(Boolean, default=True)
    last_password_change = Column(DateTime, default=datetime.now)
    role_id = Column(Integer, ForeignKey("role.id"), nullable=False)
    notes = relationship(
        "Note", backref="user", lazy=True, cascade="all, delete-orphan"
    )
    likes = relationship(
        "Like", backref="user", lazy=True, cascade="all, delete-orphan"
    )

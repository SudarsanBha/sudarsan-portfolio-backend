from sqlalchemy import JSON, Integer, String, Text
from sqlalchemy.orm import mapped_column, Mapped
from app.database import Base

class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    technologies: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
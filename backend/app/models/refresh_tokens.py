from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    token_hash: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
    )

    jti: Mapped[str] = mapped_column(
        String(36),
        index=True,
        unique=True,
        nullable=False,
    )

    family_id: Mapped[str] = mapped_column(
            String(36),
            index=True,
            nullable=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
            DateTime(timezone=True),
            nullable=False,
    )

    revoked_at: Mapped[datetime] = mapped_column(
            DateTime(timezone=True),
            nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
            DateTime(timezone=True),
            default=lambda:
                datetime.now(timezone.utc),
            nullable=False,
    )
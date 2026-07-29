from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from opspilot.db.base import Base
from opspilot.domain.tickets import Priority, ServiceType, TicketStatus


def utc_now() -> datetime:
    return datetime.now(UTC)


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    role: Mapped[str] = mapped_column(String(32), nullable=False)
    team_id: Mapped[str | None] = mapped_column(String(64))

    tickets: Mapped[list["Ticket"]] = relationship(back_populates="requester")


class Ticket(Base):
    __tablename__ = "tickets"
    __table_args__ = (
        UniqueConstraint("requester_id", "client_request_id", name="uq_ticket_requester_client_request"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    requester_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)
    subject: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    service_catalog_type: Mapped[ServiceType] = mapped_column(
        Enum(ServiceType, values_callable=lambda enum_type: [item.value for item in enum_type]),
        nullable=False,
    )
    reported_priority: Mapped[Priority] = mapped_column(
        Enum(Priority, values_callable=lambda enum_type: [item.value for item in enum_type]),
        nullable=False,
    )
    channel: Mapped[str] = mapped_column(String(32), nullable=False)
    owning_team: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    sla_hours: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[TicketStatus] = mapped_column(
        Enum(TicketStatus, values_callable=lambda enum_type: [item.value for item in enum_type]),
        default=TicketStatus.OPEN,
        nullable=False,
    )
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    client_request_id: Mapped[str | None] = mapped_column(String(128))

    requester: Mapped[User] = relationship(back_populates="tickets")

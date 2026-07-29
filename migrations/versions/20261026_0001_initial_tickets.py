"""Create seeded identities and service tickets.

Revision ID: 20261026_0001
Revises:
Create Date: 2026-10-26
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20261026_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("display_name", sa.String(length=120), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("team_id", sa.String(length=64), nullable=True),
    )
    op.create_table(
        "tickets",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("requester_id", sa.String(length=64), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("subject", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("service_catalog_type", sa.Enum("account_access", "software_request", "purchase_request",
                    "data_reporting", "policy_question", name="servicetype"), nullable=False),
        sa.Column("reported_priority", sa.Enum("low", "normal", "high", name="priority"), nullable=False),
        sa.Column("channel", sa.String(length=32), nullable=False),
        sa.Column("owning_team", sa.String(length=64), nullable=False),
        sa.Column("sla_hours", sa.Integer(), nullable=False),
        sa.Column("status", sa.Enum("open", name="ticketstatus"), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("client_request_id", sa.String(length=128), nullable=True),
        sa.UniqueConstraint("requester_id", "client_request_id", name="uq_ticket_requester_client_request"),
    )
    op.create_index("ix_tickets_requester_id", "tickets", ["requester_id"])
    op.create_index("ix_tickets_created_at", "tickets", ["created_at"])
    op.create_index("ix_tickets_owning_team", "tickets", ["owning_team"])


def downgrade() -> None:
    op.drop_index("ix_tickets_owning_team", table_name="tickets")
    op.drop_index("ix_tickets_created_at", table_name="tickets")
    op.drop_index("ix_tickets_requester_id", table_name="tickets")
    op.drop_table("tickets")
    op.drop_table("users")

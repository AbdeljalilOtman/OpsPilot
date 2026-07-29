from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from opspilot.api.auth import Principal, get_current_principal
from opspilot.api.schemas import TicketCreate, TicketRead
from opspilot.db.models import Ticket
from opspilot.db.session import get_db
from opspilot.domain.tickets import SERVICE_RULES

router = APIRouter(prefix="/v1")
DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[Principal, Depends(get_current_principal)]


@router.post("/tickets", response_model=TicketRead, status_code=status.HTTP_201_CREATED)
def create_ticket(payload: TicketCreate, db: DbSession, actor: CurrentUser) -> Ticket:
    team, sla_hours = SERVICE_RULES[payload.service_catalog_type]
    ticket = Ticket(
        requester_id=actor.id,
        subject=payload.subject,
        description=payload.description,
        service_catalog_type=payload.service_catalog_type,
        reported_priority=payload.reported_priority,
        channel=payload.channel,
        owning_team=team,
        sla_hours=sla_hours,
        client_request_id=payload.client_request_id,
    )
    db.add(ticket)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        if payload.client_request_id:
            existing = db.scalar(
                select(Ticket).where(
                    Ticket.requester_id == actor.id,
                    Ticket.client_request_id == payload.client_request_id,
                )
            )
            if existing is not None:
                same_request = (
                    existing.subject == payload.subject
                    and existing.description == payload.description
                    and existing.service_catalog_type == payload.service_catalog_type
                    and existing.reported_priority == payload.reported_priority
                    and existing.channel == payload.channel
                )
                if same_request:
                    return existing
        raise HTTPException(status_code=409, detail="Ticket could not be created") from None
    db.refresh(ticket)
    return ticket


@router.get("/tickets/{ticket_id}", response_model=TicketRead)
def get_ticket(ticket_id: str, db: DbSession, actor: CurrentUser) -> Ticket:
    ticket = db.get(Ticket, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    if actor.role == "employee" and ticket.requester_id != actor.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    if actor.role == "analyst" and ticket.owning_team != actor.team_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    if actor.role not in {"employee", "analyst"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Role cannot read tickets")
    return ticket

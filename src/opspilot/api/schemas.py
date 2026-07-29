from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from opspilot.domain.tickets import Priority, ServiceType, TicketStatus


class TicketCreate(BaseModel):
    subject: str = Field(min_length=3, max_length=160)
    description: str = Field(min_length=5, max_length=10_000)
    service_catalog_type: ServiceType
    reported_priority: Priority = Priority.NORMAL
    channel: str = Field(default="portal", min_length=1, max_length=32)
    client_request_id: str | None = Field(default=None, min_length=1, max_length=128)


class TicketRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    requester_id: str
    created_at: datetime
    subject: str
    description: str
    service_catalog_type: ServiceType
    reported_priority: Priority
    channel: str
    owning_team: str
    sla_hours: int
    status: TicketStatus
    version: int


class DevTokenRequest(BaseModel):
    user_id: str


class DevTokenRead(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

from enum import StrEnum


class ServiceType(StrEnum):
    ACCOUNT_ACCESS = "account_access"
    SOFTWARE_REQUEST = "software_request"
    PURCHASE_REQUEST = "purchase_request"
    DATA_REPORTING = "data_reporting"
    POLICY_QUESTION = "policy_question"


class Priority(StrEnum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


class TicketStatus(StrEnum):
    OPEN = "open"


SERVICE_RULES: dict[ServiceType, tuple[str, int]] = {
    ServiceType.ACCOUNT_ACCESS: ("identity_support", 24),
    ServiceType.SOFTWARE_REQUEST: ("workplace_apps", 72),
    ServiceType.PURCHASE_REQUEST: ("procurement_ops", 120),
    ServiceType.DATA_REPORTING: ("analytics_support", 48),
    ServiceType.POLICY_QUESTION: ("service_desk", 24),
}

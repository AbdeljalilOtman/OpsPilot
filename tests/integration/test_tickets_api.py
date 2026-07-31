def test_employee_can_create_and_read_own_ticket(client, auth_headers):
    created = client.post(
        "/v1/tickets",
        headers=auth_headers("employee-alex"),
        json={
            "subject": "Reporting tool access",
            "description": "I need access for the budget review.",
            "service_catalog_type": "software_request",
            "reported_priority": "normal",
            "channel": "portal",
            "client_request_id": "request-001",
        },
    )

    assert created.status_code == 201
    ticket = created.json()
    assert ticket["requester_id"] == "employee-alex"
    assert ticket["owning_team"] == "workplace_apps"
    assert ticket["sla_hours"] == 72
    assert ticket["status"] == "open"

    read = client.get(f"/v1/tickets/{ticket['id']}", headers=auth_headers("employee-alex"))
    assert read.status_code == 200
    assert read.json()["id"] == ticket["id"]


def test_employee_cannot_read_another_employees_ticket(client, auth_headers):
    created = client.post(
        "/v1/tickets",
        headers=auth_headers("employee-alex"),
        json={
            "subject": "Policy clarification",
            "description": "Please explain the expense policy.",
            "service_catalog_type": "policy_question",
        },
    )
    ticket_id = created.json()["id"]

    response = client.get(f"/v1/tickets/{ticket_id}", headers=auth_headers("employee-sam"))

    assert response.status_code == 404


def test_requester_identity_cannot_be_overridden_by_payload(client, auth_headers):
    response = client.post(
        "/v1/tickets",
        headers=auth_headers("employee-alex"),
        json={
            "requester_id": "employee-sam",
            "subject": "Policy clarification",
            "description": "Please explain the expense policy.",
            "service_catalog_type": "policy_question",
        },
    )

    assert response.status_code == 201
    assert response.json()["requester_id"] == "employee-alex"


def test_analyst_can_read_ticket_for_their_team(client, auth_headers):
    created = client.post(
        "/v1/tickets",
        headers=auth_headers("employee-alex"),
        json={
            "subject": "Policy clarification",
            "description": "Please explain the expense policy.",
            "service_catalog_type": "policy_question",
        },
    )

    response = client.get(
        f"/v1/tickets/{created.json()['id']}", headers=auth_headers("analyst-jordan")
    )

    assert response.status_code == 200


def test_analyst_cannot_read_ticket_outside_their_team(client, auth_headers):
    created = client.post(
        "/v1/tickets",
        headers=auth_headers("employee-alex"),
        json={
            "subject": "Reporting tool access",
            "description": "I need access for the budget review.",
            "service_catalog_type": "software_request",
        },
    )

    response = client.get(
        f"/v1/tickets/{created.json()['id']}", headers=auth_headers("analyst-jordan")
    )

    assert response.status_code == 404


def test_ticket_creation_requires_authentication(client):
    response = client.post(
        "/v1/tickets",
        json={
            "subject": "Reporting tool access",
            "description": "I need access for the budget review.",
            "service_catalog_type": "software_request",
        },
    )

    assert response.status_code == 401


def test_client_request_id_is_idempotent_for_same_employee(client, auth_headers):
    payload = {
        "subject": "Reporting tool access",
        "description": "I need access for the budget review.",
        "service_catalog_type": "software_request",
        "client_request_id": "retry-safe-1",
    }
    first = client.post("/v1/tickets", headers=auth_headers("employee-alex"), json=payload)
    second = client.post("/v1/tickets", headers=auth_headers("employee-alex"), json=payload)

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["id"] == second.json()["id"]


def test_reusing_client_request_id_with_different_payload_conflicts(client, auth_headers):
    headers = auth_headers("employee-alex")
    first = client.post(
        "/v1/tickets",
        headers=headers,
        json={
            "subject": "Reporting tool access",
            "description": "I need access for the budget review.",
            "service_catalog_type": "software_request",
            "client_request_id": "retry-safe-2",
        },
    )
    second = client.post(
        "/v1/tickets",
        headers=headers,
        json={
            "subject": "Changed request",
            "description": "This is a different payload.",
            "service_catalog_type": "software_request",
            "client_request_id": "retry-safe-2",
        },
    )

    assert first.status_code == 201
    assert second.status_code == 409

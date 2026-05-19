from fastapi.testclient import TestClient


async def test_when_authenticated_post_todos_shall_return_201_with_location(
    client: TestClient,
) -> None:
    response = client.post(
        "/v1/todos",
        json={"title": "Buy milk"},
        headers={"Authorization": "Bearer alice-post"},
    )

    assert response.status_code == 201
    assert response.headers["Location"].startswith("/v1/todos/")


async def test_when_authenticated_get_todos_shall_return_envelope_scoped_to_owner(
    client: TestClient,
) -> None:
    client.post(
        "/v1/todos",
        json={"title": "My list item"},
        headers={"Authorization": "Bearer alice-list"},
    )

    response = client.get("/v1/todos", headers={"Authorization": "Bearer alice-list"})

    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == 1
    assert body["items"][0]["owner_id"] == "alice-list"


async def test_when_authenticated_get_todo_shall_return_200(
    client: TestClient,
) -> None:
    created = client.post(
        "/v1/todos",
        json={"title": "Get me"},
        headers={"Authorization": "Bearer alice-get"},
    )
    todo_id = created.json()["id"]

    response = client.get(
        f"/v1/todos/{todo_id}", headers={"Authorization": "Bearer alice-get"}
    )

    assert response.status_code == 200
    assert response.json()["id"] == todo_id


async def test_when_authenticated_patch_todo_shall_update_fields(
    client: TestClient,
) -> None:
    created = client.post(
        "/v1/todos",
        json={"title": "Patch me"},
        headers={"Authorization": "Bearer alice-patch"},
    )
    todo_id = created.json()["id"]

    response = client.patch(
        f"/v1/todos/{todo_id}",
        json={"completed": True},
        headers={"Authorization": "Bearer alice-patch"},
    )

    assert response.status_code == 200
    assert response.json()["completed"] is True


async def test_when_authenticated_delete_todo_shall_return_204(
    client: TestClient,
) -> None:
    created = client.post(
        "/v1/todos",
        json={"title": "Delete me"},
        headers={"Authorization": "Bearer alice-delete"},
    )
    todo_id = created.json()["id"]

    response = client.delete(
        f"/v1/todos/{todo_id}", headers={"Authorization": "Bearer alice-delete"}
    )

    assert response.status_code == 204


async def test_if_authorization_header_missing_any_todos_route_shall_return_401_problem(
    client: TestClient,
) -> None:
    response = client.get("/v1/todos")

    assert response.status_code == 401
    assert response.headers["content-type"] == "application/problem+json"


async def test_if_todo_belongs_to_other_owner_get_todo_shall_return_404_problem(
    client: TestClient,
) -> None:
    created = client.post(
        "/v1/todos",
        json={"title": "Bob's todo"},
        headers={"Authorization": "Bearer bob-iso"},
    )
    todo_id = created.json()["id"]

    response = client.get(
        f"/v1/todos/{todo_id}", headers={"Authorization": "Bearer alice-iso"}
    )

    assert response.status_code == 404
    assert response.headers["content-type"] == "application/problem+json"


async def test_if_request_body_invalid_post_todos_shall_return_422_problem_with_errors(
    client: TestClient,
) -> None:
    response = client.post(
        "/v1/todos",
        json={},
        headers={"Authorization": "Bearer alice-422"},
    )

    assert response.status_code == 422
    assert response.headers["content-type"] == "application/problem+json"
    assert "errors" in response.json()


async def test_when_paginating_todos_cursor_returns_next_page(
    client: TestClient,
) -> None:
    for i in range(3):
        client.post(
            "/v1/todos",
            json={"title": f"Page item {i}"},
            headers={"Authorization": "Bearer alice-page"},
        )

    first = client.get(
        "/v1/todos?limit=2", headers={"Authorization": "Bearer alice-page"}
    )
    assert first.status_code == 200
    first_body = first.json()
    assert len(first_body["items"]) == 2
    assert first_body["next_cursor"] is not None

    second = client.get(
        f"/v1/todos?limit=2&cursor={first_body['next_cursor']}",
        headers={"Authorization": "Bearer alice-page"},
    )
    assert second.status_code == 200
    second_body = second.json()
    assert len(second_body["items"]) == 1
    assert second_body["next_cursor"] is None


async def test_when_filtering_by_completed_get_todos_shall_return_only_matching(
    client: TestClient,
) -> None:
    created = client.post(
        "/v1/todos",
        json={"title": "Open"},
        headers={"Authorization": "Bearer alice-filter"},
    )
    open_id = created.json()["id"]

    completed_resp = client.post(
        "/v1/todos",
        json={"title": "Done"},
        headers={"Authorization": "Bearer alice-filter"},
    )
    completed_id = completed_resp.json()["id"]
    client.patch(
        f"/v1/todos/{completed_id}",
        json={"completed": True},
        headers={"Authorization": "Bearer alice-filter"},
    )

    response = client.get(
        "/v1/todos?completed=true", headers={"Authorization": "Bearer alice-filter"}
    )

    assert response.status_code == 200
    items = response.json()["items"]
    ids = [item["id"] for item in items]
    assert completed_id in ids
    assert open_id not in ids

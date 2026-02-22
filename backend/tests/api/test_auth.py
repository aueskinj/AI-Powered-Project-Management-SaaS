def test_register_login_refresh_logout_flow(client) -> None:
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "member@example.com",
            "password": "StrongPass123",
            "full_name": "Member User",
            "role": "member",
        },
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": "member@example.com", "password": "StrongPass123"},
    )
    assert login_response.status_code == 200

    token_payload = login_response.json()
    access_token = token_payload["access_token"]
    refresh_token = token_payload["refresh_token"]

    me_response = client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "member@example.com"

    refresh_response = client.post(
        "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
    )
    assert refresh_response.status_code == 200
    rotated_refresh = refresh_response.json()["refresh_token"]

    old_refresh_response = client.post(
        "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
    )
    assert old_refresh_response.status_code == 401

    logout_response = client.post(
        "/api/v1/auth/logout", json={"refresh_token": rotated_refresh}
    )
    assert logout_response.status_code == 200

    refresh_after_logout = client.post(
        "/api/v1/auth/refresh", json={"refresh_token": rotated_refresh}
    )
    assert refresh_after_logout.status_code == 401


def test_admin_only_route_requires_role(client) -> None:
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "member2@example.com",
            "password": "StrongPass123",
            "full_name": "Member Two",
            "role": "member",
        },
    )
    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": "member2@example.com", "password": "StrongPass123"},
    )
    access_token = login_response.json()["access_token"]

    forbidden_response = client.get(
        "/api/v1/users/admin-only",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert forbidden_response.status_code == 403

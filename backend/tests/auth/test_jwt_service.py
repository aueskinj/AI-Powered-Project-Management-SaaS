from app.auth.jwt_service import create_access_token, create_refresh_token, decode_token


def test_create_access_token_contains_access_type() -> None:
    token = create_access_token(subject="507f1f77bcf86cd799439011", role="member")
    payload = decode_token(token)

    assert payload.sub == "507f1f77bcf86cd799439011"
    assert payload.type == "access"
    assert payload.jti is None
    assert payload.role == "member"


def test_create_refresh_token_contains_jti() -> None:
    token, jti, _ = create_refresh_token(subject="507f1f77bcf86cd799439011", role="admin")
    payload = decode_token(token)

    assert payload.sub == "507f1f77bcf86cd799439011"
    assert payload.type == "refresh"
    assert payload.jti == jti
    assert payload.role == "admin"

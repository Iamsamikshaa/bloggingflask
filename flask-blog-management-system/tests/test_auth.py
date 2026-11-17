from app.models import User


def test_user_registration_success(client, app):
    response = client.post(
        "/auth/register",
        data={
            "full_name": "Grace Hopper",
            "username": "graceh",
            "email": "grace@example.com",
            "password": "SecurePassword2026",
            "confirm_password": "SecurePassword2026",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Your account has been created" in response.data
    user = User.query.filter_by(username="graceh").first()
    assert user is not None
    assert user.email == "grace@example.com"


def test_registration_rejects_duplicate_email_and_username(client, create_user):
    create_user(username="existinguser", email="dup@example.com")

    response = client.post(
        "/auth/register",
        data={
            "full_name": "Duplicate Test",
            "username": "existinguser",
            "email": "dup@example.com",
            "password": "SecurePassword2026",
            "confirm_password": "SecurePassword2026",
        },
    )
    assert response.status_code == 200
    assert b"That username is already taken" in response.data
    assert b"An account with this email already exists" in response.data


def test_login_logout_and_protected_route(client, create_user):
    create_user(full_name="Alan Turing", username="alant", email="alan@example.com", password="EnigmaPassword1")

    # Protected route redirects to login when unauthenticated
    unauth_resp = client.get("/posts/create", follow_redirects=False)
    assert unauth_resp.status_code == 302
    assert "/auth/login" in unauth_resp.location

    # Invalid password returns 401
    bad_resp = client.post(
        "/auth/login",
        data={"identifier": "alan@example.com", "password": "wrong"},
    )
    assert bad_resp.status_code == 401
    assert b"Invalid email/username or password" in bad_resp.data

    # Valid login works and displays logged-in user's name
    login_resp = client.post(
        "/auth/login",
        data={"identifier": "alan@example.com", "password": "EnigmaPassword1"},
        follow_redirects=True,
    )
    assert login_resp.status_code == 200
    assert b"Alan Turing" in login_resp.data

    # Protected page now accessible
    create_page = client.get("/posts/create")
    assert create_page.status_code == 200

    # Logout clears session
    logout_resp = client.post("/auth/logout", follow_redirects=True)
    assert logout_resp.status_code == 200
    assert b"signed out" in logout_resp.data

    after_logout = client.get("/posts/create", follow_redirects=False)
    assert after_logout.status_code == 302

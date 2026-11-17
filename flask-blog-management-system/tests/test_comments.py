from app.models import db, Comment
from tests.conftest import login_client


def test_comment_create_edit_delete_and_authorization(client, create_user, create_post):
    author = create_user(username="postauthor", email="pa@example.com", password="Password123!")
    commenter = create_user(username="commenter", email="cm@example.com", password="Password123!")
    stranger = create_user(username="stranger", email="st@example.com", password="Password123!")
    post = create_post(author=author, title="Discussing Clean Code")

    # Unauthenticated user cannot post comment
    unauth_resp = client.post(
        f"/posts/{post.id}/comments",
        data={"body": "Trying without login"},
        follow_redirects=False,
    )
    assert unauth_resp.status_code == 302
    assert "/auth/login" in unauth_resp.location

    # Commenter logs in and adds comment
    login_client(client, "commenter", "Password123!")
    create_resp = client.post(
        f"/posts/{post.id}/comments",
        data={"body": "Very clear explanation of modular architecture."},
        follow_redirects=True,
    )
    assert create_resp.status_code == 200
    assert b"Comments (1)" in create_resp.data
    assert b"Very clear explanation of modular architecture." in create_resp.data

    comment = Comment.query.filter_by(post_id=post.id).first()
    assert comment is not None

    # Commenter edits own comment
    edit_resp = client.post(
        f"/comments/{comment.id}/edit",
        data={"body": "Updated: Very clear explanation of modular blueprints."},
        follow_redirects=True,
    )
    assert edit_resp.status_code == 200
    assert b"Updated: Very clear explanation of modular blueprints." in edit_resp.data

    # Stranger cannot edit or delete commenter's comment
    client.post("/auth/logout")
    login_client(client, "stranger", "Password123!")
    assert client.post(f"/comments/{comment.id}/edit", data={"body": "Hacked"}).status_code == 403
    assert client.post(f"/comments/{comment.id}/delete").status_code == 403

    # Commenter deletes own comment
    client.post("/auth/logout")
    login_client(client, "commenter", "Password123!")
    del_resp = client.post(f"/comments/{comment.id}/delete", follow_redirects=True)
    assert del_resp.status_code == 200
    assert b"Comments (0)" in del_resp.data
    assert db.session.get(Comment, comment.id) is None

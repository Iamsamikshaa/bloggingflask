import io
from PIL import Image
from app.models import db, Post
from tests.conftest import login_client


def _make_test_image_bytes():
    buf = io.BytesIO()
    img = Image.new("RGB", (120, 90), color=(20, 83, 45))
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


def test_create_read_edit_delete_post_with_image(client, create_user, create_category):
    cat = create_category(name="Architecture", slug="architecture")
    create_user(username="writer1", email="writer1@example.com", password="Password123!")
    login_client(client, "writer1", "Password123!")

    # Create post with tags and featured image
    create_resp = client.post(
        "/posts/create",
        data={
            "title": "Timber Framing in Modern Studios",
            "description": "Exploring exposed joinery and daylight balance in architectural workspaces.",
            "content": "<p>Exposed timber beams bring warmth and structural legibility to studio ceilings.</p>",
            "category_id": cat.id,
            "tags": "Architecture, Timber, Craft",
            "is_published": "y",
            "featured_image": (_make_test_image_bytes(), "studio.png"),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert create_resp.status_code == 200
    assert b"Timber Framing in Modern Studios" in create_resp.data
    assert b"#Architecture" in create_resp.data

    post = Post.query.filter_by(title="Timber Framing in Modern Studios").first()
    assert post is not None
    assert post.featured_image is not None
    assert len(post.tags) == 3

    # Edit post
    edit_resp = client.post(
        f"/posts/{post.id}/edit",
        data={
            "title": "Timber Framing in Modern Studios Revised",
            "description": "Updated summary describing exposed joinery and acoustic comfort.",
            "content": "<p>Updated content discussing acoustic calm and timber framing details.</p>",
            "category_id": cat.id,
            "tags": "Architecture, Joinery",
            "is_published": "y",
        },
        follow_redirects=True,
    )
    assert edit_resp.status_code == 200
    assert b"Timber Framing in Modern Studios Revised" in edit_resp.data
    assert b"#Joinery" in edit_resp.data

    # Delete post
    delete_resp = client.post(f"/posts/{post.id}/delete", follow_redirects=True)
    assert delete_resp.status_code == 200
    assert db.session.get(Post, post.id) is None


def test_post_edit_delete_authorization(client, create_user, create_post):
    owner = create_user(username="owner", email="owner@example.com", password="Password123!")
    other = create_user(username="other", email="other@example.com", password="Password123!")
    post = create_post(author=owner, title="Owner Exclusive Essay")

    login_client(client, "other", "Password123!")

    edit_forbidden = client.get(f"/posts/{post.id}/edit")
    assert edit_forbidden.status_code == 403

    post_edit_forbidden = client.post(
        f"/posts/{post.id}/edit",
        data={
            "title": "Hijacked Title",
            "description": "Hijacked description text.",
            "content": "<p>Unauthorized modification attempt.</p>",
            "category_id": post.category_id,
        },
    )
    assert post_edit_forbidden.status_code == 403

    delete_forbidden = client.post(f"/posts/{post.id}/delete")
    assert delete_forbidden.status_code == 403
    assert db.session.get(Post, post.id) is not None


def test_user_profile_page_displays_author_posts(client, create_user, create_post):
    author = create_user(full_name="Marie Curie", username="mcurie", email="marie@example.com")
    create_post(author=author, title="Notes on Radiochemistry")
    create_post(author=author, title="Secret Draft Essay", is_published=False)

    resp = client.get("/profile/mcurie")
    assert resp.status_code == 200
    assert b"Marie Curie" in resp.data
    assert b"Notes on Radiochemistry" in resp.data
    assert b"Secret Draft Essay" not in resp.data

from app.models import db, Tag


def test_pagination_displays_six_posts_per_page(client, create_user, create_post):
    author = create_user()
    for i in range(1, 9):
        create_post(
            author=author,
            title=f"Paginated Article {i:02d}",
            slug=f"paginated-article-{i:02d}",
        )

    page1 = client.get("/?page=1")
    assert page1.status_code == 200
    assert b"Showing page <strong>1</strong> of <strong>2</strong>" in page1.data
    # Newest 6 (08 down to 03) appear on page 1; 02 and 01 appear on page 2
    assert b"Paginated Article 08" in page1.data
    assert b"Paginated Article 03" in page1.data
    assert b"Paginated Article 02" not in page1.data

    page2 = client.get("/?page=2")
    assert page2.status_code == 200
    assert b"Paginated Article 02" in page2.data
    assert b"Paginated Article 01" in page2.data
    assert b"Paginated Article 08" not in page2.data


def test_search_and_category_and_tag_filtering(client, create_user, create_category, create_post):
    author = create_user()
    eng = create_category(name="Engineering", slug="engineering")
    arch = create_category(name="Architecture", slug="architecture")

    py_tag = Tag(name="Python", slug="python")
    db.session.add(py_tag)
    db.session.commit()

    create_post(
        author=author,
        title="Scaling Flask Services",
        slug="scaling-flask-services",
        content="<p>Deep dive into WSGI workers and database pooling.</p>",
        category=eng,
        tags=[py_tag],
    )
    create_post(
        author=author,
        title="Timber Pavilions in Kyoto",
        slug="timber-pavilions-kyoto",
        content="<p>Joinery details without steel fasteners.</p>",
        category=arch,
    )

    # Search by title
    title_resp = client.get("/?q=Kyoto")
    assert title_resp.status_code == 200
    assert b"Timber Pavilions in Kyoto" in title_resp.data
    assert b"Scaling Flask Services" not in title_resp.data

    # Search by content
    content_resp = client.get("/?q=WSGI+workers")
    assert content_resp.status_code == 200
    assert b"Scaling Flask Services" in content_resp.data
    assert b"Timber Pavilions in Kyoto" not in content_resp.data

    # Filter by category
    cat_resp = client.get("/?category=architecture")
    assert cat_resp.status_code == 200
    assert b"Timber Pavilions in Kyoto" in cat_resp.data
    assert b"Scaling Flask Services" not in cat_resp.data

    # Filter by tag
    tag_resp = client.get("/?tag=python")
    assert tag_resp.status_code == 200
    assert b"Scaling Flask Services" in tag_resp.data
    assert b"Timber Pavilions in Kyoto" not in tag_resp.data

    # Combined search + category filter
    combo_resp = client.get("/?q=WSGI&category=engineering")
    assert combo_resp.status_code == 200
    assert b"Scaling Flask Services" in combo_resp.data

    # No results found message
    empty_resp = client.get("/?q=nonexistentkeywordxyz")
    assert empty_resp.status_code == 200
    assert b"No articles found" in empty_resp.data

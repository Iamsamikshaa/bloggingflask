from app.models import db, Comment, Post, Tag, User


def test_user_password_hashing_and_initials(app, create_user):
    user = create_user(full_name="Ada Lovelace", username="ada", email="ada@example.com", password="SecretPass99")
    assert user.password_hash != "SecretPass99"
    assert user.check_password("SecretPass99") is True
    assert user.check_password("WrongPass") is False
    assert user.initials == "AL"


def test_post_cascade_deletes_comments(app, create_user, create_post):
    author = create_user()
    post = create_post(author=author)
    comment = Comment(body="Great technical breakdown.", user_id=author.id, post_id=post.id)
    db.session.add(comment)
    db.session.commit()

    assert Comment.query.count() == 1
    db.session.delete(post)
    db.session.commit()
    assert Comment.query.count() == 0


def test_post_tags_relationship_and_reading_time(app, create_user, create_post):
    author = create_user()
    tag1 = Tag(name="Python", slug="python")
    tag2 = Tag(name="Flask", slug="flask")
    db.session.add_all([tag1, tag2])
    db.session.commit()

    long_content = "<p>" + ("word " * 420) + "</p>"
    post = create_post(author=author, content=long_content, tags=[tag1, tag2])

    assert len(post.tags) == 2
    assert post.reading_time == 3

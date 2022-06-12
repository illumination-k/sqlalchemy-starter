from typing import Optional

from sqlalchemy.orm import scoped_session

from models.base import QueryCounter
from models.blog import Post, User


def test_user(test_session: scoped_session):
    user = User(name="a")
    test_session.add(user)
    test_session.commit()

    result: Optional[User] = test_session.query(User).filter(User.name == "a").first()
    assert result is not None
    assert user.id == result.id
    assert user.name == result.name


def test_user_post(test_session: scoped_session):
    post1 = Post(title="1", text="1")
    post2 = Post(title="2", text="2")
    posts = [post1, post2]
    user = User(name="a", posts=posts)

    test_session.add(user)
    test_session.commit()

    result: Optional[User] = test_session.query(User).filter(User.name == "a").first()
    assert result is not None
    assert len(user.posts) == len(result.posts)
    assert result.posts[0].id == post1.id
    assert result.posts[1].id == post2.id


def test_counter(test_session: scoped_session):
    with QueryCounter(test_session.connection()) as counter:
        post1 = Post(title="1", text="1")
        post2 = Post(title="2", text="2")
        posts = [post1, post2]
        user = User(name="a", posts=posts)

        test_session.add(user)
        test_session.commit()

        result: Optional[User] = (
            test_session.query(User).filter(User.name == "a").first()
        )

        assert counter.count == 3

        assert result is not None
        assert len(user.posts) == len(result.posts)

        assert counter.count == 4

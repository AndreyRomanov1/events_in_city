from datetime import datetime, timedelta

from db import db_session
from db.post import Post
from db.user import User


def get_users_for_mailing(type_mailing: int) -> list[User]:
    active_session = db_session.create_session()
    users_for_mailing = list(active_session.query(User).filter(User.mailing_frequency == type_mailing).all())
    return users_for_mailing


def get_posts_for_period(start_date_of_period: datetime, period_length_in_days: int):
    start_date_of_period = start_date_of_period.replace(minute=0, hour=0, second=0, microsecond=0)
    end_date_of_period = start_date_of_period + timedelta(days=period_length_in_days)
    active_session = db_session.create_session()
    all_posts = active_session.query(Post).filter(
        Post.datetime_of_event >= start_date_of_period,
        Post.datetime_of_event < end_date_of_period
    ).all()
    all_posts = sorted(all_posts, key=lambda post: post.datetime_of_event)
    return all_posts


def create_dict_of_users_and_their_posts(
        users_for_mailing: list[User],
        all_posts: list[Post]
) -> dict:
    dict_of_users_and_their_posts = {}
    for user in users_for_mailing:
        users_theme_ids = user.get_themes_for_mailing()
        posts_for_user = []
        for post in all_posts:
            if post.theme_id in users_theme_ids:
                posts_for_user.append(post)
        dict_of_users_and_their_posts[user] = posts_for_user
    return dict_of_users_and_their_posts


def daily_message():
    users_for_mailing = get_users_for_mailing(1)
    all_posts = get_posts_for_period(
        start_date_of_period=datetime.now(),
        period_length_in_days=1
    )


def weekly_message():
    users_for_mailing = get_users_for_mailing(2)

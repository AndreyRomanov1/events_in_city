from datetime import datetime

import sqlalchemy

from db import db_session
from db.db_session import SqlAlchemyBase
from sqlalchemy.orm import relationship

from db.favourite import Favourite
from db.theme import Theme
from db.user import User


class Post(SqlAlchemyBase):
    """Посты с мероприятиями"""
    __tablename__ = "post"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String(1000), nullable=False)
    text = sqlalchemy.Column(sqlalchemy.String(100000), nullable=False)
    image = sqlalchemy.Column(sqlalchemy.LargeBinary, nullable=True)
    theme_id = sqlalchemy.Column(sqlalchemy.Integer)
    user_id = sqlalchemy.Column(sqlalchemy.Integer)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.utcnow)
    datetime_of_event = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)
    url = sqlalchemy.Column(sqlalchemy.String(1000), nullable=True)

    def __repr__(self):
        return f"Post_{self.id}_{self.text[:min(len(self.text), 30)]}_{self.datetime_of_event}"

    def get_author_user(self) -> User:
        active_session = db_session.create_session()
        user = active_session.query(User).get(self.user_id)
        return user

    def get_theme(self) -> Theme:
        active_session = db_session.create_session()
        theme = active_session.query(Theme).get(self.theme_id)
        return theme

    def print_post(self) -> str:
        """Формирует сообщение для мессенджера"""
        massage = f"{self.title}\nТема: {self.get_theme().theme_name} Дата: {self.datetime_of_event.strftime('%d.%m.%Y %H:%M')}\n {self.text} \nПодробнее: {self.url}"
        return massage

    def get_count_of_favourites(self):
        """Возвращает количество отметок избранное у поста"""
        active_session = db_session.create_session()
        favourite_users = active_session.query(Favourite).filter(Favourite.post_id == self.id).all()
        return len(favourite_users)

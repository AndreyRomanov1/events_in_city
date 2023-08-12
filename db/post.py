from datetime import datetime

import sqlalchemy

from db import db_session
from db.db_session import SqlAlchemyBase
from sqlalchemy.orm import relationship

from db.user import User


class Post(SqlAlchemyBase):
    """Посты с мероприятиями"""
    __tablename__ = "post"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    text = sqlalchemy.Column(sqlalchemy.String(100000), nullable=False)
    title = sqlalchemy.Column(sqlalchemy.String(100000), nullable=False)
    image = sqlalchemy.Column(sqlalchemy.LargeBinary, nullable=True)
    theme_id = sqlalchemy.Column(sqlalchemy.Integer)
    user_id = sqlalchemy.Column(sqlalchemy.Integer)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.utcnow)
    datetime_of_event = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)
    url = sqlalchemy.Column(sqlalchemy.String(1000), nullable=True)

    def __repr__(self):
        return f"Post_{self.id}_{self.text[:min(len(self.text), 30)]}_{self.date_time_of_event}"

    def get_author_user(self) -> User:
        active_session = db_session.create_session()
        user = active_session.query(User).get(self.user_id)
        return user

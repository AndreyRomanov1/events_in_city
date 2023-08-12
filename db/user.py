import sqlalchemy

from db import db_session
from db.db_session import SqlAlchemyBase
from db.mailing_list import MailingList


class User(SqlAlchemyBase):
    """Пользователи телеграм бота"""
    __tablename__ = "user"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    telegram_id = sqlalchemy.Column(sqlalchemy.Integer, unique=True)
    mailing_frequency = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    is_admin = sqlalchemy.Column(sqlalchemy.BOOLEAN, default=False)

    def __repr__(self):
        return f"User_{self.id}_{self.telegram_id}"

    def get_themes_for_mailing(self) -> list:
        active_session = db_session.create_session()
        users_themes = list(active_session.query(MailingList).filter(
            MailingList.user_id == self.id
        ).all())
        return users_themes


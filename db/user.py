import sqlalchemy

from db import db_session
from db.db_session import SqlAlchemyBase
from db.mailing_list import MailingList


class User(SqlAlchemyBase):
    """Пользователи телеграм бота"""
    __tablename__ = "user"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    telegram_id = sqlalchemy.Column(sqlalchemy.Integer)
    mailing_frequency = sqlalchemy.Column(sqlalchemy.Integer)
    is_admin = sqlalchemy.Column(sqlalchemy.BOOLEAN, default=False)

    def __repr__(self):
        return f"User_{self.id}_{self.telegram_id}"
    #
    # def get_themes_for_mailing(self):
    #     active_session = db_session.create_session()
    #     themes = active_session.query(MailingList).filter(
    #         MailingList.user_id
    #     ).all()

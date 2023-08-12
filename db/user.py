from random import randint

import sqlalchemy

from db import db_session
from db.db_session import SqlAlchemyBase
from db.mailing_list import MailingList


class User(SqlAlchemyBase):
    """Пользователи бота"""
    __tablename__ = "user"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    telegram_id = sqlalchemy.Column(sqlalchemy.Integer, unique=True)
    mailing_frequency = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    admin_level = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    referral_code = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    referral_user = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

    def __repr__(self):
        return f"User_{self.id}_{self.telegram_id}"

    def get_themes_for_mailing(self) -> set:
        """Возвращает множество идентификаторов тем для рассылки этому пользователю"""
        active_session = db_session.create_session()
        users_themes = list(active_session.query(MailingList).filter(
            MailingList.user_id == self.id
        ).all())
        users_themes = set(map(lambda x: x.theme_id, users_themes))
        return users_themes

    def create_referral_code(self, admin_level: int) -> None:
        self.referral_code = f"{self.telegram_id}_{admin_level}_{randint(100000, 999999)}"

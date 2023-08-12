import sqlalchemy
from db.db_session import SqlAlchemyBase
from sqlalchemy.orm import relationship


class MailingList(SqlAlchemyBase):
    """Посты с мероприятиями"""
    __tablename__ = "mailing_list"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    theme_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("theme.id"))
    theme = relationship("theme", back_populates="theme")

    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("user.id"))
    user = relationship("user", back_populates="user")

    def __repr__(self):
        return f"Post_{self.id}_{self.text[:min(len(self.text), 30)]}_{self.date_time_of_event}"
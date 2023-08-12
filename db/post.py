from datetime import datetime

import sqlalchemy
from db.db_session import SqlAlchemyBase
from sqlalchemy.orm import relationship


class Post(SqlAlchemyBase):
    """Посты с мероприятиями"""
    __tablename__ = "post"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    text = sqlalchemy.Column(sqlalchemy.String(100000), nullable=False)
    mailing_frequency = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    image = sqlalchemy.Column(sqlalchemy.LargeBinary, nullable=True)

    theme_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("theme.id"))
    theme = relationship("theme", back_populates="theme")

    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("user.id"))
    user = relationship("user", back_populates="user")

    created_at = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.utcnow)
    datetime_of_event = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)
    url = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    def __repr__(self):
        return f"Post_{self.id}_{self.text[:min(len(self.text), 30)]}_{self.date_time_of_event}"

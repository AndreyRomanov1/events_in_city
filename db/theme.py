import sqlalchemy
from db.db_session import SqlAlchemyBase


class Theme(SqlAlchemyBase):
    """Темы постов"""
    __tablename__ = "theme"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    theme_name = sqlalchemy.Column(sqlalchemy.String(100000), nullable=False)

    def __repr__(self):
        return f"Theme_{self.id}_{self.theme_name}"

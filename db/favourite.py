import sqlalchemy

from db.db_session import SqlAlchemyBase


class Favourite(SqlAlchemyBase):
    """Добавление постов в избранное"""
    __tablename__ = "favourite"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    post_id = sqlalchemy.Column(sqlalchemy.Integer)
    user_id = sqlalchemy.Column(sqlalchemy.Integer)

    def __repr__(self):
        return f"Favourite_{self.id}_{self.post_id}_{self.user_id}"

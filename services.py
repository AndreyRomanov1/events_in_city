from db import db_session
from db.user import User


def get_or_create_user(telegram_id: int) -> User:
    active_session = db_session.create_session()
    user = active_session.query(User).filter_by(telegram_id=telegram_id).first()
    if user:
        return user
    else:
        new_user = User(
            telegram_id=telegram_id,
        )
        active_session.add(new_user)
        active_session.commit()
        return new_user

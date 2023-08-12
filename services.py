from db import db_session
from db.user import User


def get_or_create_user(telegram_id: int) -> User:
    active_session = db_session.create_session()
    user = active_session.query(User).filter(User.telegram_id == telegram_id)
    if user:
        return user.first()
    else:
        new_user = User(
            telegram_id=telegram_id,
        )
        active_session.add(new_user)
        active_session.commit()
        return new_user

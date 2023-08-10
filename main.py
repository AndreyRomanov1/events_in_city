from db import db_session

if __name__ == '__main__':

    db_session.global_init(
        sql_type="sqlite"
    )

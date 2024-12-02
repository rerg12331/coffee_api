from celery_worker import app 
from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.orm import sessionmaker
from config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER


DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
metadata = MetaData()
Session = sessionmaker(bind=engine)

User = Table(
    "user", metadata,
    autoload_with=engine 
)

@app.task
def delete_unverified_users():
    session = Session()

    try:
        stmt = User.select().where(User.c.is_verified == False)
        users_to_delete = session.execute(stmt).fetchall()

        for user in users_to_delete:
            delete_stmt = User.delete().where(User.c.id == user.id)
            session.execute(delete_stmt)

        session.commit()
        print(f"Удалены {len(users_to_delete)} не верифицированные пользователи")

    except Exception as e:
        session.rollback()
        print(f"Ошибка при удалении пользователей: {e}")
    finally:
        session.close()

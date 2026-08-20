"""Creates all tables. Import all models so metadata is registered."""
from app.database.database import Base, engine
from app.models import user, alert, cluster, incident, analysis  # noqa: F401


def init_db():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("Database initialized.")

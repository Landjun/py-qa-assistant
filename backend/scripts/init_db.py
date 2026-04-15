"""Manual initialization script for db + seed data."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from app.core.database import Base, SessionLocal, engine  # noqa: E402
from app.services.seed import seed_data  # noqa: E402


def main() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_data(db)
        print("Database initialized and seed data prepared.")
    finally:
        db.close()


if __name__ == "__main__":
    main()

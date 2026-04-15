"""Reset sqlite database and reseed Phase-1 demo data."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from app.core.database import Base, SessionLocal, engine  # noqa: E402
from app.services.seed import seed_data  # noqa: E402


DB_FILE = ROOT / "crm.db"


def main() -> None:
    if DB_FILE.exists():
        DB_FILE.unlink()
        print(f"Deleted database: {DB_FILE}")

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_data(db)
        print("Database recreated and seed data inserted.")
    finally:
        db.close()


if __name__ == "__main__":
    main()

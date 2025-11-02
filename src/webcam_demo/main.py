"""Main entry point for webcam demo backend"""

from sqlmodel import select, Session, SQLModel

from webcam_demo.bigwhite import BigWhiteWebcam, create_webcams, update_indices
from webcam_demo.db import engine


def create_db_and_tables():
    """Initialize the database."""
    SQLModel.metadata.create_all(engine)


def main():
    """Main entry point for web demo backend."""
    # create_db_and_tables()
    # create_webcams()
    # update_indices()
    with Session(engine) as session:
        stmt = select(BigWhiteWebcam).where(BigWhiteWebcam.name == "Village Centre")
        w = session.exec(stmt).first()
        with open("foo.jpg", "wb") as f:
            w.read(w.last_index).save(f)


if __name__ == "__main__":
    main()

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()


# Dependency for FastAPI
async def get_db():
    try:
        async with AsyncSessionLocal() as session:
            yield session
    except Exception as e:
        # Log the error and re-raise
        print(f"Database connection error: {e}")
        raise

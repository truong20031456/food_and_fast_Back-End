"""Add Google OAuth fields to users table

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add Google OAuth fields to users table
    op.add_column("users", sa.Column("google_id", sa.String(100), nullable=True))
    op.add_column("users", sa.Column("google_picture", sa.String(500), nullable=True))

    # Create index on google_id for faster lookups
    op.create_index("ix_users_google_id", "users", ["google_id"], unique=True)


def downgrade() -> None:
    # Remove Google OAuth fields from users table
    op.drop_index("ix_users_google_id", "users")
    op.drop_column("users", "google_picture")
    op.drop_column("users", "google_id")

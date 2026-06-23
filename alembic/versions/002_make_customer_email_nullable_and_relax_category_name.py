"""make customer.email nullable and relax unique constraint on category.name

Revision ID: 002_make_customer_email_nullable_and_relax_category_name
Revises: 001_initial
Create Date: 2026-06-23 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002_make_customer_email_nullable_and_relax_category_name'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade():
    # make customers.email nullable
    op.alter_column('customers', 'email', existing_type=sa.String(length=320), nullable=True)

    # drop unique constraint on categories.name if it exists
    op.execute("ALTER TABLE categories DROP CONSTRAINT IF EXISTS categories_name_key;")
    # drop unique index if exists (index name may vary)
    op.execute("DROP INDEX IF EXISTS uq_categories_name;")


def downgrade():
    # revert customers.email to not nullable (may fail if nulls exist)
    op.alter_column('customers', 'email', existing_type=sa.String(length=320), nullable=False)

    # Note: restoring unique constraint on categories.name is unsafe if duplicates exist.
    # The downgrade will attempt to recreate a unique constraint named categories_name_key.
    op.execute("ALTER TABLE categories ADD CONSTRAINT categories_name_key UNIQUE (name);")

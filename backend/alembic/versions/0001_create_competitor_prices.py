# pyright: reportUnknownArgumentType=false
"""Create competitor_prices table

Revision ID: 0001_create_competitor_prices
Revises: None
Create Date: 2025-08-25
"""

# Alembic revision identifiers
revision = "0001_create_competitor_prices"
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(  # type: ignore
        'competitor_prices',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('source', sa.String(length=255), nullable=False, index=True),
        sa.Column('external_id', sa.String(length=255), nullable=True, index=True),
        sa.Column('price', sa.Float, nullable=True),
        sa.Column('meta', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )


def downgrade():
    op.drop_table('competitor_prices')

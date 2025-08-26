"""create missing tables: users, leads, offers, customers, subscriptions

Revision ID: add_missing_tables_20250826
Revises: 396a9a1b094c
Create Date: 2025-08-26 00:00:00
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_missing_tables_20250826'
down_revision = '396a9a1b094c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # users
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
    )
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_id', 'users', ['id'])

    # leads
    op.create_table(
        'leads',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=255), nullable=True),
        sa.Column('source', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_leads_email', 'leads', ['email'])
    op.create_index('ix_leads_id', 'leads', ['id'])

    # offers
    op.create_table(
        'offers',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=1024), nullable=True),
        sa.Column('businesses', sa.String(length=1024), nullable=True),
        sa.Column('predicted_uplift', sa.Float, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_offers_id', 'offers', ['id'])

    # customers
    op.create_table(
        'customers',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('stripe_customer_id', sa.String(length=255), nullable=False),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=True),
    )
    op.create_index('ix_customers_id', 'customers', ['id'])
    op.create_index('ix_customers_stripe_customer_id', 'customers', ['stripe_customer_id'])

    # subscriptions
    op.create_table(
        'subscriptions',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('stripe_subscription_id', sa.String(length=255), nullable=False),
        sa.Column('customer_id', sa.Integer, sa.ForeignKey('customers.id'), nullable=False),
        sa.Column('status', sa.String(length=255), nullable=True),
    )
    op.create_index('ix_subscriptions_id', 'subscriptions', ['id'])
    op.create_index('ix_subscriptions_stripe_subscription_id', 'subscriptions', ['stripe_subscription_id'])


def downgrade() -> None:
    op.drop_index('ix_subscriptions_stripe_subscription_id', table_name='subscriptions')
    op.drop_index('ix_subscriptions_id', table_name='subscriptions')
    op.drop_table('subscriptions')

    op.drop_index('ix_customers_stripe_customer_id', table_name='customers')
    op.drop_index('ix_customers_id', table_name='customers')
    op.drop_table('customers')

    op.drop_index('ix_offers_id', table_name='offers')
    op.drop_table('offers')

    op.drop_index('ix_leads_id', table_name='leads')
    op.drop_index('ix_leads_email', table_name='leads')
    op.drop_table('leads')

    op.drop_index('ix_users_id', table_name='users')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')

"""initial schema

Revision ID: 001_initial
Revises: 
Create Date: 2026-06-16 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'suppliers',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('region', sa.String(length=50), nullable=False),
        sa.Column('tier', sa.Integer(), nullable=False, server_default='3'),
        sa.Column('lead_time_mean', sa.Float(), nullable=False, server_default='7.0'),
        sa.Column('lead_time_std', sa.Float(), nullable=False, server_default='2.0'),
        sa.Column('on_time_rate', sa.Float(), nullable=False, server_default='0.9'),
    )

    op.create_table(
        'products',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('sku', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('unit_cost', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('critical', sa.Boolean(), nullable=False, server_default='false'),
    )

    op.create_table(
        'orders',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('product_id', sa.Integer(), sa.ForeignKey('products.id'), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('order_date', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        'shipments',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('order_id', sa.Integer(), sa.ForeignKey('orders.id'), nullable=False),
        sa.Column('supplier_id', sa.Integer(), sa.ForeignKey('suppliers.id'), nullable=False),
        sa.Column('shipped_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('delivered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('lead_time_days', sa.Float(), nullable=True),
        sa.Column('delayed', sa.Boolean(), nullable=False, server_default='false'),
    )

    op.create_table(
        'warehouses',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('region', sa.String(length=50), nullable=False),
    )

    op.create_table(
        'inventory',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('product_id', sa.Integer(), sa.ForeignKey('products.id'), nullable=False),
        sa.Column('warehouse_id', sa.Integer(), sa.ForeignKey('warehouses.id'), nullable=False),
        sa.Column('snapshot_date', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False, server_default='0'),
    )


def downgrade():
    op.drop_table('inventory')
    op.drop_table('warehouses')
    op.drop_table('shipments')
    op.drop_table('orders')
    op.drop_table('products')
    op.drop_table('suppliers')

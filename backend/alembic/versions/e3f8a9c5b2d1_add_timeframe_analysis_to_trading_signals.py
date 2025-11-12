"""Add timeframe_analysis to trading_signals

Revision ID: e3f8a9c5b2d1
Revises: d2497ea4a377
Create Date: 2025-11-13 01:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e3f8a9c5b2d1'
down_revision: Union[str, None] = 'd2497ea4a377'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add timeframe_analysis column to trading_signals table."""
    op.add_column('trading_signals', sa.Column('timeframe_analysis', sa.JSON(), nullable=True))


def downgrade() -> None:
    """Remove timeframe_analysis column from trading_signals table."""
    op.drop_column('trading_signals', 'timeframe_analysis')

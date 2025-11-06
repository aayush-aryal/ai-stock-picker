"""changed UserStocks shares table to be Float instead of Int

Revision ID: 2e615bfda74e
Revises: 86b60855f6d3
Create Date: 2025-11-05 14:19:41.553303

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2e615bfda74e'
down_revision: Union[str, Sequence[str], None] = '86b60855f6d3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

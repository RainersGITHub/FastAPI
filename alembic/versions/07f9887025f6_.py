"""Add content column

Revision ID: 07f9887025f6
Revises: 4122a490443f
Create Date: 2024-04-06 16:59:39.443623

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '07f9887025f6'
down_revision: Union[str, None] = '4122a490443f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('posts', sa.Column('content', sa.String(), nullable=False))
    pass


def downgrade():
    op.drop_column('posts', 'content')
    pass

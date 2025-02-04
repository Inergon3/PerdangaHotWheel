"""empty message

Revision ID: 0f480addf022
Revises: 3f619e7da049
Create Date: 2025-02-04 19:40:34.950311

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0f480addf022'
down_revision: Union[str, None] = '3f619e7da049'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('members', sa.Column('gameWin', sa.String(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('members', 'gameWin')
    # ### end Alembic commands ###

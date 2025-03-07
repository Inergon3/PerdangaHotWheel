"""empty message

Revision ID: 1dac06b42d40
Revises: a7f536aa69f0
Create Date: 2025-03-07 17:09:32.897639

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1dac06b42d40'
down_revision: Union[str, None] = 'a7f536aa69f0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('eventmember', sa.Column('game_win', sa.String(), nullable=True))
    op.drop_column('members', 'gameWin')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('members', sa.Column('gameWin', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_column('eventmember', 'game_win')
    # ### end Alembic commands ###

"""empty message

Revision ID: e1daa92f9396
Revises: 9f85a6cfcafa
Create Date: 2025-02-07 18:02:31.343770

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e1daa92f9396'
down_revision: Union[str, None] = '9f85a6cfcafa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('games_name_game_key', 'games', type_='unique')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('games_name_game_key', 'games', ['name_game'])
    # ### end Alembic commands ###

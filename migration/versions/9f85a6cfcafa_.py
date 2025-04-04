"""empty message

Revision ID: 9f85a6cfcafa
Revises: b9f9de557196
Create Date: 2025-02-07 16:44:06.816091

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9f85a6cfcafa'
down_revision: Union[str, None] = 'b9f9de557196'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'events', ['name_event'])
    op.add_column('games', sa.Column('event_id', sa.Integer(), nullable=False))
    op.create_unique_constraint(None, 'games', ['name_game'])
    op.create_foreign_key(None, 'games', 'events', ['event_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'games', type_='foreignkey')
    op.drop_constraint(None, 'games', type_='unique')
    op.drop_column('games', 'event_id')
    op.drop_constraint(None, 'events', type_='unique')
    # ### end Alembic commands ###

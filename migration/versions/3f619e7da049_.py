"""empty message

Revision ID: 3f619e7da049
Revises: bfa3754d5ece
Create Date: 2025-02-04 19:39:05.837611

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3f619e7da049'
down_revision: Union[str, None] = 'bfa3754d5ece'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('members', sa.Column('event_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'members', 'events', ['event_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'members', type_='foreignkey')
    op.drop_column('members', 'event_id')
    # ### end Alembic commands ###

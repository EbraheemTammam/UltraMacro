"""year to varchar

Revision ID: b8effc786c53
Revises: 7cdce7b7c93d
Create Date: 2024-05-17 21:04:48.197790

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b8effc786c53'
down_revision: Union[str, None] = '7cdce7b7c93d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('enrollments', 'year',
               existing_type=sa.INTEGER(),
               type_=sa.String(length=4),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('enrollments', 'year',
               existing_type=sa.String(length=4),
               type_=sa.INTEGER(),
               existing_nullable=False)
    # ### end Alembic commands ###

"""course

Revision ID: 5d2802af92fa
Revises: 41a2bc0837a2
Create Date: 2024-03-06 09:09:38.041144

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5d2802af92fa'
down_revision: Union[str, None] = '41a2bc0837a2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('courses',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('code', sa.String(length=10), nullable=False),
    sa.Column('name', sa.String(length=60), nullable=False),
    sa.Column('lecture_hours', sa.Integer(), nullable=False),
    sa.Column('practical_hours', sa.Integer(), nullable=False),
    sa.Column('credit_hours', sa.Integer(), nullable=False),
    sa.Column('level', sa.Integer(), nullable=False),
    sa.Column('semester', sa.Integer(), nullable=False),
    sa.Column('required', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_courses_id'), 'courses', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_courses_id'), table_name='courses')
    op.drop_table('courses')
    # ### end Alembic commands ###

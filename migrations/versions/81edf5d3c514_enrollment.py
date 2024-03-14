"""enrollment

Revision ID: 81edf5d3c514
Revises: 84afa7aafef9
Create Date: 2024-03-06 13:22:25.595826

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '81edf5d3c514'
down_revision: Union[str, None] = '84afa7aafef9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('enrollments',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('seat_id', sa.Integer(), nullable=False),
    sa.Column('level', sa.Integer(), nullable=False),
    sa.Column('semester', sa.Integer(), nullable=False),
    sa.Column('year', sa.Integer(), nullable=False),
    sa.Column('month', sa.String(length=10), nullable=False),
    sa.Column('points', sa.Float(), nullable=False),
    sa.Column('mark', sa.Float(), nullable=False),
    sa.Column('full_mark', sa.Integer(), nullable=False),
    sa.Column('grade', sa.String(length=3), nullable=False),
    sa.Column('student_id', sa.UUID(), nullable=False),
    sa.Column('course_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['student_id'], ['students.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_enrollments_id'), 'enrollments', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_enrollments_id'), table_name='enrollments')
    op.drop_table('enrollments')
    # ### end Alembic commands ###

"""student

Revision ID: 84afa7aafef9
Revises: 5d2802af92fa
Create Date: 2024-03-06 10:17:54.646161

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '84afa7aafef9'
down_revision: Union[str, None] = '5d2802af92fa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('students',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=60), nullable=False),
    sa.Column('level', sa.Integer(), nullable=False),
    sa.Column('registered_hours', sa.Integer(), nullable=False),
    sa.Column('passed_hours', sa.Integer(), nullable=False),
    sa.Column('excluded_hours', sa.Integer(), nullable=False),
    sa.Column('research_hours', sa.Integer(), nullable=False),
    sa.Column('total_points', sa.Float(), nullable=False),
    sa.Column('gpa', sa.Float(), nullable=False),
    sa.Column('total_mark', sa.Float(), nullable=False),
    sa.Column('graduate', sa.Boolean(), nullable=False),
    sa.Column('group_id', sa.Integer(), nullable=False),
    sa.Column('division_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['division_id'], ['divisions.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['group_id'], ['divisions.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_students_id'), 'students', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_students_id'), table_name='students')
    op.drop_table('students')
    # ### end Alembic commands ###

"""user

Revision ID: 41a2bc0837a2
Revises: c710a1a7b922
Create Date: 2024-03-06 09:05:23.531281

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision: str = '41a2bc0837a2'
down_revision: Union[str, None] = 'c710a1a7b922'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('first_name', sa.String(length=50), nullable=False),
    sa.Column('last_name', sa.String(length=50), nullable=False),
    sa.Column('email', sqlalchemy_utils.types.email.EmailType(length=255), nullable=False),
    sa.Column('password', sqlalchemy_utils.types.password.PasswordType(schemes=['bcrypt'], deprecated="auto"), nullable=False),
    sa.Column('is_admin', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.drop_index('ix_courses_id', table_name='courses')
    op.drop_table('courses')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('courses',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('code', sa.VARCHAR(length=10), nullable=False),
    sa.Column('name', sa.VARCHAR(length=60), nullable=False),
    sa.Column('lecture_hours', sa.INTEGER(), nullable=False),
    sa.Column('practical_hours', sa.INTEGER(), nullable=False),
    sa.Column('credit_hours', sa.INTEGER(), nullable=False),
    sa.Column('level', sa.INTEGER(), nullable=False),
    sa.Column('semester', sa.INTEGER(), nullable=False),
    sa.Column('required', sa.BOOLEAN(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_courses_id', 'courses', ['id'], unique=False)
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    # ### end Alembic commands ###
"""change role to string

Revision ID: 01bb2c0550b7
Revises: e9de8891839d
Create Date: 2026-05-02 09:44:42.634513

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '01bb2c0550b7'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # MySQL: ubah kolom role dari ENUM jadi VARCHAR
    op.alter_column('users', 'role',
                    existing_type=sa.Enum('student', 'instructor', 'admin', 'superadmin'),
                    type_=sa.String(20),
                    existing_nullable=False,
                    existing_server_default='student')


def downgrade():
    # Balikin lagi ke ENUM kalo mau rollback
    op.alter_column('users', 'role',
                    existing_type=sa.String(20),
                    type_=sa.Enum('student', 'instructor', 'admin', 'superadmin'),
                    existing_nullable=False,
                    existing_server_default='student')
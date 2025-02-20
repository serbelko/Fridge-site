"""empty message

Revision ID: ecdecd82c58c
Revises: 2df51ba946e3
Create Date: 2025-02-10 00:32:39.205981

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ecdecd82c58c'
down_revision = '2df51ba946e3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('analytics', schema=None) as batch_op:
        batch_op.add_column(sa.Column('action', sa.Integer(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('analytics', schema=None) as batch_op:
        batch_op.drop_column('action')

    # ### end Alembic commands ###

"""empty message

Revision ID: 091783f172cd
Revises: db1e192d53db
Create Date: 2024-05-02 10:33:18.672003

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '091783f172cd'
down_revision = 'db1e192d53db'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('prompt', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_RAG_enabled', sa.Boolean(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('prompt', schema=None) as batch_op:
        batch_op.drop_column('is_RAG_enabled')

    # ### end Alembic commands ###

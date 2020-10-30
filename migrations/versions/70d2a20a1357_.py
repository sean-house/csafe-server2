"""empty message

Revision ID: 70d2a20a1357
Revises: e4bd1622f982
Create Date: 2020-10-30 20:21:56.508400

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '70d2a20a1357'
down_revision = 'e4bd1622f982'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('relationship', sa.Column('safe_id', sa.String(length=64), nullable=False))
    op.create_foreign_key(op.f('fk_relationship_safe_id_safe'), 'relationship', 'safe', ['safe_id'], ['hardware_id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f('fk_relationship_safe_id_safe'), 'relationship', type_='foreignkey')
    op.drop_column('relationship', 'safe_id')
    # ### end Alembic commands ###

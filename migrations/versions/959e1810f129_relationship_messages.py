"""Relationship messages

Revision ID: 959e1810f129
Revises: 70d2a20a1357
Create Date: 2020-10-31 17:41:48.099648

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '959e1810f129'
down_revision = '70d2a20a1357'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('relationship_message',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('relationship_id', sa.Integer(), nullable=False),
    sa.Column('originator_id', sa.Integer(), nullable=False),
    sa.Column('message', sa.Text(), nullable=False),
    sa.Column('message_timestamp', sa.DateTime(), nullable=False),
    sa.Column('seen_by_kh', sa.Boolean(), server_default=sa.text('0'), nullable=False),
    sa.Column('seen_by_sh', sa.Boolean(), server_default=sa.text('0'), nullable=False),
    sa.ForeignKeyConstraint(['originator_id'], ['users.id'], name=op.f('fk_relationship_message_originator_id_users')),
    sa.ForeignKeyConstraint(['relationship_id'], ['relationship.id'], name=op.f('fk_relationship_message_relationship_id_relationship')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_relationship_message'))
    )
    # op.create_foreign_key(op.f('fk_relationship_safe_id_safe'), 'relationship', 'safe', ['safe_id'], ['hardware_id'])
    # op.create_unique_constraint(op.f('uq_users_displayname'), 'users', ['displayname'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f('uq_users_displayname'), 'users', type_='unique')
    op.drop_constraint(op.f('fk_relationship_safe_id_safe'), 'relationship', type_='foreignkey')
    op.drop_table('relationship_message')
    # ### end Alembic commands ###

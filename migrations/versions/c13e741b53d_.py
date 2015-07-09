"""empty message

Revision ID: c13e741b53d
Revises: 2fbb8ebcb2da
Create Date: 2015-07-10 00:12:23.308225

"""

# revision identifiers, used by Alembic.
revision = 'c13e741b53d'
down_revision = '2fbb8ebcb2da'

from alembic import op
import sqlalchemy as sa


def upgrade():
	op.add_column('processed', sa.Column('player_title', sa.String(length=255), nullable=True))
    


def downgrade():
	op.drop_column('processed', 'player_title')
    

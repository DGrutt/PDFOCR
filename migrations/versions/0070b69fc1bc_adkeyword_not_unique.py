"""adkeyword not unique

Revision ID: 0070b69fc1bc
Revises: 23c48bb6aa5b
Create Date: 2018-03-19 12:19:33.820548

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0070b69fc1bc'
down_revision = '23c48bb6aa5b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_document_keywordMatches', table_name='document')
    op.create_index(op.f('ix_document_keywordMatches'), 'document', ['keywordMatches'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_document_keywordMatches'), table_name='document')
    op.create_index('ix_document_keywordMatches', 'document', ['keywordMatches'], unique=1)
    # ### end Alembic commands ###

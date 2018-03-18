"""documents table

Revision ID: a0d41ab32b0d
Revises: 
Create Date: 2018-03-16 15:00:11.024649

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a0d41ab32b0d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('document',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('txtLocation', sa.String(length=300), nullable=True),
    sa.Column('imgLocation', sa.String(length=300), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_document_imgLocation'), 'document', ['imgLocation'], unique=True)
    op.create_index(op.f('ix_document_txtLocation'), 'document', ['txtLocation'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_document_txtLocation'), table_name='document')
    op.drop_index(op.f('ix_document_imgLocation'), table_name='document')
    op.drop_table('document')
    # ### end Alembic commands ###
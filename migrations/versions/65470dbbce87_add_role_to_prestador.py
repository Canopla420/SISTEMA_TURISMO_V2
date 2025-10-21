"""Add role to prestador

Revision ID: 65470dbbce87
Revises: b7b3082a45dc
Create Date: 2025-10-20 11:33:38.779498

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '65470dbbce87'
down_revision = 'b7b3082a45dc'
branch_labels = None
depends_on = None

def upgrade():
    # Añade la columna role con server_default para evitar error al alterar tabla en SQLite
    with op.batch_alter_table('prestador', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('role', sa.String(length=20), nullable=False, server_default=sa.text("'prestador'"))
        )

def downgrade():
    with op.batch_alter_table('prestador', schema=None) as batch_op:
        batch_op.drop_column('role')

    # ### end Alembic commands ###

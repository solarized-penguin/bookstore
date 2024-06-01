"""nin

Revision ID: 9b8e0cc2bfc1
Revises: 
Create Date: 2024-05-13 18:03:12.360642

"""

from typing import Sequence, Union

from alembic import op

from db.models import SQLModel

# revision identifiers, used by Alembic.
revision: str = "9b8e0cc2bfc1"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    SQLModel.metadata.create_all(op.get_bind())


def downgrade() -> None:
    SQLModel.metadata.drop_all(bind=op.get_bind())

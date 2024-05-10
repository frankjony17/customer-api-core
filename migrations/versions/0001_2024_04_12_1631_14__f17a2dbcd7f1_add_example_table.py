"""Add Example Table

Revision ID: f17a2dbcd7f1
Revises:
Create Date: 2024-04-12 16:31:14.442782

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f17a2dbcd7f1"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "example",
        sa.Column("example_name", sa.String(length=255), nullable=False),
        sa.Column("example_date", sa.Date(), nullable=False),
        sa.Column("example_number", sa.Integer(), nullable=True),
        sa.Column(
            "example_status",
            sa.Enum(
                "A",
                "B",
                name="example_status_enum",
                schema="template_core",
                inherit_schema=True,
            ),
            nullable=False,
        ),
        sa.Column("example_boolean", sa.Boolean(), nullable=False),
        sa.Column(
            "id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP(0)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP(0)"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__example")),
        schema="template_core",
    )
    op.create_index(
        op.f("ix__example__id"), "example", ["id"], unique=True, schema="template_core"
    )


def downgrade() -> None:
    op.drop_index(op.f("ix__example__id"), table_name="example", schema="template_core")
    op.drop_table("example", schema="template_core")
    # Manually dropping ExampleStatusEnum
    sa.Enum(name="example_status_enum").drop(op.get_bind(), checkfirst=False)

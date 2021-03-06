"""Add sent_mails table

Revision ID: f5d5e1df41f9
Revises: 5dd92f141282
Create Date: 2020-05-02 16:07:52.883103

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f5d5e1df41f9"
down_revision = "5dd92f141282"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "sent_mails",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("subject", sa.String(length=255), nullable=False),
        sa.Column("sender", sa.String(length=255), nullable=False),
        sa.Column("recipient_id", sa.Integer(), nullable=False),
        sa.Column("bcc", sa.String(length=255), nullable=True),
        sa.Column("template", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["recipient_id"], ["users.id"], name="fk_sent_mails_users"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
    )
    op.create_index(
        op.f("ix_sent_mails_recipient_id"), "sent_mails", ["recipient_id"], unique=False
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint("fk_sent_mails_users", "sent_mails", type_="foreignkey")
    op.drop_index(op.f("ix_sent_mails_recipient_id"), table_name="sent_mails")
    op.drop_table("sent_mails")
    # ### end Alembic commands ###

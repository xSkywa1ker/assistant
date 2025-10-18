"""initial schema"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgvector")

    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("timezone", sa.String(length=64), nullable=False, server_default="UTC"),
        sa.Column("work_hours", sa.String(length=15), nullable=False, server_default="09:00-17:00"),
        sa.Column("preferences_json", sa.JSON(), nullable=True),
    )
    op.create_index(op.f("ix_user_id"), "user", ["id"], unique=False)
    op.create_unique_constraint("uq_user_username", "user", ["username"])

    op.create_table(
        "goal",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id", ondelete="CASCADE")),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("priority", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("due", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(op.f("ix_goal_user_id"), "goal", ["user_id"], unique=False)

    op.create_table(
        "task",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id", ondelete="CASCADE")),
        sa.Column("parent_id", sa.Integer(), sa.ForeignKey("task.id", ondelete="SET NULL")),
        sa.Column("goal_id", sa.Integer(), sa.ForeignKey("goal.id", ondelete="SET NULL")),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.Enum("todo", "doing", "wait", "done", "cancel", name="taskstatus"), nullable=False, server_default="todo"),
        sa.Column("priority", sa.Integer(), nullable=True),
        sa.Column("estimate_minutes", sa.Integer(), nullable=True),
        sa.Column("due", sa.DateTime(timezone=True), nullable=True),
        sa.Column("source", sa.String(length=64), nullable=True),
        sa.Column("external_ref", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index(op.f("ix_task_user_id"), "task", ["user_id"], unique=False)
    op.create_index(op.f("ix_task_goal_id"), "task", ["goal_id"], unique=False)
    op.create_index(op.f("ix_task_status"), "task", ["status"], unique=False)
    op.create_index(op.f("ix_task_due"), "task", ["due"], unique=False)

    op.create_table(
        "wait",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id", ondelete="CASCADE")),
        sa.Column("task_id", sa.Integer(), sa.ForeignKey("task.id", ondelete="CASCADE")),
        sa.Column("wait_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("external_actor", sa.String(length=255), nullable=True),
    )
    op.create_index(op.f("ix_wait_user_id"), "wait", ["user_id"], unique=False)

    op.create_table(
        "eventlink",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id", ondelete="CASCADE")),
        sa.Column("task_id", sa.Integer(), sa.ForeignKey("task.id", ondelete="CASCADE")),
        sa.Column("provider", sa.Enum("google_calendar", "notion", "telegram", name="provider"), nullable=False),
        sa.Column("external_id", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index(op.f("ix_eventlink_user_id"), "eventlink", ["user_id"], unique=False)
    op.create_index(op.f("ix_eventlink_task_id"), "eventlink", ["task_id"], unique=False)

    op.create_table(
        "note",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id", ondelete="CASCADE")),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index(op.f("ix_note_user_id"), "note", ["user_id"], unique=False)

    op.create_table(
        "memory_chunk",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id", ondelete="CASCADE")),
        sa.Column("kind", sa.Enum("profile", "long_term", "context", name="memorykind"), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", postgresql.ARRAY(sa.Float()), nullable=True),
        sa.Column("embedding_checksum", sa.String(length=64), nullable=True, unique=True),
    )
    op.create_index(op.f("ix_memory_chunk_user_id"), "memory_chunk", ["user_id"], unique=False)

    op.create_table(
        "auditlog",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(length=255), nullable=False),
        sa.Column("payload_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index(op.f("ix_auditlog_user_id"), "auditlog", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_table("auditlog")
    op.drop_table("memory_chunk")
    op.drop_table("note")
    op.drop_table("eventlink")
    op.drop_table("wait")
    op.drop_table("task")
    op.drop_table("goal")
    op.drop_table("user")

"""initial foundation: users, organizations, memberships, projects

Revision ID: 0001
Revises:
Create Date: 2026-08-07
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql as pg

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

user_status = pg.ENUM("ACTIVE", "SUSPENDED", "DELETED", name="userstatus")
subscription_plan = pg.ENUM("FREE", "CREATOR", "STUDIO", "ENTERPRISE", name="subscriptionplan")
org_role = pg.ENUM("OWNER", "ADMIN", "DIRECTOR", "EDITOR", "WRITER", "VIEWER", name="orgrole")
project_type = pg.ENUM(
    "MOVIE", "SHORT_FILM", "COMMERCIAL", "MUSIC_VIDEO", "ANIMATION",
    "DOCUMENTARY", "TRAILER", "PRESENTATION", "TRAINING", "SOCIAL_CONTENT",
    name="projecttype",
)
project_status = pg.ENUM(
    "DRAFT", "PLANNING", "GENERATING", "EDITING", "RENDERING", "PUBLISHED", "ARCHIVED",
    name="projectstatus",
)


def upgrade() -> None:
    bind = op.get_bind()
    user_status.create(bind, checkfirst=True)
    subscription_plan.create(bind, checkfirst=True)
    org_role.create(bind, checkfirst=True)
    project_type.create(bind, checkfirst=True)
    project_status.create(bind, checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("username", sa.String(64), nullable=False),
        sa.Column("display_name", sa.String(128), nullable=False),
        sa.Column("avatar", sa.String(512), nullable=True),
        sa.Column("language", sa.String(8), nullable=False, server_default="ru"),
        sa.Column("timezone", sa.String(64), nullable=False, server_default="UTC"),
        sa.Column("subscription_plan", subscription_plan, nullable=False, server_default="FREE"),
        sa.Column("status", user_status, nullable=False, server_default="ACTIVE"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("username"),
    )
    op.create_index("ix_users_id", "users", ["id"])
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_username", "users", ["username"])

    op.create_table(
        "organizations",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("owner_id", pg.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("plan", subscription_plan, nullable=False, server_default="FREE"),
    )
    op.create_index("ix_organizations_id", "organizations", ["id"])

    op.create_table(
        "memberships",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "organization_id", pg.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column(
            "user_id", pg.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column("role", org_role, nullable=False, server_default="VIEWER"),
    )
    op.create_index("ix_memberships_id", "memberships", ["id"])

    op.create_table(
        "projects",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column(
            "organization_id", pg.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True,
        ),
        sa.Column(
            "owner_id", pg.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("type", project_type, nullable=False),
        sa.Column("status", project_status, nullable=False, server_default="DRAFT"),
        sa.Column("resolution", sa.String(16), nullable=False, server_default="1080p"),
        sa.Column("fps", sa.Integer, nullable=False, server_default="24"),
        sa.Column("duration", sa.Float, nullable=True),
        sa.Column("aspect_ratio", sa.String(16), nullable=False, server_default="16:9"),
        sa.Column("language", sa.String(8), nullable=False, server_default="ru"),
        sa.Column("target_platform", sa.String(64), nullable=True),
        sa.Column("style_profile", sa.JSON, nullable=True),
    )
    op.create_index("ix_projects_id", "projects", ["id"])
    op.create_index("ix_projects_owner_id", "projects", ["owner_id"])

    op.create_table(
        "project_settings",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "project_id", pg.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, unique=True,
        ),
        sa.Column("quality_level", sa.String(32), nullable=False, server_default="standard"),
        sa.Column("budget_limit", sa.Float, nullable=True),
        sa.Column("default_models", sa.JSON, nullable=True),
    )
    op.create_index("ix_project_settings_id", "project_settings", ["id"])


def downgrade() -> None:
    op.drop_table("project_settings")
    op.drop_table("projects")
    op.drop_table("memberships")
    op.drop_table("organizations")
    op.drop_table("users")

    bind = op.get_bind()
    project_status.drop(bind, checkfirst=True)
    project_type.drop(bind, checkfirst=True)
    org_role.drop(bind, checkfirst=True)
    subscription_plan.drop(bind, checkfirst=True)
    user_status.drop(bind, checkfirst=True)

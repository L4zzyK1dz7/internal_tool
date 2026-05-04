"""models.py — SQLAlchemy 2.0 ORM model definitions.

Defines the full database schema for the Internal Tool Directory using
SQLAlchemy's ``Mapped`` / ``mapped_column`` declarative API (2.0 style).
All relationships are declared explicitly to avoid implicit lazy-loading
surprises.

Models:
    Team      — Organisational unit that a user belongs to.
    Language  — Programming language associated with a tool.
    Category  — Functional category used to classify tools.
    User      — Application user with a role (``"user"`` or ``"admin"``).
    Tool      — The core entity representing an internal tool record.
"""

from __future__ import annotations

from datetime import datetime, UTC

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash


db = SQLAlchemy()


class Team(db.Model):
    """Organisational team that groups users.

    Acts as a reference table populated by the seed script.  Users are
    assigned exactly one team via a foreign key.
    """

    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)

    users: Mapped[list["User"]] = relationship(back_populates="team")

    def __repr__(self) -> str:
        return f"Team(id={self.id!r}, name={self.name!r})"


class Language(db.Model):
    """Programming language used to build a tool.

    Acts as a normalised reference table so that language names are
    consistent across all tool records and available as dropdown choices
    in WTForms.
    """

    __tablename__ = "languages"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)

    tools: Mapped[list["Tool"]] = relationship(back_populates="language")

    def __repr__(self) -> str:
        return f"Language(id={self.id!r}, name={self.name!r})"


class Category(db.Model):
    """Functional category used to classify tools (e.g. Analytics, Reporting).

    Acts as a normalised reference table that drives both the search filter
    and the admin tool-form dropdown.
    """

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)

    tools: Mapped[list["Tool"]] = relationship(back_populates="category")

    def __repr__(self) -> str:
        return f"Category(id={self.id!r}, name={self.name!r})"


class User(UserMixin, db.Model):
    """Application user with role-based access control.

    Inherits from :class:`flask_login.UserMixin` to satisfy the Flask-Login
    interface.  Passwords are never stored in plain text — only the
    Werkzeug-generated hash is persisted (OWASP #A2: Cryptographic Failures
    defence).
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="user", nullable=False)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)

    team: Mapped[Team] = relationship(back_populates="users")
    created_tools: Mapped[list["Tool"]] = relationship(back_populates="creator")

    def set_password(self, password: str) -> None:
        """Hash ``password`` and store the result in ``password_hash``.

        Uses Werkzeug's ``generate_password_hash`` (bcrypt/scrypt by default)
        so that the plain-text password is never persisted.

        Args:
            password: The plain-text password supplied by the user.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify a plain-text password against the stored hash.

        Args:
            password: The plain-text password to verify.

        Returns:
            ``True`` if the password matches the stored hash, ``False``
            otherwise.
        """
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self) -> bool:
        """Return ``True`` if this user holds the ``"admin"`` role.

        Used by the ``@admin_required`` decorator to gate access to
        protected routes without exposing the raw ``role`` string outside
        the model layer.
        """
        return self.role == "admin"

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, username={self.username!r}, role={self.role!r})"


class Tool(db.Model):
    """Core entity representing an internal tool in the directory.

    Uses a soft-delete pattern via the ``is_active`` boolean flag so that
    archived tools are never permanently destroyed, allowing potential data
    recovery.  All queries on active tools should filter with
    ``Tool.is_active.is_(True)``.
    """

    __tablename__ = "tools"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    data_link: Mapped[str | None] = mapped_column(String(500))
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    language_id: Mapped[int] = mapped_column(ForeignKey("languages.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    creator: Mapped[User] = relationship(back_populates="created_tools")
    category: Mapped[Category] = relationship(back_populates="tools")
    language: Mapped[Language] = relationship(back_populates="tools")

    def __repr__(self) -> str:
        return f"Tool(id={self.id!r}, name={self.name!r})"

"""routes/admin.py — Admin CRUD blueprint.

Provides the administrator-only routes for managing the tool directory.
Every route in this module is protected by the ``@admin_required`` decorator
imported from ``routes.auth``.

Routes:
    GET  /admin                   — Admin dashboard listing all active tools.
    GET|POST /admin/add           — Create a new tool record.
    GET|POST /admin/edit/<id>     — Update an existing tool record.
    POST /admin/delete/<id>       — Soft-delete (archive) a tool record.

All database mutations use SQLAlchemy 2.0 ORM calls — no raw SQL is
permitted anywhere in this module (OWASP #A1: Injection defence).
"""

from flask import Blueprint, flash, redirect, render_template, url_for
from sqlalchemy import select

from forms import ToolForm
from models import Category, Language, Tool, User, db
from routes.auth import admin_required


admin_bp = Blueprint("admin", __name__)


def _tool_statement():
    """Build the base SELECT statement for active tools ordered by name.

    Centralises the ``is_active`` filter so that the dashboard and any
    future read queries consistently exclude archived tools.

    Returns:
        A :class:`sqlalchemy.sql.Select` object ready for further
        composition or direct execution.
    """
    return select(Tool).where(Tool.is_active.is_(True)).order_by(Tool.name)


def _populate_tool_form_choices(form: ToolForm) -> ToolForm:
    """Hydrate the SelectField choices on ``form`` from the database.

    Queries ``User``, ``Category``, and ``Language`` reference tables and
    assigns the resulting ``(id, name)`` tuples to the corresponding
    :class:`~wtforms.SelectField` on the form.  Must be called before the
    form is rendered or validated on POST.

    Args:
        form: The :class:`~forms.ToolForm` instance to mutate.

    Returns:
        The same ``form`` instance with its choices populated.
    """
    form.creator_id.choices = [
        (user.id, user.username)
        for user in db.session.scalars(select(User).order_by(User.username)).all()
    ]
    form.category_id.choices = [
        (category.id, category.name)
        for category in db.session.scalars(select(Category).order_by(Category.name)).all()
    ]
    form.language_id.choices = [
        (language.id, language.name)
        for language in db.session.scalars(select(Language).order_by(Language.name)).all()
    ]
    return form


def _assign_tool_fields(tool: Tool, form: ToolForm) -> Tool:
    """Copy validated form data onto a ``Tool`` ORM instance.

    Abstracts the field-assignment logic so it can be shared between the
    add and edit routes without duplication (DRY).

    Args:
        tool: The ``Tool`` instance to update (new or existing).
        form: A validated :class:`~forms.ToolForm` containing the new data.

    Returns:
        The mutated ``tool`` instance (not yet committed to the session).
    """
    tool.name = form.name.data
    tool.description = form.description.data
    tool.data_link = form.data_link.data
    tool.creator_id = form.creator_id.data
    tool.category_id = form.category_id.data
    tool.language_id = form.language_id.data
    return tool


def _get_tool_or_404(tool_id: int) -> Tool:
    """Fetch a ``Tool`` by primary key or abort with 404.

    Uses the SQLAlchemy identity map (``db.session.get``) for an efficient
    single-row lookup that avoids a full SELECT statement when the object is
    already cached in the session.

    Args:
        tool_id: The integer primary key of the tool to retrieve.

    Returns:
        The matching :class:`~models.Tool` instance.

    Raises:
        :class:`werkzeug.exceptions.NotFound`: If no tool with the given
            ``tool_id`` exists.
    """
    tool = db.session.get(Tool, tool_id)
    if tool is None:
        from flask import abort

        abort(404)
    return tool


@admin_bp.get("/admin")
@admin_required
def dashboard():
    """Render the admin dashboard listing all active tools.

    Returns:
        The rendered ``admin/index.html`` template populated with all
        active :class:`~models.Tool` records ordered by name.
    """
    tools = db.session.scalars(_tool_statement()).all()
    return render_template("admin/index.html", tools=tools)


@admin_bp.route("/admin/add", methods=["GET", "POST"])
@admin_required
def add_tool():
    """Render and process the add-tool form.

    On GET, displays an empty :class:`~forms.ToolForm`.  On POST, validates
    the submission, creates a new active :class:`~models.Tool` record, and
    redirects to the admin dashboard on success.

    Returns:
        A redirect to ``admin.dashboard`` on success, or the rendered form
        template with validation errors.
    """
    form = _populate_tool_form_choices(ToolForm())
    if form.validate_on_submit():
        tool = _assign_tool_fields(Tool(is_active=True), form)
        db.session.add(tool)
        db.session.commit()
        flash("Tool created successfully.", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template("admin/tool_form.html", form=form, heading="Add Tool")


@admin_bp.route("/admin/edit/<int:tool_id>", methods=["GET", "POST"])
@admin_required
def edit_tool(tool_id: int):
    """Render and process the edit-tool form for an existing tool.

    On GET, pre-populates the form with the current tool data.  On POST,
    validates the submission and persists the changes.

    Args:
        tool_id: The primary key of the tool to edit.

    Returns:
        A redirect to ``admin.dashboard`` on success, or the rendered form
        template with validation errors.  Aborts with 404 if the tool does
        not exist.
    """
    tool = _get_tool_or_404(tool_id)
    form = _populate_tool_form_choices(ToolForm(obj=tool))
    if form.validate_on_submit():
        _assign_tool_fields(tool, form)
        db.session.commit()
        flash("Tool updated successfully.", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template("admin/tool_form.html", form=form, heading="Edit Tool")


@admin_bp.post("/admin/delete/<int:tool_id>")
@admin_required
def delete_tool(tool_id: int):
    """Soft-delete a tool by setting its ``is_active`` flag to ``False``.

    The record is retained in the database for audit purposes but is
    excluded from all active-tool queries.  This fulfils the PRD's
    soft-delete requirement to prevent accidental data loss.

    Args:
        tool_id: The primary key of the tool to archive.

    Returns:
        A redirect to ``admin.dashboard`` with a confirmation flash message.
        Aborts with 404 if the tool does not exist.
    """
    tool = _get_tool_or_404(tool_id)
    tool.is_active = False
    db.session.commit()
    flash("Tool archived successfully.", "success")
    return redirect(url_for("admin.dashboard"))

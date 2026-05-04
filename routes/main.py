"""routes/main.py — Public-facing directory routes.

Provides the read-only routes accessible to all users (authenticated or not):

- ``/``            — Paginated tool directory with optional search.
- ``/tools/<id>``  — Detail view for a single tool.

Search uses SQLAlchemy ``ilike`` queries for case-insensitive matching on
tool name and category name.  Results are paginated in pages of
``PAGE_SIZE`` (20) items using an offset/limit approach — fetching
``PAGE_SIZE + 1`` items to determine whether a next-page button should
be shown without an expensive ``COUNT`` query.
"""

from flask import Blueprint, abort, render_template, request
from sqlalchemy import or_, select
from sqlalchemy.orm import joinedload

from forms import SearchForm
from models import Category, Tool, User, db

main_bp = Blueprint("main", __name__)

PAGE_SIZE = 20


def _coerce_page(value: str | None) -> int:
    """Convert a raw query-string value to a safe positive page number.

    Handles missing, non-numeric, and non-positive values gracefully so
    that malformed ``?page=`` parameters never cause a 500 error.

    Args:
        value: The raw string from ``request.args.get("page")``, or
            ``None`` if the parameter is absent.

    Returns:
        A positive integer page number, defaulting to ``1`` for any
        invalid input.
    """
    try:
        page = int(value or "1")
    except ValueError:
        return 1
    return page if page > 0 else 1


def _build_directory_statement(search_term: str | None):
    """Build a SELECT statement for active tools with optional search filtering.

    Eagerly loads the ``creator → team``, ``category``, and ``language``
    relationships in a single query to avoid N+1 issues when rendering the
    tool cards.  When ``search_term`` is provided, adds a case-insensitive
    ``ILIKE`` filter across tool name and category name.

    Args:
        search_term: A plain string to match against tool name and category
            name using ``ILIKE``, or ``None`` to return all active tools.

    Returns:
        A composable :class:`sqlalchemy.sql.Select` statement (without
        ``LIMIT`` / ``OFFSET`` applied — those are added by the caller).
    """
    statement = (
        select(Tool)
        .where(Tool.is_active.is_(True))
        .options(
            joinedload(Tool.creator).joinedload(User.team),
            joinedload(Tool.category),
            joinedload(Tool.language),
        )
        .order_by(Tool.name)
    )

    if search_term:
        pattern = f"%{search_term}%"
        statement = statement.join(Tool.category).where(
            or_(Tool.name.ilike(pattern), Category.name.ilike(pattern))
        )

    return statement


def _fetch_directory_page(search_term: str | None, page: int) -> tuple[list[Tool], bool]:
    """Execute a paginated directory query and detect whether more pages exist.

    Fetches ``PAGE_SIZE + 1`` rows.  If a 21st row is returned, the extra
    item is discarded and ``has_next_page`` is set to ``True``, enabling the
    "Load More" button without a separate ``COUNT`` query.

    Args:
        search_term: Optional search string forwarded to
            ``_build_directory_statement``.
        page:        1-based page number.

    Returns:
        A two-tuple of ``(tools, has_next_page)`` where ``tools`` contains
        at most ``PAGE_SIZE`` items and ``has_next_page`` indicates whether
        additional results exist.
    """
    offset = (page - 1) * PAGE_SIZE
    tools = db.session.scalars(
        _build_directory_statement(search_term).offset(offset).limit(PAGE_SIZE + 1)
    ).all()
    return tools[:PAGE_SIZE], len(tools) > PAGE_SIZE


@main_bp.get("/")
def index():
    """Render the public tool directory with search and pagination.

    Reads the optional ``q`` (search term) and ``page`` query parameters,
    delegates to ``_fetch_directory_page``, and passes the results to the
    ``index.html`` template.

    Returns:
        The rendered ``index.html`` template with the current page of tools,
        the search form, and pagination context variables.
    """
    form = SearchForm(request.args)
    search_term = form.q.data.strip() if form.validate() and form.q.data else ""
    page = _coerce_page(request.args.get("page"))
    tools, has_next_page = _fetch_directory_page(search_term or None, page)

    return render_template(
        "index.html",
        form=form,
        tools=tools,
        search_term=search_term,
        page=page,
        has_next_page=has_next_page,
    )


@main_bp.get("/tools/<int:tool_id>")
def tool_detail(tool_id: int):
    """Render the detail page for a single active tool.

    Eagerly loads the creator (with team), category, and language to avoid
    N+1 queries on the detail template.

    Args:
        tool_id: The primary key of the tool to display.

    Returns:
        The rendered ``tool_detail.html`` template.  Aborts with 404 if the
        tool does not exist or has been soft-deleted.
    """
    statement = (
        select(Tool)
        .where(Tool.id == tool_id, Tool.is_active.is_(True))
        .options(
            joinedload(Tool.creator).joinedload(User.team),
            joinedload(Tool.category),
            joinedload(Tool.language),
        )
    )
    tool = db.session.scalar(statement)
    if tool is None:
        abort(404)

    return render_template("tool_detail.html", tool=tool)

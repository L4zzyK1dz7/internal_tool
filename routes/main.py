from flask import Blueprint, abort, render_template, request
from sqlalchemy import or_, select
from sqlalchemy.orm import joinedload

from forms import SearchForm
from models import Category, Tool, User, db

main_bp = Blueprint("main", __name__)

PAGE_SIZE = 20


def _coerce_page(value: str | None) -> int:
    try:
        page = int(value or "1")
    except ValueError:
        return 1
    return page if page > 0 else 1


def _build_directory_statement(search_term: str | None):
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
    offset = (page - 1) * PAGE_SIZE
    tools = db.session.scalars(
        _build_directory_statement(search_term).offset(offset).limit(PAGE_SIZE + 1)
    ).all()
    return tools[:PAGE_SIZE], len(tools) > PAGE_SIZE


@main_bp.get("/")
def index():
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

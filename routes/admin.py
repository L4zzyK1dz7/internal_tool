from flask import Blueprint, flash, redirect, render_template, url_for
from sqlalchemy import select

from forms import ToolForm
from models import Category, Language, Tool, User, db
from routes.auth import admin_required


admin_bp = Blueprint("admin", __name__)


def _tool_statement():
    return select(Tool).where(Tool.is_active.is_(True)).order_by(Tool.name)


def _populate_tool_form_choices(form: ToolForm) -> ToolForm:
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
    tool.name = form.name.data
    tool.description = form.description.data
    tool.data_link = form.data_link.data
    tool.creator_id = form.creator_id.data
    tool.category_id = form.category_id.data
    tool.language_id = form.language_id.data
    return tool


def _get_tool_or_404(tool_id: int) -> Tool:
    tool = db.session.get(Tool, tool_id)
    if tool is None:
        from flask import abort

        abort(404)
    return tool


@admin_bp.get("/admin")
@admin_required
def dashboard():
    tools = db.session.scalars(_tool_statement()).all()
    return render_template("admin/index.html", tools=tools)


@admin_bp.route("/admin/add", methods=["GET", "POST"])
@admin_required
def add_tool():
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
    tool = _get_tool_or_404(tool_id)
    tool.is_active = False
    db.session.commit()
    flash("Tool archived successfully.", "success")
    return redirect(url_for("admin.dashboard"))

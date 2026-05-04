"""forms.py — WTForms form definitions.

Provides all server-side form classes used by the application.  Every form
inherits from :class:`flask_wtf.FlaskForm` which automatically includes
CSRF protection on all POST submissions.

Forms:
    LoginForm  — Authenticates a user with username and password.
    ToolForm   — Creates or updates a tool record via the admin interface.
    SearchForm — Accepts an optional query string for the tool directory.
"""

from flask_wtf import FlaskForm
from wtforms import PasswordField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional, URL


class LoginForm(FlaskForm):
    """Form for user authentication.

    Validates that both ``username`` and ``password`` are present and within
    acceptable length bounds before the route handler queries the database.
    """

    username = StringField("Username", validators=[DataRequired(), Length(max=80)])
    password = PasswordField("Password", validators=[DataRequired(), Length(max=255)])
    submit = SubmitField("Log In")


class ToolForm(FlaskForm):
    """Form for creating and editing tool records.

    ``creator_id``, ``category_id``, and ``language_id`` are
    :class:`wtforms.SelectField` instances whose ``choices`` must be
    populated dynamically from the database before the form is rendered
    (see ``_populate_tool_form_choices`` in ``routes/admin.py``).
    """

    name = StringField("Tool Name", validators=[DataRequired(), Length(max=200)])
    description = TextAreaField("Description", validators=[Optional(), Length(max=5000)])
    data_link = StringField("Data Link", validators=[Optional(), URL(), Length(max=500)])
    creator_id = SelectField("Creator", coerce=int, validators=[DataRequired()])
    category_id = SelectField("Category", coerce=int, validators=[DataRequired()])
    language_id = SelectField("Language", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Save Tool")


class SearchForm(FlaskForm):
    """Form for the public tool-directory search bar.

    Submitted via GET so that search results are bookmarkable.  The ``q``
    field is optional — an empty submission returns the full paginated
    listing.
    """

    # Remove CSRF validation because the form is submitted via GET request so token is not included
    # This is not a security risk because the form does not perform any state-changing operations
    # and the results are bookmarkable
    class Meta:
        csrf = False

    q = StringField("Search", validators=[Optional(), Length(max=120)])
    submit = SubmitField("Search")


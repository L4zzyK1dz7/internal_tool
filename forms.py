from flask_wtf import FlaskForm
from wtforms import PasswordField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional, URL


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(max=80)])
    password = PasswordField("Password", validators=[DataRequired(), Length(max=255)])
    submit = SubmitField("Log In")


class ToolForm(FlaskForm):
    name = StringField("Tool Name", validators=[DataRequired(), Length(max=200)])
    description = TextAreaField("Description", validators=[Optional(), Length(max=5000)])
    data_link = StringField("Data Link", validators=[Optional(), URL(), Length(max=500)])
    creator_id = SelectField("Creator", coerce=int, validators=[DataRequired()])
    category_id = SelectField("Category", coerce=int, validators=[DataRequired()])
    language_id = SelectField("Language", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Save Tool")


class SearchForm(FlaskForm):
    q = StringField("Search", validators=[Optional(), Length(max=120)])
    submit = SubmitField("Search")

from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, EmailField
from wtforms.validators import DataRequired, Length, Email


class RegisterForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Length(min=5, max=50), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=5, max=10)])
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Length(min=5, max=50), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=5, max=10)])
    submit = SubmitField("Login")





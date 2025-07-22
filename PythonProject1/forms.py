from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    username = StringField("მომხმარებელი", validators=[DataRequired()])
    password = PasswordField("პაროლი", validators=[DataRequired()])
    submit = SubmitField("შესვლა")

class SignupForm(FlaskForm):
    username = StringField("მომხმარებელი", validators=[DataRequired(), Length(min=3)])
    password = PasswordField("პაროლი", validators=[DataRequired(), Length(min=4)])
    submit = SubmitField("რეგისტრაცია")

class StoryForm(FlaskForm):
    title = StringField('სათაური', validators=[DataRequired()])
    content = TextAreaField('ზღაპარი', validators=[DataRequired()])
    submit = SubmitField('დამატება')

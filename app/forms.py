from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from wtforms import IntegerField
from wtforms.validators import NumberRange
from wtforms.fields import EmailField

class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

class RecipeForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    ingredients = TextAreaField('Ingredients (one per line)', validators=[DataRequired()])
    steps = TextAreaField('Steps (one per line)', validators=[DataRequired()])
    image_url = StringField('Image URL (optional)')
    tags = StringField('Tags (comma-separated)')
    submit = SubmitField('Save Recipe')

class ReviewForm(FlaskForm):
    comment = TextAreaField('Your Comment', validators=[DataRequired()])
    rating = IntegerField('Rating (1 to 5)', validators=[DataRequired(), NumberRange(min=1, max=5)])
    submit = SubmitField('Post Review')

class DeleteForm(FlaskForm):
    pass  # No fields, just CSRF protection
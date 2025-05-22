from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length

class TributeForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=1, max=100)])
    content = TextAreaField('Your Message', validators=[DataRequired()])
    is_visible = BooleanField('Make visible to recipient now')
    submit = SubmitField('Save Tribute')

class TributeVisibilityForm(FlaskForm):
    is_visible = BooleanField('Make visible to recipient')
    submit = SubmitField('Update Visibility') 
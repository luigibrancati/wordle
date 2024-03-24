from ..db import crud
from .auth_utils import verify_password
from starlette_wtf import StarletteForm
from wtforms.widgets import PasswordInput
from wtforms import StringField, PasswordField, ValidationError
from wtforms.validators	import DataRequired, EqualTo
from ..db.database import get_db


class LoginForm(StarletteForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField(
        'Password',
        widget=PasswordInput(hide_value=False),
        validators=[
            DataRequired('Please enter your password')
        ]
    )

    async def async_validate_username(self, field):
        db = next(get_db())
        user = crud.get_user_by_name(field.data, db)
        if user is None:
            raise ValidationError('Username not found')

    async def async_validate_password(self, field):
        db = next(get_db())
        user = crud.get_user_by_name(self.username.data, db)
        if user is not None and not verify_password(field.data, user.hashed_password):
            raise ValidationError('Wrong password')


class RegisterForm(StarletteForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField(
        'Password',
        widget=PasswordInput(hide_value=False),
        validators=[
            DataRequired('Please enter your password'),
            EqualTo('password_confirm', message='Passwords must match')
        ]
    )
    password_confirm = PasswordField(
        'Confirm Password',
        widget=PasswordInput(hide_value=False),
        validators=[
            DataRequired('Please confirm your password')
        ]
    )

    async def async_validate_username(self, field):
        db = next(get_db())
        user = crud.get_user_by_name(field.data, db)
        if user is not None:
            raise ValidationError('Username already exists!')

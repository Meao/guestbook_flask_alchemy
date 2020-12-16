from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class LoginForm(FlaskForm):
    email = StringField("Email: ", validators=[Email("Некорректный email")])
    psw = PasswordField("Пароль: ", validators=[DataRequired(), Length(min=4, max=100, message="Пароль должен быть от 4 до 100 символов")])
    remember = BooleanField("Запомнить", default=False)
    submit = SubmitField("Войти")

class RegisterForm(FlaskForm):
    name = StringField("Имя (от 4 до 300 символов): ", validators=[Length(min=4, max=100, message="Имя должно быть от 4 до 100 символов")])
    email = StringField("Email: ", validators=[Email("Некорректный email")])
    psw = PasswordField("Пароль (от 4 до 300 символов): ", validators=[DataRequired(),
                                                Length(min=4, max=100, message="Пароль должен быть от 4 до 100 символов")])
    submit = SubmitField("Регистрация")

class AddPostForm(FlaskForm):
    title = StringField("Название записи (от 4 до 300 символов): ", validators=[Length(min=4, max=300, message="Название записи должно быть от 4 до 300 символов")])
    url = StringField("URL записи (название латиницей от 4 до 20 символов): ", validators=[Length(min=4, max=20, message="Название записи должно быть от 4 до 20 символов")])
    text = TextAreaField("Текст записи (от 10 символов): ", validators=[Length(min=10, message="Текст записи должен быть от 10 символов")])
    submit = SubmitField("Добавить")

class AmendPostForm(FlaskForm):
    title = StringField("Название записи (от 4 до 300 символов): ", validators=[Length(min=4, max=300, message="Название записи должно быть от 4 до 300 символов")])
    text = TextAreaField("Текст записи (от 10 символов): ", validators=[Length(min=10, message="Текст записи должен быть от 10 символов")])
    hidden = BooleanField("Скрыть", default=False)
    delete = BooleanField("Удалить", default=False)
    submit = SubmitField("Изменить")


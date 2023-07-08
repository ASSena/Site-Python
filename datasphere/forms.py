from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import Email, EqualTo, DataRequired, Length, ValidationError
from datasphere.models import Usuario
from flask_login import current_user


class FormLogin(FlaskForm):
    email_login = StringField('E-mail', validators=[DataRequired(), Email()])
    senha_login = PasswordField('Senha', validators=[DataRequired(), Length(6, 20)])
    lembrar_dados = BooleanField('Salvar informação de login')
    botao_submit_login = SubmitField('Entrar')

class FormCriarConta(FlaskForm):
    username = StringField('Nome de usuário', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(6, 20)])
    confirmacao_senha = PasswordField('Confirme a senha', validators=[DataRequired(), EqualTo('senha')])
    botao_submit_criarconta = SubmitField('Criar conta')

    def validate_email(self, email):
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario:
            raise ValidationError('E-mail já cadastrado. Mude o e-mail ou faça login para continuar')

class FormEditar(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    foto_perfil = FileField('Mudar a foto de perfil', validators=[FileAllowed(['jpg', 'png'])])
    username = StringField('Nome de usuário', validators=[DataRequired()])
    botao_editar = SubmitField('Confirmar Edição')
    botao_excluir_foto = SubmitField('Excluir Foto De Perfil')
    curso_excel = BooleanField('Curso Excel Impressionador')
    curso_python = BooleanField('Curso Python Impressionador')
    curso_sql = BooleanField('Curso SQL Impressionador')
    curso_powerbi = BooleanField('Curso Power BI Impressionador')
    curso_javascript = BooleanField('Curso Java Script Impressionador')
    curso_word = BooleanField('Curso Word Impressionador')

    def validate_email(self, email):
        if email.data != current_user.email:
          usuario = Usuario.query.filter_by(email=email.data).first()
          if usuario:
              raise ValidationError('E-mail já cadastrado')

class FormPost(FlaskForm):
    titulo = StringField('Título do Post', validators=[DataRequired(), Length(2,140)])
    corpo = TextAreaField('Corpo do Post', validators=[DataRequired()])
    botao_submit = SubmitField('Criar Post')
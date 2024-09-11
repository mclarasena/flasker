from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, TextAreaField, IntegerField
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField
from flask_wtf.file import FileField, FileAllowed

##Criando o formulário de Pesquisa
class SearchForm(FlaskForm):
    searched = StringField("Pesquisa", validators=[DataRequired()])
    submit = SubmitField("Enviar")

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")

#Criando o posts do blog 
class PostForm(FlaskForm):
    title = StringField("Título", validators=[DataRequired()])
    #content = StringField("Conteúdo", validators=[DataRequired()], widget=TextArea())
    content = CKEditorField('Contéudo', validators=[DataRequired()])
    #author = StringField("Usuário")
    slug = StringField("Slug", validators=[DataRequired()])
    submit = SubmitField("Enviar", validators=[DataRequired()])

#Create a form class
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    username= StringField("Username", validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    about_author= TextAreaField("Sobre o Autor")
    password_hash = PasswordField('Password', validators=[DataRequired(), EqualTo('password_hash2', message='As senhas devem ser iguais')])
    password_hash2 = PasswordField('Confirmar sua senha', validators=[DataRequired()])
    profile_pic = FileField('Foto de perfil', validators=[
        FileAllowed(['jpg', 'png'], 'Somente imagens são permitidas!')
    ])
    
    submit = SubmitField('Enviar')
    
#Create a form class
class NamerForm(FlaskForm):
    name = StringField('Qual é o seu nome?', validators=[DataRequired()])
    submit = SubmitField('Enviar')

class PasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password_hash = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Enviar')

'''class RecipeForm(FlaskForm):
    title= StringField('Título', validators=[DataRequired()])
    ingredients= TextAreaField('Ingredientes', validators=[DataRequired()])
    instructions= TextAreaField('Instruções', validators=[DataRequired()])
    cooking_time= IntegerField('Tempo de Preparo (min)', validators=[DataRequired()])
    submit= SubmitField('Criar Receita')'''
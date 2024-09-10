from flask import Flask, render_template, flash, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy 
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from datetime import date
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from werkzeug.security import check_password_hash
from web_forms import LoginForm, PostForm, UserForm, NamerForm, PasswordForm, SearchForm
from flask_ckeditor import CKEditor
from werkzeug.utils import secure_filename
import uuid as uuid 
import os 


#Instância do Flask
app = Flask(__name__)
ckeditor = CKEditor(app)

#antigo sqlite db
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

#adicionar banco de dados/novo mysql db
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/users'

#chave 
app.config['SECRET_KEY'] = "my super secret"

UPLOAD_FOLDER = 'static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)

# Inicializar o Flask-Migrate
migrate = Migrate(app, db)  # Configuração correta do Migrate

login_manager= LoginManager()
login_manager.init_app(app)
login_manager.login_view= 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

#Passar para o navbar
@app.context_processor
def base():
    form= SearchForm()
    return dict(form=form)

#Página do administrador 
@app.route('/admin')
@login_required
def admin():
    id = current_user.id 
    #restringindo acesso
    if id == 9:
        return render_template('admin.html')
    
    else: 
        flash('Não é possível acessar essa página')
        return redirect(url_for('dashboard'))

    return render_template("admin.html")


#Criar uma função de pesquisar
@app.route('/search', methods=["POST"])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        searched = form.searched.data
        # Consultar o banco de dados para encontrar posts que correspondam à pesquisa
        posts = Posts.query.filter(Posts.content.like('%' + searched + '%')).order_by(Posts.title).all()

        return render_template("search.html", form=form, searched=searched, posts=posts)
    
    return redirect(url_for('index'))

#Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    form= LoginForm()
    if form.validate_on_submit():
        user= Users.query.filter_by(username= form.username.data).first()
        if user: 
            #Check hash
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash('Login feito com sucesso')
                return redirect(url_for('dashboard'))
            else:
                flash('Senha incorreta')
        else:
            flash('Esse usuário não existe')

    return render_template('login.html', form=form)

#Logout
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('Você foi deslogado')
    return redirect(url_for('login'))

#Dashboard 
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form=UserForm()
    id = current_user.id
    name_to_update=Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name= request.form['name']
        name_to_update.email= request.form['email']
        name_to_update.username= request.form['username']
        name_to_update.about_author= request.form['about_author']
        name_to_update.profile_pic= request.files['profile_pic']
        #Pegar o nome da imagem
        pic_filename = secure_filename(name_to_update.profile_pic.filename)
        #Set UUID
        pic_name = str(uuid.uuid1()) + "_" + pic_filename
        #Salvar imagem 
        saver = request.files['profile_pic']
    
        #Mudar para string para salvar no banco de dados
        name_to_update.profile_pic = pic_name
       
        try:
            db.session.commit()
            saver.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
            flash("Dados do usuário atualizados com sucesso!")
            return render_template("dashboard.html",
                                   form=form,
                                   name_to_update=name_to_update)
        except:
            flash("Erro... Tente de novo")
            return render_template("dashboard.html",
                                   form=form,
                                   name_to_update=name_to_update)
    else: 
        return render_template("dashboard.html",
                                   form=form,
                                   name_to_update=name_to_update,
                                   id = id)
    
    return render_template('dashboard.html')

@app.route('/posts/delete/<int:id>')
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)

    if post_to_delete.poster is None:
        flash('O post não tem um autor associado. Não é possível deletar.')
        return redirect(url_for('posts'))

    # Verifica se o usuário atual é o dono do post
    if current_user.id == post_to_delete.poster.id:
        try:
            db.session.delete(post_to_delete)
            db.session.commit()

            flash('Post deletado com sucesso.')
        except:
            flash('Problema ao deletar o post... Tente de novo.')

    else:
        flash('Você não está autorizado a deletar esse post.')

    # Pegar os posts do banco de dados
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template("posts.html", posts=posts)

@app.route('/posts')
def posts():
    #pegar os posts do banco de dados 
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template("posts.html", posts=posts)

@app.route('/posts/<int:id>')
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template('post.html', post=post)

@app.route('/posts/edit/<int:id>', methods= ['GET', 'POST'])
@login_required
def edit_post(id):
    post= Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title= form.title.data
        #post.author= form.author.data
        post.slug= form.slug.data
        post.content= form.content.data
        #update db 
        db.session.add(post)
        db.session.commit()
        flash('Post atualizado!')
        return redirect(url_for('post', id=post.id))
    
    if current_user.id == post.poster_id:
        form.title.data= post.title
        #form.author.data= post.author
        form.slug.data= post.slug
        form.content.data= post.content
        return render_template('edit_post.html', form=form)
    else: 
        flash('Você não está autorizado a editar esse post')
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template("posts.html", posts=posts)

#Adicionar Página de Posts 
@app.route('/adicionar-post', methods=['GET', 'POST'])
@login_required
def add_post():

    form = PostForm()

    if form.validate_on_submit():
        poster= current_user.id
        post = Posts(title=form.title.data, content=form.content.data, poster_id=poster, slug=form.slug.data)
        # Limpar o formulário
        form.title.data = ''
        form.content.data = ''
        #form.author.data = ''
        form.slug.data = ''

        # Adicionando post ao banco de dados
        db.session.add(post)
        db.session.commit()

        flash("Post publicado com sucesso")

    return render_template('add_post.html', form=form)

#JSON
@app.route('/date')
def get_current_date():
    return {"Date": date.today()}
    
#atualizar o banco de registros 
@app.route('/delete/<int:id>')
@login_required
def delete(id):
    if id == current_user.id:

        user_to_delete = Users.query.get_or_404(id)
        name = None
        form = UserForm()

        try:
            db.session.delete(user_to_delete)
            db.session.commit()
            flash("Usuario deletado com sucesso!")

            our_users= Users.query.order_by(Users.date_added)
            return render_template('add_user.html', form=form, name=name, our_users=our_users)

        except: 
            flash('Erro, tente novamente')
            return render_template('add_user.html', form=form, name=name, our_users=our_users)

    else:
        flash('Vocẽ não pode deletar esse usuário!')
        return redirect(url_for('dashboard'))
    
#atualizar o banco de registros 
@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    form=UserForm()
    name_to_update=Users.query.get_or_404(id)
    
    if request.method == "POST" and form.validate_on_submit:
        
        name_to_update.name= request.form['name']
        name_to_update.email= request.form['email']
        name_to_update.username= request.form['username']
        try:
            db.session.commit()
            flash("Dados do usuário atualizados com sucesso!")
            return render_template("update.html",
                                   form=form,
                                   name_to_update=name_to_update)
        except:
            flash("Erro... Tente de novo")
            return render_template("update.html",
                                   form=form,
                                   name_to_update=name_to_update)
    else: 
        return render_template("update.html",
                                   form=form,
                                   name_to_update=name_to_update,
                                   id = id)


@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            # criptografar a senha 
            hashed_pw= generate_password_hash(form.password_hash.data, "pbkdf2:sha256")
            user= Users(username=form.username.data, name=form.name.data, email=form.email.data, password_hash= hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ""
        form.username.data = ""
        form.email.data = ""
        form.password_hash.data= ''

        flash('Enviado Com Sucesso!')
    our_users= Users.query.order_by(Users.date_added)
    return render_template('add_user.html', form=form, name=name, our_users=our_users)


# Define a rota para a página inicial
@app.route('/')
#def index():
#    return "<h1>Hello World!</h1>"
def index():
    first_name= "John"
    stuff = "This is bold text"

    favorite_pizza= ["calabresa", "cheese", "portugueesa",  41]
    return render_template("index.html", first_name=first_name, stuff=stuff, favorite_pizza=favorite_pizza)

# Define a rota para usuários dinâmicos
@app.route('/user/<name>')

def user(name):
    return render_template("user.html", user_name=name )

#Páginas de erro

#Invalid URL
@app.errorhandler(404)

def page_not_found(e):
    return render_template("404.html"), 404

#Internal Server Error 
@app.errorhandler(500)

def page_not_found(e):
    return render_template("500.html"), 500

@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
    email = None
    password= None 
    pw_to_check= None
    passed = None
    form = PasswordForm()


    
    if form.validate_on_submit():
        email=form.email.data
        password =form.password_hash.data
        
        form.email.data= ""
        form.password_hash.data = ""

        pw_to_check= Users.query.filter_by(email=email).first()

        passed = check_password_hash(pw_to_check.password_hash, password)

        flash('Enviado Com Sucesso!')

    return render_template('test_pw.html', email=email, password=password, form=form, pw_to_check=pw_to_check, passed=passed)



#Criar uma página de nome 
@app.route('/name', methods=['GET', 'POST'])
def name():
    name  = None
    form = NamerForm()
    if form.validate_on_submit():
        name=form.name.data
        form.name.data= ""
        flash('Enviado Com Sucesso!')
    return render_template('name.html', name=name, form=form)


#Blog Post 
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    title = db.Column(db.String(255))
    content= db.Column(db.Text)
    #author= db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default= datetime.utcnow)
    slug= db.Column(db.String(255))
    #foreign key
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable= False, unique=True)
    name = db.Column(db.String(200), nullable= False)
    email = db.Column(db.String(120), nullable= False, unique =True)
    about_author= db.Column(db.Text(500), nullable= True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    profile_pic = db.Column(db.String(255), nullable=True)
    #Senha 
    password_hash = db.Column(db.String(128))
    #usuarios podem ter varios pots
    posts = db.relationship('Posts', backref='poster')

    
    @property
    def password(self):
        raise AttributeError('password is not a readable atribute')
    
    @password.setter
    def password(self, password):
        self.password_hash= generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    #Criar uma string
    def __repr__(self):
        return '<Name %r>' % self.name


if __name__ == "__main__":
    app.run(debug=True)



from flask import Flask, render_template


app = Flask(__name__)

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

#Criar uma página de nome 
#@app.route('/name', methods=['GET', 'POST'])

if __name__ == "__main__":
    app.run(debug=True)



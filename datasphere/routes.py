from flask import render_template, url_for, request, flash, redirect, abort
from datasphere.forms import FormLogin, FormCriarConta, FormEditar, FormPost
from datasphere import app, database, bcrypt
from datasphere.models import Usuario,Post
from flask_login import login_user, logout_user, current_user, login_required
import secrets
import os
from PIL import Image, ImageDraw


@app.route('/')
def home():
    posts = Post.query.order_by(Post.id.desc())
    return render_template('home.html', posts=posts)


@app.route('/contato')
def contato():
    return render_template('contato.html')


@app.route('/usuarios')
@login_required
def usuarios():

    lista_usuarios = []

    for usuario in Usuario.query.all():

        if usuario:
            lista_usuarios.append(usuario)

    return render_template('usuarios.html', lista_usuarios=lista_usuarios)


@app.route('/login', methods=['GET', 'POST'])
def login():

    form_login = FormLogin()
    form_criarconta = FormCriarConta()

    if form_criarconta.validate_on_submit() and 'botao_submit_criarconta' in request.form:
        senha_cript = bcrypt.generate_password_hash(form_criarconta.senha.data)
        usuario = Usuario(email=request.form['email'], username=request.form['username'], senha=senha_cript)
        database.session.add(usuario)
        database.session.commit()
        flash(f'Conta criada para o e-mail: {form_criarconta.email.data}', 'alert-success')

        return redirect(url_for('home'))

    if form_login.validate_on_submit() and 'botao_submit_login' in request.form:
        usuario = Usuario.query.filter_by(email=form_login.email_login.data).first()

        if usuario and bcrypt.check_password_hash(usuario.senha, form_login.senha_login.data).decode('UTF-8'):
            login_user(usuario, remember=form_login.lembrar_dados.data)
            flash(f'Login feito com sucesso no e-mail: {form_login.email_login.data}', 'alert-success')
            par_next = request.args.get('next')

            if par_next:

                return redirect(par_next)

            else:

                return redirect(url_for('home'))

        else:
            flash('E-mail ou senha inválidos', 'alert-danger')

    return render_template('teste.html', form_login=form_login, form_criarconta=form_criarconta)


@app.route('/Logout')
@login_required
def logout():
    logout_user()
    flash(f'Logout feito com sucesso', 'alert-success')
    return redirect(url_for('home'))


@app.route('/post/criar', methods=['GET','POST'])
@login_required
def criar_post():
    form = FormPost()

    if form.validate_on_submit():
        post = Post(titulo=form.titulo.data, corpo=form.corpo.data, autor=current_user)
        database.session.add(post)
        database.session.commit()
        flash('Post Criado com Sucesso', 'alert-success')

        return redirect(url_for('home'))

    return render_template('post.html', form=form)


@app.route('/post/<post_id>',  methods=['GET','POST'])
@login_required
def editar_post(post_id):
    post = Post.query.get(post_id)

    if post.autor == current_user:
        form = FormPost()

        if request.method == "GET":
            form.titulo.data = post.titulo
            form.corpo.data = post.corpo

        elif form.validate_on_submit():
            post.titulo = form.titulo.data
            post.corpo = form.corpo.data
            database.session.commit()
            flash('Post atualizado com sucesso', 'alert alert-success')

            return redirect(url_for('home'))

    else:
        form = None

    return render_template('editar_post.html', post=post,form=form)


@app.route('/post/<post_id>/exluir',  methods=['GET','POST'])
@login_required
def excluir_post(post_id):

    post = Post.query.get(post_id)

    if post.autor == current_user:
        database.session.delete(post)
        database.session.commit()
        flash('Post excluído com sucesso', 'alert-danger')

        return redirect(url_for('home'))

    else:
        abort(403)


@app.route('/perfil')
@login_required
def perfil():

    form = FormEditar()
    lista = current_user.cursos.split(';')

    if lista == [''] or lista == ['Não Informado']:
        qtd_cursos = 0
        lista = ['Curso Não Informado']

    else:
        qtd_cursos = len(lista)
    foto_perfil = url_for('static', filename=f'fotos_perfil/{current_user.foto_perfil}')

    return render_template('perfil.html', foto_perfil=foto_perfil, qtd_cursos=qtd_cursos, lista=lista,form=form)


#Funçoes à parte para edição de imagem e contabilização dos cursos

def apply_circle_mask(image):

    # Cria uma máscara circular

    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, image.size[0], image.size[1]), fill=255)

    # Aplica a máscara à imagem
    result = Image.new("RGBA", image.size)
    result.paste(image, (0, 0), mask=mask)

    return result

def imagem_modificada(imagem):
    codigo = secrets.token_hex(8)
    nome, extensao = os.path.splitext(imagem.filename)
    nome_imagemCod = nome + codigo + '.png'
    caminho_completo = os.path.join(app.root_path, 'static', 'fotos_perfil', nome_imagemCod)
    tamanho = (400, 400)
    im = Image.open(imagem)

    # Converte a imagem para o modo RGB se for JPEG

    if im.mode != 'RGB':
        im = im.convert('RGB')

    im_resized = im.resize(tamanho)
    im_circular = apply_circle_mask(im_resized)
    im_circular.save(caminho_completo)

    return nome_imagemCod

def adicionar_cursos(form):
    lista_cursos = []

    for campo in form:

        if campo.data:

            if 'curso_' in campo.name:
                lista_cursos.append(campo.label.text)

    return ';'.join(lista_cursos)

@app.route('/perfil/editar', methods=['GET', 'POST'])
@login_required
def perfil_editar():
    form = FormEditar()

    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data

        if form.foto_perfil.data:
            nome_imagem = imagem_modificada(form.foto_perfil.data)
            current_user.foto_perfil = nome_imagem

        elif 'botao_excluir_foto' in request.form:
            current_user.foto_perfil = 'default.jpg'
        current_user.cursos = adicionar_cursos(form)
        database.session.commit()
        flash('Perfil atualizado com sucesso', 'alert-success')

        return redirect(url_for('perfil'))

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    foto_perfil = url_for('static', filename=f'fotos_perfil/{current_user.foto_perfil}')
    return render_template('atualizar_perfil.html', foto_perfil=foto_perfil, form=form)


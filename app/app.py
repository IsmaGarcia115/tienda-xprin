from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import os

try:
    from forms import ProductoForm, LoginForm, RegistroForm
except ImportError:
    from app.forms import ProductoForm, LoginForm, RegistroForm

# Configuración de la aplicación Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'ElArzobispoDeConstantiplaSufreDeHipopotomonstrosesquipedaliofobiaDebidoASuAcidoDesoxirribonucleico'
csrf = CSRFProtect(app)
# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Debes iniciar sesión para acceder a esta página.'
login_manager.login_message_category = 'danger'

# Configuración de MongoDB
# Usa variable de entorno o valor por defecto para Docker
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://isma:isma@localhost:27017/tienda?authSource=admin')
client = MongoClient(MONGO_URI)
db = client['tienda']
productos_collection = db['productos']
usuarios_collection = db['usuarios']


# Clase User para Flask-Login
class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.nombre = user_data['nombre']
        self.email = user_data['email']


@login_manager.user_loader
def load_user(user_id):
    user_data = usuarios_collection.find_one({'_id': ObjectId(user_id)})
    if user_data:
        return User(user_data)
    return None

# FUNCIONES AUXILIARES
def cargar_opciones_formulario(form):
    categorias = productos_collection.distinct('categoria')
    subcategorias = productos_collection.distinct('subcategoria')
    marcas = productos_collection.distinct('marca')
    
    form.categoria.choices = [('', 'Seleccione una categoría')] + [(c, c) for c in categorias]
    form.subcategoria.choices = [('', 'Seleccione una subcategoría')] + [(s, s) for s in subcategorias]
    form.marca.choices = [('', 'Seleccione una marca')] + [(m, m) for m in marcas]
    
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    # Si ya está logueado, redirigir al inicio
    if current_user.is_authenticated:
        return redirect(url_for('inicio'))
    
    form = RegistroForm()
    
    if form.validate_on_submit():
        # Verificar si el email ya existe
        usuario_existente = usuarios_collection.find_one({'email': form.email.data})
        
        if usuario_existente:
            flash('Este email ya está registrado', 'danger')
            return render_template('registro.html', form=form)
        
        # Crear nuevo usuario
        nuevo_usuario = {
            'nombre': form.nombre.data,
            'email': form.email.data,
            'password': generate_password_hash(form.password.data)
        }
        
        usuarios_collection.insert_one(nuevo_usuario)
        flash('Registro exitoso. Ya puedes iniciar sesión.', 'success')
        return redirect(url_for('login'))
    
    return render_template('registro.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Si ya está logueado, redirigir al inicio
    if current_user.is_authenticated:
        return redirect(url_for('inicio'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        # Buscar usuario por email
        usuario = usuarios_collection.find_one({'email': form.email.data})
        
        if usuario and check_password_hash(usuario['password'], form.password.data):
            user = User(usuario)
            login_user(user)
            flash(f'¡Bienvenido, {user.nombre}!', 'success')
            
            # Redirigir a la página que intentaba acceder o al inicio
            next_page = request.args.get('next')
            return redirect(next_page or url_for('inicio'))
        else:
            flash('Email o contraseña incorrectos', 'danger')
    
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente', 'success')
    return redirect(url_for('inicio'))

@app.route('/')
def inicio():
    # Contar productos totales
    total_productos = productos_collection.count_documents({})
    
    # Contar por categoría
    total_bobinas = productos_collection.count_documents({'categoria': 'Bobinas'})
    total_tintas = productos_collection.count_documents({'categoria': 'Tintas'})
    total_polvo = productos_collection.count_documents({'categoria': 'Polvo'})
    
    # Productos con stock bajo (menos de 40 unidades)
    stock_bajo = productos_collection.count_documents({'stock': {'$lt': 40}})
    
    return render_template('inicio.html', 
                           total=total_productos,
                           bobinas=total_bobinas,
                           tintas=total_tintas,
                           polvo=total_polvo,
                           stock_bajo=stock_bajo)
    
@app.route('/catalogo')
def catalogo():
    # Obtener todos los productos
    productos = list(productos_collection.find())
    
    return render_template('catalogo.html', productos=productos)

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = ProductoForm()
    cargar_opciones_formulario(form)
    
    if form.validate_on_submit():
        nuevo_producto = {
            'nombre': form.nombre.data,
            'categoria': form.categoria.data,
            'subcategoria': form.subcategoria.data,
            'marca': form.marca.data,
            'descripcion': form.descripcion.data,
            'precio': float(form.precio.data),
            'stock': int(form.stock.data),
            'activo': form.activo.data
        }
        
        productos_collection.insert_one(nuevo_producto)
        flash('Producto añadido correctamente', 'success')
        return redirect(url_for('catalogo'))
    
    return render_template('add.html', form=form)
@app.route('/update/<id>', methods=['GET', 'POST'])
@login_required
def update(id):
    # Buscar el producto por ID
    producto = productos_collection.find_one({'_id': ObjectId(id)})

    form = ProductoForm()
    cargar_opciones_formulario(form)
    
    if form.validate_on_submit():
        # Actualizar el producto
        productos_collection.update_one(
            {'_id': ObjectId(id)},
            {'$set': {
                'nombre': form.nombre.data,
                'categoria': form.categoria.data,
                'subcategoria': form.subcategoria.data,
                'marca': form.marca.data,
                'descripcion': form.descripcion.data,
                'precio': float(form.precio.data),
                'stock': int(form.stock.data),
                'activo': form.activo.data
            }}
        )
        flash('Producto actualizado correctamente', 'success')
        return redirect(url_for('catalogo'))
    
   
    if request.method == 'GET':
        form.nombre.data = producto.get('nombre', '')
        form.categoria.data = producto.get('categoria', '')
        form.subcategoria.data = producto.get('subcategoria', '')
        form.marca.data = producto.get('marca', '')
        form.descripcion.data = producto.get('descripcion', '')
        form.precio.data = producto.get('precio', 0)
        form.stock.data = producto.get('stock', 0)
        form.activo.data = producto.get('activo', True)
    
    return render_template('update.html', form=form, producto=producto)

@app.route('/delete/<id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    # Buscar el producto
    producto = productos_collection.find_one({'_id': ObjectId(id)})
    
    if not producto:
        flash('Producto no encontrado', 'danger')
        return redirect(url_for('catalogo'))
    
    if request.method == 'POST':
        # Eliminar el producto
        productos_collection.delete_one({'_id': ObjectId(id)})
        flash('Producto eliminado correctamente', 'success')
        return redirect(url_for('catalogo'))
    
    # Si es GET, mostrar confirmación
    return render_template('delete.html', producto=producto)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
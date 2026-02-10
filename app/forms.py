# type: ignore
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DecimalField, IntegerField, SelectField, BooleanField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, Email, EqualTo
 

class ProductoForm(FlaskForm):
    nombre = StringField('Nombre del Producto', validators=[
        DataRequired(),Length(min=3, max=100)
    ])
    
    # Choices vacías - se rellenarán dinámicamente
    categoria = SelectField('Categoría', choices=[], validators=[
        DataRequired()
    ])
    
    subcategoria = SelectField('Subcategoría', choices=[], validators=[
        DataRequired()
    ])
    
    marca = SelectField('Marca', choices=[], validators=[
        DataRequired()
    ])
    
    descripcion = TextAreaField('Descripción', validators=[
        Optional(),
        Length(max=500)
    ])
    
    precio = DecimalField('Precio (€)', validators=[
        DataRequired(),
        NumberRange(min=0.01)
    ])
    
    stock = IntegerField('Stock', validators=[
        DataRequired(),
        NumberRange(min=0)
    ])
    
    activo = BooleanField('Producto Activo', default=True)
    
    submit = SubmitField('Guardar Producto')
    
    
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(message='El email es obligatorio'),
        Email(message='Introduce un email válido')
    ])
    
    password = PasswordField('Contraseña', validators=[
        DataRequired(message='La contraseña es obligatoria')
    ])
    
    submit = SubmitField('Iniciar Sesión')


class RegistroForm(FlaskForm):
    nombre = StringField('Nombre', validators=[
        DataRequired(message='El nombre es obligatorio'),
        Length(min=2, max=50, message='El nombre debe tener entre 2 y 50 caracteres')
    ])
    
    email = StringField('Email', validators=[
        DataRequired(message='El email es obligatorio'),
        Email(message='Introduce un email válido')
    ])
    
    password = PasswordField('Contraseña', validators=[
        DataRequired(message='La contraseña es obligatoria'),
        Length(min=6, message='La contraseña debe tener al menos 6 caracteres')
    ])
    
    confirmar_password = PasswordField('Confirmar Contraseña', validators=[
        DataRequired(message='Confirma la contraseña'),
        EqualTo('password', message='Las contraseñas no coinciden')
    ])
    
    submit = SubmitField('Registrarse')
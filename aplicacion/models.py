from django.db import models
import logging
# Create your models here.
from django.db import models
from django.db.models.signals import post_save, pre_delete, post_delete
from django.dispatch import receiver
from .choices import sexos, Estado_civil, vivienda, parentesco, NACIONALIDAD_CHOICES
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.db import transaction
from django.core.exceptions import ValidationError


logger = logging.getLogger(__name__)


class Profesion(models.Model):
    nombre_profesion = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.nombre_profesion}"



    class Meta:
        db_table = 'Profesion'

class Nivel_Educ(models.Model):
    nombre_Nivel = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.nombre_Nivel}"

    class Meta:
        db_table = 'Nivel_educ'


class Bloque(models.Model):
    numero_bloque = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.numero_bloque}"

    class Meta:
        db_table = 'Bloque'

class Calle(models.Model):
    numero_calle = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.numero_calle}"

    class Meta:
        db_table = 'Calle'

class Familia(models.Model):
    idfamilia = models.AutoField(primary_key=True)
    jefe_de_familia = models.OneToOneField('Persona', on_delete=models.CASCADE, related_name='familia_jefe', null=True, blank=True)

    def __str__(self):
        if self.jefe_de_familia:
            return f" {self.jefe_de_familia.cedula} {self.jefe_de_familia.P_nombre} {self.jefe_de_familia.P_apellido} Casa: {self.jefe_de_familia.num_casa} Calle: {self.jefe_de_familia.num_calle} Bloque: {self.jefe_de_familia.num_bloque} "
        else:
            return "No hay jefe de familia registrado."
        
    def cantidad_miembros(self):
        return self.familia_personas.count()
        
    
    
    class Meta:
        db_table = 'Familia'



class Persona(models.Model):
    idPersona = models.AutoField(primary_key=True)
    nacionalidad = models.CharField(max_length=50, choices=NACIONALIDAD_CHOICES, default='V')
    posee_cedula = models.BooleanField(default=True)
    cedula = models.CharField(max_length=12, blank=True, null=True)
    pasaporte = models.CharField(max_length=12, blank=True, null=True)
    P_nombre = models.CharField(max_length=100)
    P_apellido = models.CharField(max_length=100)
    S_nombre = models.CharField(max_length=100,null=True)
    S_apellido = models.CharField(max_length=100,null=True)
    fecha_nacimiento = models.DateField(null=True)
    sexo = models.CharField(max_length=1, choices=sexos, default='F')
    parentesco = models.CharField(max_length=20,choices=parentesco, default='n', blank=True)
    estado_civil = models.CharField(max_length=1, choices=Estado_civil, default='s')
    nivel_educ = models.ForeignKey(Nivel_Educ, on_delete=models.SET_NULL, null=True, blank=True)
    profesion = models.ForeignKey(Profesion, on_delete=models.SET_NULL, null=True, blank=True)
    trabaja = models.BooleanField(default=False)
    descripcion_trabajo = models.TextField(blank=True)
    ocupacion = models.BooleanField()
    descripcion_ocupacion = models.TextField(blank=True)
    correo = models.EmailField(blank=False, null=True)
    celular= models.CharField(max_length=15, null=True)
    telefono = models.CharField(max_length=15, null=True)
    discapacidad = models.BooleanField()
    descripcion_discapacidad = models.TextField(blank=True)
    tipo_vivienda = models.CharField(max_length=21, choices=vivienda, default='casa_unifamiliar')
    num_casa = models.IntegerField()
    num_calle = models.ForeignKey(Calle, on_delete=models.SET_NULL, null=True, blank=True)
    num_bloque = models.ForeignKey(Bloque, on_delete=models.SET_NULL, null=True, blank=True)
    jefe_familia = models.IntegerField(choices=[(1, "Sí"), (0, "No")], default=0)
    carga_familiar = models.IntegerField(choices=[(1, "Sí"), (0, "No")], default=0)
    observaciones = models.TextField(blank=True)
    familia_r = models.ForeignKey(Familia, on_delete=models.CASCADE, null=True, blank=True, related_name='familia_personas')
    

    def __str__(self):
        return f"{self.P_nombre} {self.P_apellido}"


    class Meta:
        db_table = 'Persona'



class Banco(models.Model):
    codigo = models.CharField(max_length=45, null=True)
    nombre = models.CharField(max_length=100, null=True, blank=True)
    
    def __str__(self):
        return f"{self.codigo} {self.nombre} "
    
    class Meta:
        db_table = 'Banco'
   
class Pagos(models.Model):
    idPagos = models.AutoField(primary_key=True)
    fecha = models.DateField(null=True)
    jefe_de_familia = models.ForeignKey(Familia, on_delete=models.CASCADE)
    banco_receptor = models.ForeignKey(Banco, on_delete=models.CASCADE, related_name='pagos_receptor', null=True, blank=True)
    banco_emisor = models.ForeignKey(Banco, on_delete=models.CASCADE, related_name='pagos_emisor', null=True, blank=True)
    numero_referencia = models.CharField(max_length=45)
    comprobante_pago = models.FileField(upload_to='comprobantes/', null=True, blank=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    observaciones = models.TextField(blank=True)

    
    

    class Meta:
        db_table = 'pagos'


# models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission


class CustomUser(AbstractUser):
    bio = models.TextField(blank=True)
    cedula = models.CharField(max_length=10, blank=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True, related_name='custom_users_groups')
    telefono = models.CharField(max_length=15, blank=True)  # Agregado el campo de teléfono
    user_permissions = models.ManyToManyField(Permission, blank=True, related_name='custom_users_permissions')
    custom_user_groups = models.ManyToManyField(Group, blank=True, related_name='custom_user_users')  # Nuevo campo con related_name único


    # Agrega related_name para evitar conflictos en los accesores inversos
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        related_query_name='customuser',
        blank=True,
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',
        related_query_name='customuser',
        blank=True,
    )

    def __str__(self):
        return self.username


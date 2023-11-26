from django import forms
from .models import Familia, Persona, Banco, Pagos, Bloque, Profesion, Nivel_Educ, Calle
from django.urls import reverse
from io import BytesIO
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.shortcuts import get_object_or_404
from django.db.models import Count
from .choices import parentesco




class FamiliaForm(forms.ModelForm):
    class Meta:
        model = Familia
        fields = '__all__'




class PersonaForm(forms.ModelForm):
    familia_r = forms.ModelChoiceField(
        queryset=Familia.objects.filter(jefe_de_familia__isnull=False),  # Filtra las familias con jefe de familia
        required=False,
        widget=forms.Select(attrs={'class': 'select2'})
    )

    discapacidad = forms.BooleanField(
        required=False,
        widget=forms.RadioSelect(choices=((True, 'Sí'), (False, 'No'))),
        initial=False
    )
    
    descripcion_discapacidad = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'style': 'display: none;'}),
        label='Descripción Discapacidad'
    )

    ocupacion = forms.BooleanField(
        required=False,
        widget=forms.RadioSelect(choices=((True, 'Sí'), (False, 'No'))),
        initial=False
    )
    
    descripcion_ocupacion = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'style': 'display: none;'}),
        label='Descripción Ocupación'
    )
    
    SINO_CHOICES = (
        (True, 'Sí'),
        (False, 'No'),
    )
    
    trabaja = forms.ChoiceField(
        choices=SINO_CHOICES,
        widget=forms.RadioSelect,
        required=True,
        initial=False  # Cambiado a False
    )

    jefe_familia = forms.ChoiceField(
        choices=[(0, "No"), (1, "Sí")],
        initial=0,  # Establece "No" como valor predeterminado
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    carga_familiar = forms.ChoiceField(
        choices=[(0, "No"), (1, "Sí")],
        initial=0,  # Establece "No" como valor predeterminado
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    num_calle = forms.ModelChoiceField(
        queryset=Calle.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True  # Este campo es obligatorio
    )

    num_bloque = forms.ModelChoiceField(
        queryset=Bloque.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True  # Este campo es obligatorio
    )

    parentesco = forms.ChoiceField(
    choices=parentesco,  # Agrega esta línea
    widget=forms.Select(attrs={'class': 'form-control'}),
    required=False,
    )


    cedula = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control custom-input'}), required=False)

    def clean(self):
        cleaned_data = super().clean()
        carga_familiar = cleaned_data.get('carga_familiar')
        familia_r = cleaned_data.get('familia_r')
        parentesco = cleaned_data.get('parentesco')

        if carga_familiar == 1:
            if not familia_r:
                self.add_error('familia_r', 'Si es carga familiar, debes seleccionar una familia en "Familia"')
            if not parentesco:
                self.add_error('parentesco', 'Si es carga familiar, debes especificar un parentesco')


        print("Carga familiar:", carga_familiar)
        print("Familia:", familia_r)
        print("Parentesco:", parentesco)

        return cleaned_data
    
    
    class Meta:
        model = Persona
        fields = '__all__'
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
            # Otros widgets para otros campos si es necesario
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

                # Para el campo 'profesion'
        self.fields['profesion'].queryset = Profesion.objects.all()
        self.fields['profesion'].empty_label = None

        # Para el campo 'nivel_educativo'
        self.fields['nivel_educ'].queryset = Nivel_Educ.objects.all()
        self.fields['nivel_educ'].empty_label = None


        # Verificar si la instancia actual está editando una persona existente
        if self.instance.pk and self.instance.familia_r and self.instance.familia_r.jefe_de_familia:
            # Si está editando y la persona tiene una familia asociada, incluimos la familia actual de la persona
            familia_actual = self.instance.familia_r
            familias_con_menos_de_7 = Familia.objects.annotate(num_personas=Count('familia_personas')).filter(num_personas__lt=7) | Familia.objects.filter(idfamilia=familia_actual.idfamilia)
        else:
            # Si está creando una nueva persona o la persona no tiene una familia asociada, simplemente contamos todas las familias
            familias_con_menos_de_7 = Familia.objects.annotate(num_personas=Count('familia_personas')).filter(num_personas__lt=7)

        # Actualizar el queryset del campo familia_r
        self.fields['familia_r'].queryset = familias_con_menos_de_7





        

class PagosForm(forms.ModelForm):
    jefe_de_familia = forms.ModelChoiceField(
        queryset=Familia.objects.filter(jefe_de_familia__isnull=False),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control select2 jefe-familia-select', 'style': 'height: 50px;'}),
    )

    banco_receptor = forms.ModelChoiceField(
        queryset=Banco.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control border-blue', 'style': 'height: 50px;'}),
        required=True
    )

    banco_emisor = forms.ModelChoiceField(
        queryset=Banco.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control border-blue', 'style': 'height: 50px;'}),
        required=True
    )

    numero_referencia = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control border-blue'}),
        required=True  # Este campo es obligatorio
    )

    def clean_numero_referencia(self):
        numero_referencia = self.cleaned_data['numero_referencia']
        if not numero_referencia.isdigit() or len(numero_referencia) != 6:
            raise forms.ValidationError("Solo se permiten números (6).")
        return numero_referencia

    monto = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control border-blue'}),
        required=True  # Este campo es obligatorio
    )

    comprobante_pago = forms.FileField(
        required=False  # Este campo no es obligatorio
    )

    class Meta:
        model = Pagos
        fields = ['fecha', 'jefe_de_familia', 'banco_receptor', 'banco_emisor', 'numero_referencia', 'monto', 'comprobante_pago', 'observaciones']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control border-blue'}),
            # Otros widgets para otros campos si es necesario
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Puedes agregar más personalización si es necesario
        self.fields['fecha'].widget.attrs.update({'class': 'form-control border-blue'})  # Agrega clases al campo 'fecha'
        self.fields['numero_referencia'].widget.attrs.update({'class': 'form-control border-blue'})  # Agrega clases al campo 'numero_referencia'
        self.fields['monto'].widget.attrs.update({'class': 'form-control border-blue'})  # Agrega clases al campo 'monto'
        self.fields['comprobante_pago'].widget.attrs.update({'class': 'form-control border-blue'})  # Agrega clases al campo 'comprobante_pago'
        self.fields['observaciones'].widget.attrs.update({'class': 'form-control border-blue'})  # Agrega clases al campo 'observaciones'



class BancoForm(forms.ModelForm):
    class Meta:
        model = Banco
        fields = '__all__'


class ReportePagosForm(forms.Form):
    bloque_choices = [(bloque.id, str(bloque)) for bloque in Bloque.objects.all()]
    bloque_choices.append(('all', 'Todos los Bloques'))
    bloque = forms.ChoiceField(choices=bloque_choices, required=False, label="Bloque")
    mes_anio = forms.CharField(required=False, label="Mes y Año")


class ProfesionForm(forms.ModelForm):
    class Meta:
        model = Profesion
        fields = ['nombre_profesion']

    nombre_profesion = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control my-custom-input'})
    )


class NivelEducForm(forms.ModelForm):
    class Meta:
        model = Nivel_Educ
        fields = ['nombre_Nivel']

    nombre_Nivel = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control my-custom-input'})
    )

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre_Nivel']
        if not nombre.isalpha():
            raise forms.ValidationError("Solo se permiten letras y espacios en blanco.")
        return nombre



class BloqueForm(forms.ModelForm):
    class Meta:
        model = Bloque
        fields = ['numero_bloque']
        widgets = {
            'numero_bloque': forms.TextInput(attrs={'class': 'form-control'}),
        }


class CalleForm(forms.ModelForm):
    class Meta:
        model = Calle
        fields = ['numero_calle']

class CustomUserCreationForm(UserCreationForm):
    group = forms.ModelChoiceField(queryset=Group.objects.all(), empty_label=None, label='Grupo')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'group']



class RegistroForm(forms.ModelForm):
    class Meta:
        model = Persona
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        carga_familiar = cleaned_data.get('carga_familiar')
        familia_r = cleaned_data.get('familia_r')
        parentesco = cleaned_data.get('parentesco')

        if carga_familiar == 1:
            if not familia_r:
                self.add_error('familia_r', 'Si es carga familiar, debes seleccionar una familia en "Familia"')
            if not parentesco:
                self.add_error('parentesco', 'Si es carga familiar, debes especificar un parentesco')


        print("Carga familiar:", carga_familiar)
        print("Familia:", familia_r)
        print("Parentesco:", parentesco)

        return cleaned_data
    
    discapacidad = forms.BooleanField(
    required=False,
    widget=forms.RadioSelect(choices=((True, 'Sí'), (False, 'No'))),
    initial=False
    )
    
    descripcion_discapacidad = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'style': 'display: none;'}),
        label='Descripción Discapacidad'
    )
    ocupacion = forms.BooleanField(
    required=False,
    widget=forms.RadioSelect(choices=((True, 'Sí'), (False, 'No'))),
    initial=False
    )
    
    descripcion_ocupacion = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'style': 'display: none;'}),
        label='Descripción Ocupación'
    )
    
    SINO_CHOICES = (
        (True, 'Sí'),
        (False, 'No'),
    )
    
    trabaja = forms.ChoiceField(
        choices=SINO_CHOICES,
        widget=forms.RadioSelect,
        required=True,
        initial=False  # Cambiado a False
    )
    

    cedula = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control custom-input'}), required=False)
    S_nombre = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control custom-input'}), required=False)

    class Meta:
        model = Persona
        fields = '__all__'
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
            # Otros widgets para otros campos si es necesario
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
                
        # Para el campo 'profesion'
        self.fields['profesion'].queryset = Profesion.objects.all()
        self.fields['profesion'].empty_label = None

        # Para el campo 'nivel_educativo'
        self.fields['nivel_educ'].queryset = Nivel_Educ.objects.all()
        self.fields['nivel_educ'].empty_label = None

        # Verificar si la instancia actual está editando una persona existente
        if self.instance.pk and self.instance.familia_r and self.instance.familia_r.jefe_de_familia:
            # Si está editando y la persona tiene una familia asociada, incluimos la familia actual de la persona
            familia_actual = self.instance.familia_r
            familias_con_menos_de_7 = Familia.objects.annotate(num_personas=Count('familia_personas')).filter(num_personas__lt=7) | Familia.objects.filter(idfamilia=familia_actual.idfamilia)
        else:
            # Si está creando una nueva persona o la persona no tiene una familia asociada, simplemente contamos todas las familias
            familias_con_menos_de_7 = Familia.objects.annotate(num_personas=Count('familia_personas')).filter(num_personas__lt=7)

        # Actualizar el queryset del campo familia_r
        self.fields['familia_r'].queryset = familias_con_menos_de_7

# forms.py
from django import forms
from .models import CustomUser

class EditUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'telefono', 'bio', 'cedula', 'group']


# aplicacion/forms.py
from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User

class UserProfileForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']


# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    group = forms.ModelChoiceField(queryset=Group.objects.all(), empty_label=None, label='Grupo')

    class Meta:
        model = CustomUser  # Utiliza el modelo personalizado
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'group']

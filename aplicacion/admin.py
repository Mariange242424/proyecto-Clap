from django.contrib import admin
from .models import Persona, Familia, Pagos, Banco, Profesion, Nivel_Educ, Bloque, Calle, CustomUser
from django.contrib.auth.admin import UserAdmin

# Define a function to get list_display for a model
def get_list_display(model):
    return [field.name for field in model._meta.fields]

# Register your models here.
class PersonaAdmin(admin.ModelAdmin):
    list_display = get_list_display(Persona)

class FamiliaAdmin(admin.ModelAdmin):
    list_display = get_list_display(Familia)

class BancoAdmin(admin.ModelAdmin):
    list_display = get_list_display(Banco)

class PagosAdmin(admin.ModelAdmin):
    list_display = get_list_display(Pagos)

class ProfesionAdmin(admin.ModelAdmin):
    list_display = get_list_display(Profesion)


class Nivel_EducAdmin(admin.ModelAdmin):
    list_display = get_list_display(Nivel_Educ)

class BloqueAdmin(admin.ModelAdmin):
    list_display = get_list_display(Bloque)

class CalleAdmin(admin.ModelAdmin):
    list_display = get_list_display(Calle)

class CustomUserAdmin(UserAdmin):
    list_display = ('id', 'username', 'first_name', 'last_name', 'email', 'telefono', 'group')
    search_fields = ('username', 'first_name', 'last_name', 'email')

admin.site.register(CustomUser, CustomUserAdmin)


admin.site.register(Persona, PersonaAdmin)
admin.site.register(Familia, FamiliaAdmin)
admin.site.register(Pagos, PagosAdmin)
admin.site.register(Profesion, ProfesionAdmin)
admin.site.register(Nivel_Educ, Nivel_EducAdmin)
admin.site.register(Bloque, BloqueAdmin)
admin.site.register(Calle, CalleAdmin)
admin.site.register(Banco, BancoAdmin)





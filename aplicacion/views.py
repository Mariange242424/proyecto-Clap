from django.shortcuts import render
from .models import Persona, Pagos, Familia,  Banco, Bloque, Profesion, Nivel_Educ
from .forms import PersonaForm, PagosForm, BancoForm, ReportePagosForm, ProfesionForm, NivelEducForm, CalleForm
from django.shortcuts import render,  get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count
from django.db.models.functions import TruncMonth
from datetime import date, timedelta
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseServerError
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import render
from django.http import FileResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
import logging
from django.db.models import Sum
from django.shortcuts import render
from django.db.models import Avg
from django.db.models import F, ExpressionWrapper, DurationField
from django.http import HttpResponseBadRequest
from django.db.models import Min, Max, Sum, Count, F, ExpressionWrapper, IntegerField
from django.db.models.functions import ExtractMonth, ExtractYear
from django.db.models.functions import TruncYear
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Banco, Bloque, Calle
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
logger = logging.getLogger(__name__)
from .forms import CustomUserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.models import Group
from datetime import datetime
from collections import Counter
from .choices import vivienda
import json
from django.http import HttpResponseForbidden
from django.db import transaction
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from django.http import HttpResponse, HttpResponseServerError
from django.http import JsonResponse
from django.views import View
from reportlab.platypus import Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
import locale
from django.http import HttpResponse
from .forms import RegistroForm  
from django.core.management import call_command
from django.http import JsonResponse
from django.views import View

def registro(request):
    familias = Familia.objects.all()
    mensaje_exito = None

    if request.method == 'POST':
        form = RegistroForm(request.POST)

        if form.is_valid():
            persona = form.save(commit=False)

            # Verificar si la persona es jefa de familia
            if persona.jefe_familia == 1:  # 1 para "Sí" en tu modelo
                # Crear una nueva familia si aún no existe
                nueva_familia, created = Familia.objects.get_or_create(jefe_de_familia=None)

                # Asignar la familia existente a la persona
                persona.familia_r = nueva_familia
                persona.save()

                # Asignar la instancia de Persona como jefe_de_familia en la familia
                nueva_familia.jefe_de_familia = persona
                nueva_familia.save()

            else:
                # Asignar la familia existente si se proporciona
                familia_id = request.POST.get('familia_r')  # Asegúrate de que este sea el nombre correcto del campo en tu formulario
                if familia_id:
                    familia = Familia.objects.get(idfamilia=familia_id)
                    persona.familia_r = familia
                    persona.save()

            # Muestra una notificación Toastr de éxito
            mensaje_exito = 'La persona ha sido registrada exitosamente.'

            if 'guardar_y_nuevo' in request.POST:
                # Redirige a la vista del formulario para añadir otra persona
                messages.success(request, mensaje_exito, extra_tags='toastr-success')
                return redirect('registro')

            # Si no es "Guardar y añadir otro", redirige a la lista de personas
            messages.success(request, mensaje_exito, extra_tags='toastr-success')
            return redirect('ListaPersonas')
        else:
            # En caso de errores en el formulario, puedes imprimirlos para debug
            print(form.errors)
    else:
        form = RegistroForm()

    return render(request, 'registro.html', {'form': form, 'familias': familias, 'mensaje_exito': mensaje_exito})


def nivel_requerido(nivel_requerido):
    def decorator(view_func):
        def wrapped_view(request, *args, **kwargs):
            if request.user.groups.filter(name=f'Nivel {nivel_requerido}').exists():
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponseForbidden("No tienes permisos suficientes para acceder a esta página.")

        return wrapped_view

    return decorator

@login_required
def Bienvenido(request):
    eliminar_familias_vacias()
    procesar_jefe_de_familia()
    logger.info("Función eliminar_familias_vacias ejecutada después")
    return render(request,'bienvenido.html')


def salir(request):
    logout(request)
    return redirect ('/')


def ListaPersonas(request):
    eliminar_familias_vacias()
    procesar_jefe_de_familia()
    personas = Persona.objects.all()
    edad_actual = date.today()
    
    
    for persona in personas:
        # Calcular la edad para cada persona
        edad = edad_actual.year - persona.fecha_nacimiento.year - ((edad_actual.month, edad_actual.day) < (persona.fecha_nacimiento.month, persona.fecha_nacimiento.day))
        persona.edad = edad
    return render(request, 'index.html', {'personas': personas})






def ListaPersonasEdicion(request):
    eliminar_familias_vacias()
    procesar_jefe_de_familia()
    personas = Persona.objects.all()
    edad_actual = date.today()
    for persona in personas:
        # Calcular la edad para cada persona
        edad = edad_actual.year - persona.fecha_nacimiento.year - ((edad_actual.month, edad_actual.day) < (persona.fecha_nacimiento.month, persona.fecha_nacimiento.day))
        persona.edad = edad
    return render(request, 'index_ee.html', {'personas': personas})



from django.db import IntegrityError  # Importa la excepción de integridad de la base de datos


def agregar_persona(request, familia_id=None):
    familias = Familia.objects.all()
    familia = None
    mensaje_exito = None

    if familia_id:
        familia = get_object_or_404(Familia, idfamilia=familia_id)

    if request.method == 'POST':
        form = PersonaForm(request.POST)

        if form.is_valid():
            try:
                persona = form.save(commit=False)

                # Verificar si la persona es jefa de familia
                if persona.jefe_familia == 1:  # 1 para "Sí" en tu modelo
                    # Crear una nueva familia si aún no existe
                    nueva_familia, created = Familia.objects.get_or_create(jefe_de_familia=None)

                    # Asignar la familia existente a la persona
                    persona.familia_r = nueva_familia
                    persona.save()

                    # Asignar la instancia de Persona como jefe_de_familia en la familia
                    nueva_familia.jefe_de_familia = persona
                    nueva_familia.save()

                else:
                    # Asignar la familia existente si se proporciona
                    if familia:
                        persona.familia_r = familia
                        persona.save()

                # Muestra una notificación Toastr de éxito
                mensaje_exito = 'La persona ha sido agregada a la carga familiar.'

                if 'guardar_y_nuevo' in request.POST:
                    # Redirige a la vista del formulario para añadir otra persona
                    messages.success(request, mensaje_exito, extra_tags='toastr-success')
                    return redirect('agregar_persona')

                # Si no es "Guardar y añadir otro", redirige a la lista de personas
                messages.success(request, mensaje_exito, extra_tags='toastr-success')
                return redirect('ListaPersonas')
            except IntegrityError as e:
                # Maneja la excepción de integridad de la base de datos (por ejemplo, violación de clave única)
                print(f"Error de integridad de la base de datos: {e}")
                messages.error(request, "Error al guardar la persona. Puede que ya exista en la base de datos.")
            except Exception as e:
                # Maneja otras excepciones no previstas
                print(f"Error desconocido: {e}")
                messages.error(request, "Error desconocido al guardar la persona.")
        else:
            # En caso de errores en el formulario, puedes imprimirlos para debug
            print(form.errors)
    else:
        form = PersonaForm()

    return render(request, 'agregar_persona.html', {'familia': familia, 'form': form, 'familias': familias, 'mensaje_exito': mensaje_exito})



def procesar_jefe_de_familia():
    # Obtener todas las personas que son jefes de familia en la tabla Familia
    familias_con_jefe = Familia.objects.exclude(jefe_de_familia=None)

    for familia in familias_con_jefe:
        persona_jefe = familia.jefe_de_familia

        # Verificar si la persona cumple las condiciones para ser eliminada como jefe de familia en la tabla Familia
        if persona_jefe.jefe_familia == 0 and persona_jefe.carga_familiar == 1:
            # Limpiar la relación en la tabla Familia
            familia.jefe_de_familia = None
            familia.save()
            print(f"Se eliminó a {persona_jefe} como jefe de familia.")



def lista_cargas_familiares(request):
    eliminar_familias_vacias()
    procesar_jefe_de_familia()
    logger.info("Función eliminar_familias_vacias ejecutada después")
    search_query = request.GET.get('search_query', '')  

    if search_query:
        familias = Familia.objects.filter(
            jefe_de_familia__num_casa__icontains=search_query
        ).select_related('jefe_de_familia').prefetch_related('familia_personas')
    else:
        familias = Familia.objects.select_related('jefe_de_familia').prefetch_related('familia_personas').all()

    familias_con_num_miembros = []
    for familia in familias:
        num_miembros = familia.familia_personas.exclude(idPersona=familia.jefe_de_familia.idPersona).count()
        familias_con_num_miembros.append({'familia': familia, 'num_miembros': num_miembros})

    return render(request, 'lista_cargas_familiares.html', {'familias_con_num_miembros': familias_con_num_miembros})

def detalle_familia(request, idfamilia):
    eliminar_familias_vacias()
    procesar_jefe_de_familia()
    familia = get_object_or_404(Familia, pk=idfamilia)
    personas = familia.familia_personas.all()
    return render(request, 'detalle_carga_familiar.html', {'familia': familia, 'personas': personas})

def ListaPagos(request):
    dat = Pagos.objects.all()
    return render(request,'Pagos.html',{'ListaPagos':dat})


@login_required
@nivel_requerido(2)
def registrar_pagos(request):
    if request.method == 'POST':
        form = PagosForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'El pago ha sido registrado exitosamente.')

            # Redirige a la lista de pagos o a la página deseada
            return redirect('ListaPagos')  
    else:
        form = PagosForm()

    return render(request, 'registrar_pagos.html', {'form': form})


def families_count(request):
    count = Familia.objects.count()
    return JsonResponse({'count': count})

def residents_count(request):
    count = Persona.objects.count()
    return JsonResponse({'count': count})

def payments_count(request):
    count = Pagos.objects.count()
    return JsonResponse({'count': count})




def informes(request):
    fecha_actual = date.today()

    # Obtén la lista de personas
    personas = Persona.objects.all()

    personas_hombres = Persona.objects.filter(sexo='M').count()
    personas_mujeres = Persona.objects.filter(sexo='F').count()

    # Calcula el número de personas casadas, solteras y en concubinato
    personas_casadas = Persona.objects.filter(estado_civil='c')
    personas_solteras = Persona.objects.filter(estado_civil='s')
    personas_concubinato = Persona.objects.filter(estado_civil='e')
    personas_divorciadas = Persona.objects.filter(estado_civil='d')


    


    # Obtiene la lista de fechas de nacimiento
    fechas_nacimiento = personas.values_list('fecha_nacimiento', flat=True)

    # Calcula la edad de las personas y cuenta el número en cada categoría
    # En tu vista (views.py)
    personas_mayores_de_18 = Persona.objects.filter(fecha_nacimiento__lte=fecha_actual - timedelta(days=18*365)).exclude(fecha_nacimiento__lt=fecha_actual - timedelta(days=65*365))
    personas_menores_de_18 = Persona.objects.filter(fecha_nacimiento__gt=fecha_actual - timedelta(days=18*365))
    personas_tercera_edad = Persona.objects.filter(fecha_nacimiento__lt=fecha_actual - timedelta(days=65*365))

    personas_sintrabajo = personas_mayores_de_18.filter(trabaja=False)
    personas_contrabajo = personas_mayores_de_18.filter(trabaja=True)

    return render(request, 'informes.html', {
    'personas_mayores_de_18': personas_mayores_de_18,
    'personas_hombres': personas_hombres,
    'personas_mujeres': personas_mujeres,
    'personas_menores_de_18': personas_menores_de_18,
    'personas_tercera_edad': personas_tercera_edad,
    'personas_casadas': personas_casadas,
    'personas_solteras': personas_solteras,
    'personas_concubinato': personas_concubinato,
    'personas_divorciadas': personas_divorciadas,
    'personas_sintrabajo' : personas_sintrabajo,
    'personas_contrabajo': personas_contrabajo
})



logger = logging.getLogger(__name__)

def eliminar_familias_vacias():
    # Obtiene las familias sin jefe de familia
    familias_vacias = Familia.objects.filter(jefe_de_familia__isnull=True)

    # Elimina las familias vacías sin miembros
    for familia in familias_vacias:
        if not familia.familia_personas.exists():
            familia.delete()
            logger.info(f"Familia {familia.idfamilia} eliminada porque está vacía.")






def editar_persona(request, persona_idPersona):
    persona = get_object_or_404(Persona, pk=persona_idPersona)

    if request.method == 'POST':
        form = PersonaForm(request.POST, instance=persona)
        if form.is_valid():
            persona = form.save()

            # Lógica adicional para el caso cuando jefe_familia es True
            if persona.jefe_familia:
                familia, _ = Familia.objects.get_or_create(jefe_de_familia=persona)
                familia.calle = persona.num_calle
                familia.bloque = persona.num_bloque
                familia.save()
                persona.familia_r = familia
                persona.save()

            eliminar_familias_vacias()
            logger.info("Función eliminar_familias_vacias ejecutada después de editar la persona.")

            return redirect('ListaPersonasEdicion')

    else:
        form = PersonaForm(instance=persona)

    # Verificar si la persona es jefe de familia y tiene más de una carga familiar
    es_jefe_con_mas_de_una_carga = persona.jefe_familia and persona.familia_r and persona.familia_r.familia_personas.count() > 1


    return render(request, 'editar_persona.html', {'form': form, 'familias': Familia.objects.all(), 'es_jefe_con_mas_de_una_carga': es_jefe_con_mas_de_una_carga})


def editar_persona_carga(request, persona_idPersona):
    persona = get_object_or_404(Persona, pk=persona_idPersona)

    if request.method == 'POST':
        form = PersonaForm(request.POST, instance=persona)
        if form.is_valid():
            persona = form.save()

            # Lógica adicional para el caso cuando jefe_familia es True
            if persona.jefe_familia:
                familia, _ = Familia.objects.get_or_create(jefe_de_familia=persona)
                familia.calle = persona.num_calle
                familia.bloque = persona.num_bloque
                familia.save()
                persona.familia_r = familia
                persona.save()

            eliminar_familias_vacias()
            logger.info("Función eliminar_familias_vacias ejecutada después de editar la persona.")

            return redirect('lista_cargas_familiares')
    else:
        form = PersonaForm(instance=persona)

    # Verificar si la persona es jefe de familia y tiene más de una carga familiar
    es_jefe_con_mas_de_una_carga = persona.jefe_familia and persona.familia_r.familia_personas.count() > 1

    return render(request, 'editar_persona_carga.html', {'form': form, 'familias': Familia.objects.all(), 'es_jefe_con_mas_de_una_carga': es_jefe_con_mas_de_una_carga})


@login_required
@nivel_requerido(2)
def eliminar_persona(request, persona_idPersona):
    try:
        persona = Persona.objects.get(idPersona=persona_idPersona)
        persona.delete()
    except Persona.DoesNotExist:
        # Manejar el caso en que la persona no existe
        pass
    return redirect('ListaPersonasEdicion')

def eliminar_persona_carga(request, persona_idPersona):
    try:
        persona = Persona.objects.get(idPersona=persona_idPersona)
        persona.delete()
    except Persona.DoesNotExist:
        # Manejar el caso en que la persona no existe
        pass
    return redirect('lista_cargas_familiares')


def detalle_persona(request, persona_id):
    persona = get_object_or_404(Persona, idPersona=persona_id)

    # Obtén el id de la familia relacionada
    id_familia_r = None
    if persona.familia_r:
        id_familia_r = persona.familia_r.idfamilia

    return render(request, 'detalle_persona.html', {
        'persona': persona,
        'id_familia_r': id_familia_r,
    })

def actualizacion_de_datos(request):

    lista_pagos = Pagos.objects.all()
    return render(request, 'actualizacion_de_datos.html', {'ListaPagos': lista_pagos})



def eliminar_pago(request, pago_id):
    try:
        pago = Pagos.objects.get(idPagos=pago_id)
        pago.delete()
    except Pagos.DoesNotExist:
        # Manejar el caso en que el pago no existe
        pass
    return redirect('ListaPagos')


def editar_pago(request, pago_id):
    pago = get_object_or_404(Pagos, idPagos=pago_id)

    if request.method == 'POST':
        form = PagosForm(request.POST, instance=pago)
        if form.is_valid():
            form.save()
            return redirect('ListaPagos')
    else:
        form = PagosForm(instance=pago)

    return render(request, 'editar_pago.html', {'form': form, 'pago': pago})



def agregar_persona_carga(request, familia_id=None):
    familias = Familia.objects.all()
    familia = None
    mensaje_exito = None

    if familia_id:
        familia = get_object_or_404(Familia, idfamilia=familia_id)

    if request.method == 'POST':
        form = PersonaForm(request.POST)

        if form.is_valid():
            persona = form.save(commit=False)

            # Verificar si la persona es jefa de familia
            if persona.jefe_familia == 1:  # 1 para "Sí" en tu modelo
                # Crear una nueva familia si aún no existe
                nueva_familia, created = Familia.objects.get_or_create(jefe_de_familia=None)

                # Asignar la familia existente a la persona
                persona.familia_r = nueva_familia
                persona.save()

                # Asignar la instancia de Persona como jefe_de_familia en la familia
                nueva_familia.jefe_de_familia = persona
                nueva_familia.save()

            else:
                # Asignar la familia existente si se proporciona
                if familia:
                    persona.familia_r = familia
                    persona.save()

            # Muestra una notificación Toastr de éxito
            mensaje_exito = 'La persona ha sido agregada a la carga familiar.'

            if 'guardar_y_nuevo' in request.POST:
                # Redirige a la vista del formulario para añadir otra persona
                messages.success(request, mensaje_exito, extra_tags='toastr-success')
                return redirect('agregar_persona')

            # Si no es "Guardar y añadir otro", redirige a la lista de personas
            messages.success(request, mensaje_exito, extra_tags='toastr-success')
            return redirect('detalle_familia', idfamilia=familia_id)
        else:
            # En caso de errores en el formulario, puedes imprimirlos para debug
            print(form.errors)
    else:
        form = PersonaForm()

    return render(request, 'agregar_persona_carga.html', {'familia': familia, 'form': form, 'familias': familias, 'mensaje_exito': mensaje_exito})





def generar_pdf_jefes_familia(request, selected_bloque):
    try:
        # Obtén las familias con jefes de familia en el bloque seleccionado
        familias = Familia.objects.filter(jefe_de_familia__num_bloque=selected_bloque, jefe_de_familia__isnull=False)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="acta_entrega_clap_{selected_bloque}.pdf"'

        # Crear el PDF con ReportLab
        buffer = BytesIO()
        pdf = SimpleDocTemplate(buffer, pagesize=letter)

        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

        # ...

        # Obtener la fecha actual en español
        fecha_actual = datetime.now().strftime('%d de %B de %Y')

        # Agregar un pie de página
        def footer(canvas, doc):
            canvas.saveState()
            canvas.setFont('Helvetica', 9)
            canvas.drawRightString(inch, 0.75 * inch, f'Página {doc.page}')  # Cambiar según tus necesidades
            canvas.restoreState()
        
        right_aligned_style = ParagraphStyle('RightAligned', alignment=2)
        title_style = ParagraphStyle('Title', alignment=TA_CENTER, fontSize=16, spaceAfter=12)
        # Agregar el contenido del acta de entrega a la historia del PDF
        story = [
            Paragraph('<b>ACTA DE ENTREGA DE BOLSAS CLAP:</b>', style=title_style),
            Spacer(0, 12),  # Agregar espacio después del título
            Paragraph(f'<b>Guanare, Portuguesa {fecha_actual}</b>', style=right_aligned_style),
            Spacer(0, 12),  # Agregar espacio después de la fecha
            Paragraph(f'En el día {fecha_actual}, se llevó a cabo la entrega de bolsas del Comité Local de Abastecimiento y Producción (CLAP) en Guanare, Portuguesa para el bloque {selected_bloque}. El objetivo de esta entrega es proporcionar alimentos básicos a las familias de la comunidad.',
                    style=ParagraphStyle('Normal')),
            Spacer(0, 12),  # Agregar espacio después del párrafo
        ]

        # Crear una tabla para mostrar cédula, nombre, apellido y firma de receptores
        data = [['Cedula:', 'Nombre:', 'Apellido:', 'Firma:']]

        for familia in familias:
            data.append([familia.jefe_de_familia.cedula, familia.jefe_de_familia.P_nombre, familia.jefe_de_familia.P_apellido, ''])

        table = Table(data)
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            # Configuración para blanco y negro
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        # Ajustar el ancho de la celda de firma (intentar con un valor más grande)
        table._argW[3] = 180  # Ajusta el ancho de la celda de firma a 200 puntos

        story.append(Spacer(0, 12))
        story.append(table)

        # Firma del responsable de la entrega
        story.append(Spacer(0, 12))
        story.append(Spacer(0, 12))
        firma_style = ParagraphStyle('Normal', alignment=TA_CENTER)
        story.append(Paragraph('<b>Firma del responsable de la entrega:</b>', style=firma_style))
        story.append(Spacer(0, 12))
        story.append(Spacer(0, 12))
        story.append(Paragraph('____________________________________________', style=firma_style))

        # Construir el PDF
        pdf.build(story, onFirstPage=footer, onLaterPages=footer)

        # Mover el cursor al inicio del buffer antes de enviar la respuesta
        buffer.seek(0)
        response.write(buffer.read())
        buffer.close()

        return response
    except Exception as e:
        logging.error(f"Error en la generación del PDF: {e}")
        print(f"Error en la generación del PDF: {e}")
        return HttpResponseServerError(f"Ocurrió un error al generar el PDF: {e}")











def tiene_registros(bloque):
    # Implementa la lógica real para verificar si el bloque tiene registros asociados
    return Bloque.objects.filter(numero_bloque=bloque).exists()

# Vista para seleccionar un bloque
def seleccionar_bloque(request):
    # Obtener bloques que tienen registros asociados
    bloques_con_registros = Bloque.objects.filter(persona__isnull=False).values_list('numero_bloque', flat=True).distinct()

    if request.method == 'POST':
        selected_bloque = request.POST.get('bloque')
        return render(request, 'generar_pdf.html', {'selected_bloque': selected_bloque})
    
    return render(request, 'seleccionar_bloque.html', {'bloques': bloques_con_registros})




def reporte_pagos(request):
    if request.method == 'GET':
        form = ReportePagosForm(request.GET)
        if form.is_valid():
            bloque = form.cleaned_data.get('bloque')
            mes_anio = form.cleaned_data.get('mes_anio')

            pagos_query = Pagos.objects.annotate(
                mes=TruncMonth('fecha')
            ).values('mes', 'jefe_de_familia__jefe_de_familia__num_bloque').annotate(
                total_pagos=Count('idPagos'),
                monto_total=Sum('monto')
            ).order_by('mes', 'jefe_de_familia__jefe_de_familia__num_bloque')

            if bloque and bloque != 'all':
                pagos_query = pagos_query.filter(jefe_de_familia__jefe_de_familia__num_bloque=bloque)

            if mes_anio:
                month, year = map(int, mes_anio.split('/'))  # Dividir por "/" y obtener el mes y el año
                date_to_filter = datetime(year, month, 1)
                pagos_query = pagos_query.filter(mes=date_to_filter)

        else:
            pagos_query = None

    else:
        form = ReportePagosForm()
        pagos_query = None

    return render(request, 'reporte_pagos.html', {'form': form, 'pagos_por_mes_y_bloque': pagos_query})



class ProfesionListView(ListView):
    model = Profesion
    template_name = 'profesion_list.html'  # Asegúrate de que la ruta sea correcta
    context_object_name = 'profesiones'  # Nombre para la variable en la plantilla

    def get_queryset(self):
        # Aquí obtienes la lista de profesiones
        return Profesion.objects.all()

class ProfesionCreateView(CreateView):
    model = Profesion
    template_name = 'profesion_form.html'
    form_class = ProfesionForm  # Usa tu formulario personalizado aquí
    success_url = reverse_lazy('profesion-list')

class ProfesionUpdateView(UpdateView):
    model = Profesion
    template_name = 'profesion_edit.html'
    form_class = ProfesionForm  # Utiliza tu formulario personalizado
    success_url = reverse_lazy('profesion-list')

class ProfesionDeleteView(DeleteView):
    model = Profesion
    template_name = 'profesion_confirm_delete.html'
    success_url = reverse_lazy('profesion-list')

    def get(self, request, *args, **kwargs):
        # Sobrescribimos el método get para verificar si hay personas relacionadas
        # con la profesión antes de mostrar la página de confirmación de eliminación.
        self.object = self.get_object()

        # Verificamos si hay personas relacionadas con la profesión.
        if self.object.persona_set.exists():
            # Si hay personas relacionadas, podrías redirigir a una página de error
            # o mostrar un mensaje indicando que no se puede eliminar la profesión.
            return HttpResponseRedirect(reverse_lazy('error-page'))  # Reemplaza 'error-page' con la URL deseada.

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # Sobrescribimos el método post para realizar la eliminación solo si
        # no hay personas relacionadas con la profesión.
        self.object = self.get_object()

        if self.object.persona_set.exists():
            # Si hay personas relacionadas, podrías redirigir a una página de error
            # o mostrar un mensaje indicando que no se puede eliminar la profesión.
            return HttpResponseRedirect(reverse_lazy('error-page'))  # Reemplaza 'error-page' con la URL deseada.

        return super().post(request, *args, **kwargs)

###############################################################

class NivelEducListView(ListView):
    model = Nivel_Educ
    template_name = 'niveleduc_list.html'


class NivelEducCreateView(CreateView):
    model = Nivel_Educ
    template_name = 'niveleduc_form.html'
    form_class = NivelEducForm
    success_url = reverse_lazy('nivel-educ-list')

class NivelEducUpdateView(UpdateView):
    model = Nivel_Educ
    template_name = 'niveleduc_form_edit.html'
    form_class = NivelEducForm
    success_url = reverse_lazy('nivel-educ-list')

class NivelEducDeleteView(DeleteView):
    model = Nivel_Educ
    template_name = 'niveleduc_confirm_delete.html'
    success_url = reverse_lazy('nivel-educ-list')

    def get(self, request, *args, **kwargs):
        # Sobrescribimos el método get para verificar si hay personas relacionadas
        # con el nivel educativo antes de mostrar la página de confirmación de eliminación.
        self.object = self.get_object()

        # Verificamos si hay personas relacionadas con el nivel educativo.
        if self.object.persona_set.exists():
            # Si hay personas relacionadas, podrías redirigir a una página de error
            # o mostrar un mensaje indicando que no se puede eliminar el nivel educativo.
            return HttpResponseRedirect(reverse_lazy('error-page'))  # Reemplaza 'error-page' con la URL deseada.

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # Sobrescribimos el método post para realizar la eliminación solo si
        # no hay personas relacionadas con el nivel educativo.
        self.object = self.get_object()

        if self.object.persona_set.exists():
            # Si hay personas relacionadas, podrías redirigir a una página de error
            # o mostrar un mensaje indicando que no se puede eliminar el nivel educativo.
            return HttpResponseRedirect(reverse_lazy('error-page'))  # Reemplaza 'error-page' con la URL deseada.

        return super().post(request, *args, **kwargs)


#######################################################################
class BancoListView(ListView):
    model = Banco
    template_name = 'banco_list.html'

class BancoCreateView(CreateView):
    model = Banco
    template_name = 'banco_form.html'
    fields = ['codigo', 'nombre']
    success_url = reverse_lazy('banco-list')

class BancoUpdateView(UpdateView):
    model = Banco
    template_name = 'banco_form_edit.html'
    fields = ['codigo', 'nombre']
    success_url = reverse_lazy('banco-list')

class BancoDeleteView(DeleteView):
    model = Banco
    template_name = 'banco_confirm_delete.html'
    success_url = reverse_lazy('banco-list')

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        # Verificamos si hay pagos registrados asociados al banco.
        if Pagos.objects.filter(banco_receptor=self.object).exists():
            return HttpResponseRedirect(reverse_lazy('error-page'))  # Reemplaza 'error-page' con la URL deseada.

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        # Verificamos si hay pagos registrados asociados al banco.
        if Pagos.objects.filter(banco_receptor=self.object).exists():
            return HttpResponseRedirect(reverse_lazy('error-page'))  # Reemplaza 'error-page' con la URL deseada.

        return super().post(request, *args, **kwargs)
##################################################################}


class BloqueListView(ListView):
    model = Bloque
    template_name = 'bloque_list.html'

class BloqueCreateView(CreateView):
    model = Bloque
    template_name = 'bloque_form.html'
    fields = ['numero_bloque']  # Personaliza los campos según tu modelo
    success_url = reverse_lazy('bloque-list')

class BloqueUpdateView(UpdateView):
    model = Bloque
    template_name = 'bloque_form_edit.html'
    fields = ['numero_bloque']  # Personaliza los campos según tu modelo
    success_url = reverse_lazy('bloque-list')

class BloqueDeleteView(DeleteView):
    model = Bloque
    template_name = 'bloque_confirm_delete.html'
    success_url = reverse_lazy('bloque-list')

    def get(self, request, *args, **kwargs):
        # Sobrescribimos el método get para verificar si hay personas relacionadas
        # con el bloque antes de mostrar la página de confirmación de eliminación.
        self.object = self.get_object()

        # Verificamos si hay personas relacionadas con el bloque.
        if self.object.persona_set.exists():
            # Si hay personas relacionadas, podrías redirigir a una página de error
            # o mostrar un mensaje indicando que no se puede eliminar el bloque.
            return HttpResponseRedirect(reverse_lazy('error-page'))  # Reemplaza 'error-page' con la URL deseada.

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # Sobrescribimos el método post para realizar la eliminación solo si
        # no hay personas relacionadas con el bloque.
        self.object = self.get_object()

        if self.object.persona_set.exists():
            # Si hay personas relacionadas, podrías redirigir a una página de error
            # o mostrar un mensaje indicando que no se puede eliminar el bloque.
            return HttpResponseRedirect(reverse_lazy('error-page'))  # Reemplaza 'error-page' con la URL deseada.

        return super().post(request, *args, **kwargs)


from django.http import HttpResponseRedirect

############################################################################3
class CalleListView(ListView):
    model = Calle
    template_name = 'calle_list.html'

class CalleCreateView(CreateView):
    model = Calle
    template_name = 'calle_form.html'
    form_class = CalleForm
    success_url = reverse_lazy('calle-list')

class CalleUpdateView(UpdateView):
    model = Calle
    template_name = 'calle_form_edit.html'
    form_class = CalleForm
    success_url = reverse_lazy('calle-list')

class CalleDeleteView(DeleteView):
    model = Calle
    template_name = 'calle_confirm_delete.html'
    success_url = reverse_lazy('calle-list')

    def get(self, request, *args, **kwargs):
        # Sobrescribimos el método get para verificar si hay personas relacionadas
        # con la calle antes de mostrar la página de confirmación de eliminación.
        self.object = self.get_object()

        # Verificamos si hay personas relacionadas con la calle.
        if self.object.persona_set.exists():
            # Si hay personas relacionadas, podrías redirigir a una página de error
            # o mostrar un mensaje indicando que no se puede eliminar la calle.
            return HttpResponseRedirect(reverse_lazy('error-page'))  # Reemplaza 'error-page' con la URL deseada.

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # Sobrescribimos el método post para realizar la eliminación solo si
        # no hay personas relacionadas con la calle.
        self.object = self.get_object()

        if self.object.persona_set.exists():
            # Si hay personas relacionadas, podrías redirigir a una página de error
            # o mostrar un mensaje indicando que no se puede eliminar la calle.
            return HttpResponseRedirect(reverse_lazy('error-page'))  # Reemplaza 'error-page' con la URL deseada.

        return super().post(request, *args, **kwargs)


###########################################################################



@login_required
def register(request):
    if request.user.groups.filter(name='Nivel 2').exists():
        if request.method == 'POST':
            user_creation_form = CustomUserCreationForm(data=request.POST)

            if user_creation_form.is_valid():
                user = user_creation_form.save(commit=False)
                user.save()

                # Asigna el grupo después de guardar el usuario
                user.groups.add(user_creation_form.cleaned_data['group'])

                # Guarda nuevamente para actualizar la relación de muchos a muchos
                user.save()

                return redirect('Bienvenido')

        else:
            user_creation_form = CustomUserCreationForm()

        return render(request, 'registration/register.html', {'form': user_creation_form})

    # Redirige o muestra un mensaje de error si el usuario no tiene permiso
    return redirect('PermisoDenegado')



def permiso_denegado(request):
    return render(request, 'permiso_denegado.html')
    


##############################################################################################

def seleccionar_bloque_carga(request):
    # Obtener bloques que tienen registros asociados
    bloques_con_registros = Bloque.objects.filter(persona__isnull=False).values_list('numero_bloque', flat=True).distinct()

    if request.method == 'POST':
        selected_bloque = request.POST.get('bloque')
        return render(request, 'generar_pdf_carga.html', {'selected_bloque': selected_bloque})
    
    return render(request, 'seleccionar_bloque_carga.html', {'bloques': bloques_con_registros})



#####################################################################################################
def generar_pdf_carga_familiar(request, selected_bloque):
    try:
        # Obtén las familias con jefes de familia en el bloque seleccionado
        familias = Familia.objects.filter(jefe_de_familia__num_bloque=selected_bloque, jefe_de_familia__isnull=False)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="acta_entrega_clap_{selected_bloque}.pdf"'

        # Crear el PDF con ReportLab
        buffer = BytesIO()
        pdf = SimpleDocTemplate(buffer, pagesize=letter)

        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

        # ...

        # Obtener la fecha actual en español
        fecha_actual = datetime.now().strftime('%d de %B de %Y')

        # Agregar un pie de página
        def footer(canvas, doc):
            canvas.saveState()
            canvas.setFont('Helvetica', 9)
            canvas.drawRightString(inch, 0.75 * inch, f'Página {doc.page}')  # Cambiar según tus necesidades
            canvas.restoreState()
        
        right_aligned_style = ParagraphStyle('RightAligned', alignment=2)
        title_style = ParagraphStyle('Title', alignment=TA_CENTER, fontSize=16, spaceAfter=12)
        # Agregar el contenido del acta de entrega a la historia del PDF
        story = [
            Paragraph('<b>Jefes de familia y cargas familiares:</b>', style=title_style),
            Spacer(0, 12),  # Agregar espacio después del título
            Paragraph(f'<b>Guanare, Portuguesa {fecha_actual}</b>', style=right_aligned_style),
            Spacer(0, 12),  # Agregar espacio después de la fecha
            Paragraph(f'En el día {fecha_actual}, se llevó a cabo la entrega de bolsas del Comité Local de Abastecimiento y Producción (CLAP) en Guanare, Portuguesa para el bloque {selected_bloque}. El objetivo de esta entrega es proporcionar alimentos básicos a las familias de la comunidad.',
                    style=ParagraphStyle('Normal')),
            Spacer(0, 12),  # Agregar espacio después del párrafo
        ]

        # Crear una tabla para mostrar cédula, nombre, apellido y firma de receptores
        data = [['Cedula','Nombre', 'Apellido', 'Miembros de Carga Familiar']]

        for familia in familias:
            jefe_de_familia = familia.jefe_de_familia
            carga_familiar = Persona.objects.filter(familia_r=familia, carga_familiar=1).count()
            data.append([jefe_de_familia.cedula,jefe_de_familia.P_nombre, jefe_de_familia.P_apellido, carga_familiar])


        table = Table(data)
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            # Configuración para blanco y negro
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        # Ajustar el ancho de la celda de firma (intentar con un valor más grande)
        table._argW[3] = 180  # Ajusta el ancho de la celda de firma a 200 puntos

        story.append(Spacer(0, 12))
        story.append(table)


        # Construir el PDF
        pdf.build(story, onFirstPage=footer, onLaterPages=footer)

        # Mover el cursor al inicio del buffer antes de enviar la respuesta
        buffer.seek(0)
        response.write(buffer.read())
        buffer.close()

        return response
    except Exception as e:
        logging.error(f"Error en la generación del PDF: {e}")
        print(f"Error en la generación del PDF: {e}")
        return HttpResponseServerError(f"Ocurrió un error al generar el PDF: {e}")






def reporte_familias(request):
    calles = Calle.objects.all()
    bloques = Bloque.objects.all()
    reporte_calles = []
    reporte_bloques = []

    for calle in calles:
        familias_count_calle = Familia.objects.filter(jefe_de_familia__num_calle=calle).count()
        reporte_calles.append({'calle': calle, 'familias_count': familias_count_calle})

    for bloque in bloques:
        familias_count_bloque = Familia.objects.filter(jefe_de_familia__num_bloque=bloque).count()
        reporte_bloques.append({'bloque': bloque, 'familias_count': familias_count_bloque})

    # Contar cuántas familias tienen cada tipo de vivienda considerando solo al jefe de familia
    tipos_vivienda = [choice[0] for choice in vivienda]
    familias_jefes = Familia.objects.filter(jefe_de_familia__jefe_familia=1)
    familias_por_tipo = Counter(familias_jefes.values_list('jefe_de_familia__tipo_vivienda', flat=True))

    # Devuelve un diccionario
    reporte_tipos_vivienda = dict(familias_por_tipo)

    return render(request, 'reporte_familias.html', {
        'reporte_calles': reporte_calles,
        'reporte_bloques': reporte_bloques,
        'reporte_tipos_vivienda': reporte_tipos_vivienda,
    })

def obtener_informacion_jefe(request, familia_id):
    # Obtén la instancia de la familia
    familia = get_object_or_404(Familia, idfamilia=familia_id)

    # Verifica si hay un jefe de familia asociado
    if familia.jefe_de_familia:
        jefe = familia.jefe_de_familia
        # Devuelve la información en formato JSON
        return JsonResponse({
            'num_casa': jefe.num_casa,
            'num_calle': jefe.num_calle.numero_calle if jefe.num_calle else None,
            'num_bloque': jefe.num_bloque.numero_bloque if jefe.num_bloque else None,
        })
    else:
        # Si no hay jefe de familia, devuelve un error o un valor predeterminado
        return JsonResponse({'error': 'No hay jefe de familia asociado a esta familia'})
    


class BackupView(View):
    def get(self, request, *args, **kwargs):
        try:
            # Ejecuta el comando dumpdata y almacena el resultado en un archivo
            call_command('dumpdata', output='backup.json')

            # Lee el archivo de respaldo y devuelve su contenido como una respuesta de descarga
            with open('backup.json', 'rb') as backup_file:
                response = HttpResponse(backup_file.read(), content_type='application/json')
                response['Content-Disposition'] = 'attachment; filename=backup.json'
                return response
        except Exception as e:
            # Maneja cualquier excepción y devuelve un mensaje de error
            return JsonResponse({'error': f"Error durante la copia de seguridad: {str(e)}"})





class RestoreView(View):
    def post(self, request, *args, **kwargs):
        try:
            # Obtén el archivo cargado desde la solicitud POST
            uploaded_file = request.FILES.get('backup_file')

            if not uploaded_file:
                raise ValueError("No se proporcionó ningún archivo")

            # Asegúrate de que el puntero del archivo esté al principio
            uploaded_file.seek(0)

            # Intenta leer el contenido del archivo con varias codificaciones
            encodings_to_try = ['utf-8', 'latin-1', 'iso-8859-1']
            content = None

            for encoding in encodings_to_try:
                try:
                    # Intenta decodificar el contenido utilizando una codificación específica
                    content = uploaded_file.read().decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue

            if content is None:
                raise ValueError("No se pudo decodificar el archivo con ninguna codificación compatible")

            # Imprime el contenido completo del archivo (puedes comentar esto en producción)
            print(f"Contenido completo del archivo: {content}")

            if not content.strip():
                raise ValueError("El archivo está vacío")

            try:
                # Intenta cargar los datos JSON desde el contenido leído
                data = json.loads(content)
            except json.JSONDecodeError as json_error:
                return JsonResponse({'error': f"Error al decodificar JSON: {json_error}"})

            # Utiliza el comando loaddata para cargar los datos en la base de datos
            call_command('loaddata', '--format=json', '--input=-', stdin=uploaded_file)

            return JsonResponse({'message': 'Restauración exitosa'})
        except Exception as e:
            return JsonResponse({'error': f"Error durante la restauración: {str(e)}"})
        

from django.utils import timezone

def generar_informe_pdf(request, familia_id):
    try:
        # Obtener la familia principal y su jefe
        familia = Familia.objects.get(idfamilia=familia_id)
        jefe_familia = familia.jefe_de_familia

        # Obtener familias relacionadas
        familias_relacionadas = Familia.objects.filter(jefe_de_familia=jefe_familia)

        # Crear el objeto HttpResponse con el tipo de contenido PDF
        response = HttpResponse(content_type='application/pdf')

        # Establecer el nombre del archivo PDF
        response['Content-Disposition'] = f'filename=informe_familia_{familia_id}.pdf'

        # Crear el objeto PDF, escribir contenido y cerrar el objeto
        p = canvas.Canvas(response)
        p.drawString(100, 800, f'Informe de Familia')

        # Información sobre la familia principal y su jefe
        p.drawString(100, 780, f'Jefe de Familia: {jefe_familia.cedula} {jefe_familia.P_nombre} {jefe_familia.P_apellido}')
        p.drawString(100, 760, f'Número de Calle: {jefe_familia.num_calle}')
        p.drawString(100, 740, f'Número de Casa: {jefe_familia.num_casa}')
        p.drawString(100, 720, f'Número de Bloque: {jefe_familia.num_bloque}')

        # Información sobre familias relacionadas y sus miembros
        p.drawString(100, 700, 'Carga Familiar:')
        y_position = 700

        for familia_relacionada in familias_relacionadas:

            # Obtener y listar los miembros de la familia relacionada (excluyendo al jefe)
            miembros_relacionados = Persona.objects.filter(familia_r=familia_relacionada).exclude(idPersona=jefe_familia.idPersona)
            y_position -= 20

            for miembro in miembros_relacionados:
                p.drawString(140, y_position, f'{miembro.P_nombre} {miembro.P_apellido}')
                y_position -= 15

        p.showPage()
        p.save()

        return response

    except Familia.DoesNotExist:
        return HttpResponse("La familia no existe", status=404)
    

class ErrorPageView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'error_page_template.html') 
    



# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import EditUserForm
from .models import CustomUser

@login_required
def view_profile(request):
    user = request.user

    if request.method == 'POST':
        user_form = EditUserForm(request.POST, instance=user)
        
        if user_form.is_valid():
            user_form.save()
            return redirect('view_profile')
    else:
        user_form = EditUserForm(instance=user)

    return render(request, 'view_profile.html', {'user_form': user_form, 'user': user})


# views.py
from django.shortcuts import render
from .models import CustomUser

def user_list(request):
    users = CustomUser.objects.all()
    return render(request, 'user_list.html', {'users': users})



# aplicacion/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User  # Importa tu modelo de usuario personalizado si lo has definido

@login_required
@staff_member_required
def admin_view(request):
    # Obtén la lista de usuarios
    users = User.objects.all()

    # Pasa la lista de usuarios a la plantilla
    context = {'users': users}

    # Renderiza la plantilla con la lista de usuarios
    return render(request, 'admin_template.html', context)



# aplicacion/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserProfileForm  # Ajusta el nombre del formulario según tu estructura de archivos

@login_required
def edit_profile(request):
    user = request.user

    if request.method == 'POST':
        # Manejar la lógica de guardado cuando se envía el formulario
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado exitosamente.')
            return redirect('view_profile')
        else:
            messages.error(request, 'Error al actualizar el perfil. Por favor, corrige los errores en el formulario.')
    else:
        # Presentar el formulario de edición
        form = UserProfileForm(instance=user)

    context = {'form': form}
    return render(request, 'edit_profile_template.html', context)



# aplicacion/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def views_profile(request):
    # Recupera el objeto de usuario actual
    user = request.user

    # Pasa el objeto de usuario a la plantilla
    context = {'user': user}
    return render(request, 'profile_template.html', context)


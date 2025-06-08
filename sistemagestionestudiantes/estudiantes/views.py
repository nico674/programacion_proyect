"""
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Avg
from .models import Estudiante, Asignatura, Nota
from .forms import EstudianteForm

def base(request):
    # Registrar estudiante
    if request.method == 'POST':
        form = EstudianteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('base')
    else:
        form = EstudianteForm()

    # Obtener todos los estudiantes
    estudiantes = Estudiante.objects.all()

    # Calcular promedio individual para cada estudiante
    for estudiante in estudiantes:
        promedio = Nota.objects.filter(estudiante=estudiante).aggregate(prom=Avg('calificacion'))['prom']
        estudiante.promedio = promedio if promedio is not None else 0

    # Calcular promedios por asignatura
    asignaturas = Asignatura.objects.all()
    promedios_curso = {}
    for asignatura in asignaturas:
        promedio = Nota.objects.filter(asignatura=asignatura).aggregate(avg=Avg('calificacion'))['avg']
        promedios_curso[asignatura.nombre] = promedio if promedio is not None else 0

    # Revisar si el usuario quiere ver detalle de un estudiante
    estudiante_detalle = None
    promedio_detalle = None
    estudiante_id = request.GET.get('id')  # Obtenemos id desde el query param

    if estudiante_id:
        estudiante_detalle = get_object_or_404(Estudiante, id=estudiante_id)
        promedio_detalle = Nota.objects.filter(estudiante=estudiante_detalle).aggregate(prom=Avg('calificacion'))['prom']
        if promedio_detalle is None:
            promedio_detalle = 0

    context = {
        'form': form,
        'estudiantes': estudiantes,
        'promedios_curso': promedios_curso,
        'estudiante_detalle': estudiante_detalle,
        'promedio': promedio_detalle,
    }
    return render(request, 'base.html', context)
"""
"""
# estudiantes/views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from bson.objectid import ObjectId
import pymongo

# ——————————————————————————————————————————————
# 1. Conexión global a MongoDB
client = pymongo.MongoClient('mongodb://localhost:27017')
db = client['sistema_gestion_estudiantes']
collection_estudiantes = db['estudiantes']
collection_notas = db['notas']
collection_asignaturas = db['asignaturas']
# ——————————————————————————————————————————————

def base(request):
    # ——————————————————  
    # 2. Registrar estudiante  
    # ——————————————————
    if request.method == 'POST' and request.POST.get('action') == 'add':
        nombre    = request.POST.get('nombre', '').strip()
        apellido  = request.POST.get('apellido', '').strip()
        documento = request.POST.get('documento', '').strip()
        codigo    = request.POST.get('codigo', '').strip()
        email     = request.POST.get('email', '').strip()

        if not all([nombre, apellido, documento, codigo, email]):
            messages.error(request, "Todos los campos son obligatorios.")
        else:
            collection_estudiantes.insert_one({
                'nombre': nombre,
                'apellido': apellido,
                'documento': documento,
                'codigo': codigo,
                'email': email
            })
            messages.success(request, "Estudiante registrado correctamente.")
        return redirect('base')

    # —————————————————————————————  
    # 3. Obtener y preparar listado  
    # —————————————————————————————
    estudiantes_cursor = collection_estudiantes.find().sort('_id', -1)
    estudiantes = []
    for est in estudiantes_cursor:
        # Calcular promedio de este estudiante
        agg = collection_notas.aggregate([
            {'$match': {'estudiante_id': est['_id']}},
            {'$group': {'_id': None, 'prom': {'$avg': '$calificacion'}}}
        ])
        prom = next(agg, {}).get('prom', 0)
        estudiantes.append({
            'id':        str(est['_id']),
            'nombre':    est.get('nombre', ''),
            'apellido':  est.get('apellido', ''),
            'documento': est.get('documento', ''),
            'codigo':    est.get('codigo', ''),
            'email':     est.get('email', ''),
            'promedio':  round(prom or 0, 2)
        })

    return render(request, 'base.html', {
        'estudiantes': estudiantes
})
"""
import pymongo
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from bson.objectid import ObjectId
from .forms import EstudianteForm
from django.views.decorators.csrf import csrf_exempt
# Conexión global a MongoDB
client = pymongo.MongoClient('mongodb://localhost:27017')
db = client['sistema_gestion_estudiantes']
collection_estudiantes = db['estudiantes']
collection_asignaturas = db['asignaturas']
collection_notas = db['notas']


def base(request):
    # Registro de Estudiante
    if request.method == 'POST':
        form = EstudianteForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            collection_estudiantes.insert_one({
                'nombre': data['nombre'],
                'apellido': data['apellido'],
                'documento': data['documento'],
                'codigo': data['codigo'],
                'email': data['email'],
            })
            messages.success(request, 'Estudiante registrado correctamente.')
            return redirect('index')  # Redirige al nombre de ruta 'index'
    else:
        form = EstudianteForm()

    # Lista de Estudiantes y promedio individual
    estudiantes_cursor = collection_estudiantes.find().sort('_id', -1)
    estudiantes = []
    for est in estudiantes_cursor:
        agg = collection_notas.aggregate([
            {'$match': {'estudiante_id': est['_id']}},
            {'$group': {'_id': None, 'prom': {'$avg': '$calificacion'}}}
        ])
        prom = next(agg, {}).get('prom', 0)
        estudiantes.append({
            'id': str(est['_id']),
            'nombre': est.get('nombre', ''),
            'apellido': est.get('apellido', ''),
            'codigo': est.get('codigo', ''),
            'email': est.get('email', ''),
            'promedio': round(prom or 0, 2),
        })

    # Promedio por Asignatura
    promedios_curso = {}
    for asig in collection_asignaturas.find():
        agg = collection_notas.aggregate([
            {'$match': {'asignatura_id': asig['_id']}},
            {'$group': {'_id': None, 'prom': {'$avg': '$calificacion'}}}
        ])
        prom = next(agg, {}).get('prom', 0)
        promedios_curso[asig.get('nombre', '')] = round(prom or 0, 2)

    return render(request, 'base.html', {
        'form': form,
        'estudiantes': estudiantes,
        'promedios_curso': promedios_curso,
    })


def panel_estudiantes(request):
    if request.method == 'POST':
        form = EstudianteForm(request.POST)
        if form.is_valid():
            estudiante_data = form.cleaned_data
            collection_estudiantes.insert_one(estudiante_data)
            messages.success(request, 'Estudiante registrado exitosamente.')
            return redirect('panel_estudiantes')
        else:
            messages.error(request, 'Formulario inválido.')

    busqueda = request.GET.get('busqueda', '')
    if busqueda:
        query = {
            '$or': [
                {'nombre': {'$regex': busqueda, '$options': 'i'}},
                {'apellido': {'$regex': busqueda, '$options': 'i'}},
                {'codigo': {'$regex': busqueda, '$options': 'i'}},
            ]
        }
        estudiantes = list(collection_estudiantes.find(query))
    else:
        estudiantes = list(collection_estudiantes.find().sort('_id', -1))

    # Si llegaste desde detalle_estudiante, podrías pasar una bandera para mostrar detalles.
    return render(request, 'base.html', {
        'form': EstudianteForm(),
        'estudiantes': estudiantes,
    })

def detalle_estudiante(request, id):
    try:
        obj_id = ObjectId(id)
    except Exception:
        messages.error(request, 'ID de estudiante inválido.')
        return redirect('index')

    
    est = collection_estudiantes.find_one({'_id': obj_id})
    if not est:
        messages.error(request, 'Estudiante no encontrado.')
        return redirect('index')

    estudiante_detalle = {
        'id': str(est['_id']),
        'nombre': est.get('nombre', ''),
        'apellido': est.get('apellido', ''),
        'codigo': est.get('codigo', ''),
        'email': est.get('email', ''),
    }

    notas = []
    for n in collection_notas.find({'estudiante_id': obj_id}):
        asig = collection_asignaturas.find_one({'_id': n['asignatura_id']})
        notas.append({
            'asignatura': asig.get('nombre', '') if asig else '',
            'calificacion': n.get('calificacion', 0),
        })

    estudiantes = []
    for est in collection_estudiantes.find().sort('_id', -1):
        estudiantes.append({
            'id': str(est['_id']),
            'nombre': est.get('nombre', ''),
            'apellido': est.get('apellido', ''),
            'codigo': est.get('codigo', ''),
            'email': est.get('email', ''),
        })

    promedios_curso = {}
    for asig in collection_asignaturas.find():
        agg = collection_notas.aggregate([
            {'$match': {'asignatura_id': asig['_id']}},
            {'$group': {'_id': None, 'prom': {'$avg': '$calificacion'}}}
        ])
        prom = next(agg, {}).get('prom', 0)
        promedios_curso[asig.get('nombre', '')] = round(prom or 0, 2)

    return render(request, 'base.html', {
        'form': EstudianteForm(),
        'estudiantes': estudiantes,
        'estudiante_detalle': estudiante_detalle,
        'notas_detalle': notas,
        'promedios_curso': promedios_curso,
})


def matricular_estudiante(request):
    # ————————————————————————————————
# Insertar asignaturas si no existen
# ————————————————————————————————
    asignaturas_predefinidas = [
        {'nombre': 'Matemáticas'},
        {'nombre': 'Física'},
        {'nombre': 'Química'},
        {'nombre': 'Programación'},
        {'nombre': 'Electrónica Digital'},
]

    for asignatura in asignaturas_predefinidas:
        existe = collection_asignaturas.find_one({'nombre': asignatura['nombre']})
        if not existe:
            collection_asignaturas.insert_one(asignatura)

    if request.method == 'POST':
        estudiante_id = request.POST.get('estudiante_id')
        asignatura_id = request.POST.get('asignatura_id')

        try:
            estudiante_oid = ObjectId(estudiante_id)
            asignatura_oid = ObjectId(asignatura_id)

            # Verificar si ya está matriculado
            ya_matriculado = collection_notas.find_one({
                'estudiante_id': estudiante_oid,
                'asignatura_id': asignatura_oid
            })
            if not ya_matriculado:
                collection_notas.insert_one({
                    'estudiante_id': estudiante_oid,
                    'asignatura_id': asignatura_oid,
                    'calificacion': None  # Sin nota aún
                })
                messages.success(request, 'Estudiante matriculado correctamente.')
            else:
                messages.info(request, 'El estudiante ya está matriculado en esta asignatura.')

        except Exception as e:
            messages.error(request, f'Error al matricular estudiante: {e}')

        return redirect('matricular_estudiante')

    # Convertir ObjectId a str para evitar errores en template
    estudiantes = []
    for est in collection_estudiantes.find():
        estudiantes.append({
            'id': str(est['_id']),
            'nombre': est.get('nombre', ''),
            'apellido': est.get('apellido', '')
        })

    asignaturas = []
    for asig in collection_asignaturas.find():
        asignaturas.append({
            'id': str(asig['_id']),
            'nombre': asig.get('nombre', '')
        })

    return render(request, 'base.html', {
        'estudiantes': estudiantes,
        'asignaturas': asignaturas,
        'vista_actual': 'matricular_estudiante'
    })

@csrf_exempt
def cancelar_curso(request):
    if request.method == 'POST':
        estudiante_id = request.POST.get('estudiante_id')
        asignatura_id = request.POST.get('asignatura_id')
        if estudiante_id and asignatura_id:
            db.notas.delete_one({
                'estudiante_id': ObjectId(estudiante_id),
                'asignatura_id': ObjectId(asignatura_id)
            })
    return redirect('home')  # Ajusta si tienes otro nombre para tu home 
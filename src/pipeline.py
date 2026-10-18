"""Lectura, inspección, limpieza auditable, selección y exportación."""
import json
import math
import re
from pathlib import Path
from .fuentes import cargar
from .modelos import NUTRIENTES, ProductoNutricional

CAMPOS = set(ProductoNutricional.__dataclass_fields__)
EAN = re.compile(r'(?:[0-9]{8}|[0-9]{13})')
CIQUAL = re.compile(r'CIQ-[0-9]+')


def validar_esquema(filas):
    if not filas:
        raise ValueError('El archivo no contiene filas')
    for numero, fila in enumerate(filas, 1):
        if not isinstance(fila, dict) or set(fila) != CAMPOS:
            raise ValueError(f'Fila {numero}: columnas incorrectas; se requieren {sorted(CAMPOS)}')


def numero(valor, campo, permitir_faltante=False):
    if valor is None or valor == '':
        if permitir_faltante:
            return None
        raise ValueError(f'{campo}: valor obligatorio faltante')
    if isinstance(valor, bool):
        raise ValueError(f'{campo}: se esperaba un número')
    try:
        resultado = float(str(valor).replace(',', '.'))
    except (ValueError, TypeError):
        raise ValueError(f'{campo}: número inválido') from None
    if not math.isfinite(resultado):
        raise ValueError(f'{campo}: número no finito')
    return resultado


def normalizar_ficha(fila):
    f = dict(fila)
    for campo in ('codigo', 'nombre', 'tipo', 'unidad_masa', 'unidad_energia'):
        if not isinstance(f[campo], str):
            raise ValueError(f'{campo}: debe ser texto (código conserva ceros iniciales)')
        f[campo] = f[campo].strip()
    if not isinstance(f['categorias'], str):
        raise ValueError('categorias: debe ser texto separado por |')
    f['categorias'] = tuple(sorted(set(c.strip() for c in f['categorias'].split('|') if c.strip()))) or ('sin-categoria',)
    f['base_g'] = numero(f['base_g'], 'base_g')
    for nutriente in NUTRIENTES:
        f[nutriente] = numero(f[nutriente], nutriente, True)
    return f


def validar_producto(f):
    if f['tipo'] not in ('etiqueta', 'alimento'):
        raise ValueError('tipo debe ser etiqueta o alimento')
    patron = EAN if f['tipo'] == 'etiqueta' else CIQUAL
    if not patron.fullmatch(f['codigo']):
        raise ValueError('Código inválido: EAN de 8/13 dígitos o CIQ-<número> según tipo')
    if not f['nombre'] or not f['categorias']:
        raise ValueError('Nombre y al menos una categoría son obligatorios')
    if f['base_g'] <= 0:
        raise ValueError('base_g debe ser positiva')
    if f['unidad_energia'] not in ('kcal', 'kJ') or f['unidad_masa'] not in ('g', 'mg'):
        raise ValueError('Unidades admitidas: kcal/kJ y g/mg; base siempre en gramos')
    producto = ProductoNutricional(**f)
    for nutriente in NUTRIENTES:
        valor = producto.nutriente_100g(nutriente)
        maximo = 1000 if nutriente == 'energia' else 100
        if valor is not None and not 0 <= valor <= maximo:
            raise ValueError(f'{nutriente}: fuera de rango [0,{maximo}] por 100 g')
    return producto


def limpiar_datos(filas):
    validar_esquema(filas)
    productos, incidencias, vistos = [], [], set()
    for numero_fila, fila in enumerate(filas, 1):
        try:
            normalizada = normalizar_ficha(fila)
            producto = validar_producto(normalizada)
            if producto.codigo in vistos:
                raise ValueError('Código duplicado: se conserva la primera ficha válida')
            vistos.add(producto.codigo)
            productos.append(producto)
            cambios = {}
            for campo, valor in normalizada.items():
                original = fila[campo]
                comparable = '|'.join(valor) if campo == 'categorias' else valor
                if type(original) is not type(comparable) or original != comparable:
                    cambios[campo] = {'antes': original, 'despues': list(valor) if isinstance(valor, tuple) else valor}
            faltantes = [n for n in NUTRIENTES if normalizada[n] is None]
            if cambios or faltantes:
                incidencias.append({'fila': numero_fila, 'estado': 'modificada', 'codigo': producto.codigo, 'cambios': cambios, 'faltantes': faltantes, 'original': fila})
        except ValueError as error:
            incidencias.append({'fila': numero_fila, 'estado': 'rechazada', 'motivo': str(error), 'original': fila})
    return productos, incidencias


def indexar_productos(productos):
    indice = {p.codigo: p for p in productos}
    if len(indice) != len(productos):
        raise ValueError('Índice con códigos duplicados')
    return indice


def buscar_producto(productos, codigo):
    try:
        return indexar_productos(productos)[codigo]
    except KeyError:
        raise ValueError(f'No existe el producto {codigo}') from None


def seleccionar(productos, codigos=None, categoria=None, texto='', tipo=None, max_energia=None, min_proteinas=None):
    for valor in (max_energia, min_proteinas):
        if valor is not None and (not math.isfinite(valor) or valor < 0):
            raise ValueError('Los límites nutricionales deben ser finitos y no negativos')
    if codigos:
        if len(set(codigos)) != len(codigos):
            raise ValueError('No repetir códigos en una comparación')
        productos = [buscar_producto(productos, c) for c in codigos]
    return [p for p in productos
            if (not categoria or categoria in p.categorias)
            and (not texto or texto.casefold() in p.nombre.casefold())
            and (not tipo or p.tipo == tipo)
            and (max_energia is None or p.energia is not None and p.nutriente_100g('energia') <= max_energia)
            and (min_proteinas is None or p.proteinas is not None and p.nutriente_100g('proteinas') >= min_proteinas)]


def comparar_etiquetas(productos, porcion_g=100):
    if not productos:
        raise ValueError('La selección no contiene productos')
    tabla = [p.ficha(porcion_g) for p in sorted(productos, key=lambda p: p.codigo)]
    base = tabla[0]
    for ficha in tabla:
        ficha['diferencia_absoluta_vs_primero'] = {n: None if ficha[n] is None or base[n] is None else round(abs(ficha[n] - base[n]), 6) for n in NUTRIENTES}
    return tabla


def ejecutar(ruta, **filtros):
    filas = cargar(ruta)
    productos, incidencias = limpiar_datos(filas)
    seleccion = seleccionar(productos, **filtros)
    tabla = comparar_etiquetas(seleccion) if seleccion else []
    rechazadas = sum(i['estado'] == 'rechazada' for i in incidencias)
    assert len(filas) == len(productos) + rechazadas, 'No se conserva el conteo de filas'
    return {'inspeccion': {'filas': len(filas), 'columnas': sorted(CAMPOS), 'validas': len(productos), 'rechazadas': rechazadas, 'seleccionadas': len(seleccion)}, 'mensaje': 'Comparación generada' if tabla else 'Sin productos para los filtros indicados; consultar incidencias', 'base': '100 g', 'unidades': {'energia': 'kcal', 'otros': 'g'}, 'tabla': tabla, 'incidencias': incidencias}


def guardar_resultado(resultado, directorio):
    directorio = Path(directorio)
    directorio.mkdir(parents=True, exist_ok=True)
    for nombre, datos in [('resultado.json', resultado), ('incidencias.json', resultado['incidencias'])]:
        (directorio / nombre).write_text(json.dumps(datos, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')

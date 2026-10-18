"""Validación independiente de campos, normalización y limpieza auditable."""
from collections import Counter
from datetime import date
from decimal import Decimal, InvalidOperation
import re
from .modelos import ChequeElectronico, Registro

CAMPOS = ('id_cheque', 'importe', 'fecha_pago', 'emisor', 'estado')
PATRON_ID = re.compile(r'ECH-[0-9]{6,12}')
PATRON_FECHA = re.compile(r'[0-9]{4}-[0-9]{2}-[0-9]{2}')
PATRON_IMPORTE = re.compile(r'[+-]?[0-9]+(?:[.,][0-9]{1,2})?')
CENTAVO = Decimal('0.01')
MAX_IMPORTE = Decimal('999999999999999.99')


def validar_importe(valor):
    """Aceptar decimales exactos, sin miles, exponentes ni redondeos ocultos."""
    if valor is None or valor == '':
        raise ValueError('Importe faltante')
    if isinstance(valor, (bool, float)) or not isinstance(valor, (str, int, Decimal)):
        raise ValueError('Importe debe ser texto o número decimal exacto, no float/bool')
    texto = str(valor).strip()
    if not PATRON_IMPORTE.fullmatch(texto):
        raise ValueError('Importe no numérico o formato inválido: usar hasta dos decimales, sin miles')
    try:
        importe = Decimal(texto.replace(',', '.'))
    except InvalidOperation:
        raise ValueError('Importe no numérico') from None
    if not importe.is_finite() or importe < 0:
        raise ValueError('Importe negativo o no finito')
    if importe > MAX_IMPORTE:
        raise ValueError(f'Importe excede el máximo admitido {MAX_IMPORTE}')
    return importe.quantize(CENTAVO)


def normalizar_campos(fila):
    resultado = dict(fila)
    for campo in ('id_cheque','fecha_pago','emisor','estado'):
        valor = resultado.get(campo)
        if isinstance(valor,str):
            resultado[campo] = valor.strip()
    for campo in ('id_cheque','estado'):
        if isinstance(resultado.get(campo),str):
            resultado[campo] = resultado[campo].upper()
    return resultado


def validar_registro(fila, fuente, numero):
    normalizado = normalizar_campos(fila)
    errores, motivos = [], []
    def error(tipo, mensaje):
        errores.append(tipo)
        motivos.append(mensaje)
    faltan = [c for c in CAMPOS if c not in fila]
    extras = [str(c) for c in fila if c not in CAMPOS]
    if faltan:
        error('CAMPOS_FALTANTES', 'Campos ausentes: '+', '.join(faltan))
    if extras:
        error('CAMPOS_INESPERADOS', 'Campos no definidos: '+', '.join(extras))
    codigo = normalizado.get('id_cheque')
    if not isinstance(codigo,str) or not PATRON_ID.fullmatch(codigo):
        error('ID_INVALIDO','Identificador inválido: se espera ECH- y 6 a 12 dígitos ASCII')
        normalizado['id_cheque'] = None  # No usar un ID no reconocido como candidato.
    importe, exclusion = None, None
    try:
        importe = validar_importe(normalizado.get('importe'))
        normalizado['importe'] = importe
    except ValueError as exc:
        exclusion = str(exc)
        error('IMPORTE_INVALIDO',exclusion)
        normalizado['importe'] = None
    texto_fecha = normalizado.get('fecha_pago')
    fecha = None
    try:
        if not isinstance(texto_fecha,str) or not PATRON_FECHA.fullmatch(texto_fecha):
            raise ValueError('formato')
        fecha = date.fromisoformat(texto_fecha)
    except ValueError:
        error('FECHA_INVALIDA',f'Fecha de pago inválida: {texto_fecha!r}; usar AAAA-MM-DD y una fecha real')
    for campo in ('emisor','estado'):
        if not isinstance(normalizado.get(campo),str) or not normalizado[campo]:
            error('CAMPO_OBLIGATORIO',f'{campo}: texto obligatorio faltante o inválido')
    cheque = None
    if not errores:
        cheque = ChequeElectronico(codigo,importe,fecha,normalizado['emisor'],normalizado['estado'])
    # La representación canónica usa fecha ISO e importe con dos decimales.
    if fecha is not None:
        normalizado['fecha_pago'] = fecha.isoformat()
    cambios = {}
    for campo in CAMPOS:
        antes, despues = fila.get(campo), normalizado.get(campo)
        if type(antes) is not type(despues) or antes != despues:
            cambios[campo] = {'antes': antes, 'despues': despues}
    return Registro(fuente,numero,dict(fila),normalizado,errores,motivos,cheque,importe,exclusion,cambios=cambios)


def limpiar_registros(filas, fuente):
    if fuente not in ('banco','sistema'):
        raise ValueError('Fuente debe ser banco o sistema')
    if not filas:
        raise ValueError(f'{fuente}: no hay registros')
    registros = []
    for numero, fila in enumerate(filas,1):
        if not isinstance(fila,dict):
            raise ValueError(f'{fuente}, fila {numero}: se esperaba un objeto')
        registros.append(validar_registro(fila,fuente,numero))
    frecuencias = Counter(r.codigo for r in registros if r.codigo is not None)
    for registro in registros:
        registro.duplicado = registro.codigo is not None and frecuencias[registro.codigo] > 1
    return registros

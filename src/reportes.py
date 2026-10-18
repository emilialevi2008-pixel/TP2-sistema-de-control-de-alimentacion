"""Cuatro reportes UTF-8: detalle, errores y dos resúmenes coherentes."""
import csv
from datetime import date
from .fechas import mostrar_fecha
from decimal import Decimal
import json
import os
from pathlib import Path
import tempfile

NOMBRES = ('reporte_conciliacion.csv','cheques_con_errores.csv','resumen.json','resumen_importes.csv')
COLUMNAS = ('id_banco','id_sistema','importe_banco','importe_sistema','diferencia_importe',
            'fecha_banco','fecha_sistema','estado','tipo_error','descripcion',
            'fila_origen_banco','fila_origen_sistema','grupo','candidatos_banco',
            'importe_original_banco','importe_original_sistema')


def decimal_json(valor):
    if isinstance(valor,Decimal):
        return str(valor)
    if isinstance(valor,date):
        return mostrar_fecha(valor)
    raise TypeError(f'Tipo no serializable: {type(valor).__name__}')


def detalle(resultado):
    b,s = resultado.banco,resultado.sistema
    def dato(registro,campo):
        if registro is None:
            return ''
        if campo=='importe':
            return '' if registro.importe is None else format(registro.importe,'.2f')
        return registro.normalizado.get(campo) or registro.original.get(campo) or ''
    return {'id_banco':dato(b,'id_cheque'),'id_sistema':dato(s,'id_cheque'),
            'importe_banco':dato(b,'importe'),'importe_sistema':dato(s,'importe'),
            'diferencia_importe':format(b.importe-s.importe,'.2f') if b and s and b.importe is not None and s.importe is not None else '',
            'fecha_banco':dato(b,'fecha_pago'),'fecha_sistema':dato(s,'fecha_pago'),
            'estado':resultado.estado,'tipo_error':'|'.join(resultado.tipos),'descripcion':resultado.descripcion,
            'fila_origen_banco':b.fila if b else '', 'fila_origen_sistema':s.fila if s else '',
            'grupo':resultado.grupo,
            'candidatos_banco':'|'.join(f"{c['id_cheque']}@{c['fila_banco']}" for c in resultado.candidatos),
            'importe_original_banco':b.original.get('importe','') if b else '',
            'importe_original_sistema':s.original.get('importe','') if s else ''}


def escribir_csv(ruta,columnas,filas):
    with Path(ruta).open('w',encoding='utf-8-sig',newline='') as archivo:
        escritor = csv.DictWriter(archivo,fieldnames=columnas,delimiter=';')
        escritor.writeheader()
        escritor.writerows(filas)


def guardar_reportes(resultados,resumen,directorio,entradas=()):
    destino = Path(directorio)
    objetivos = {(destino/nombre).resolve() for nombre in NOMBRES}
    if any(Path(ruta).resolve() in objetivos for ruta in entradas):
        raise ValueError('La carpeta de salida sobrescribiría un archivo de entrada')
    destino.mkdir(parents=True,exist_ok=True)
    filas = [detalle(r) for r in resultados]
    # Preparar los cuatro archivos completos antes de reemplazar salidas anteriores.
    with tempfile.TemporaryDirectory(prefix='.echeq-',dir=destino) as temporal:
        temporal = Path(temporal)
        escribir_csv(temporal/NOMBRES[0],COLUMNAS,filas)
        escribir_csv(temporal/NOMBRES[1],COLUMNAS,[f for f in filas if f['grupo']!='conciliados'])
        (temporal/NOMBRES[2]).write_text(json.dumps(resumen,default=decimal_json,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
        fila_importes = {k:format(v,'.2f') if isinstance(v,Decimal) else v for k,v in resumen['importes'].items()}
        escribir_csv(temporal/NOMBRES[3],tuple(fila_importes),[fila_importes])
        for nombre in NOMBRES:
            os.replace(temporal/nombre,destino/nombre)
    return [destino/nombre for nombre in NOMBRES]

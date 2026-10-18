"""Recetas personales estimadas y persistencia local separada del catálogo."""
import json
import sqlite3
from pathlib import Path
from .pipeline import buscar_producto, numero
from .modelos import NUTRIENTES


def calcular_receta(datos, productos):
    if not isinstance(datos, dict):
        raise ValueError('La receta debe ser un objeto')
    nombre = datos.get('nombre')
    if not isinstance(nombre, str) or not nombre.strip() or len(nombre.strip()) > 120:
        raise ValueError('Nombre obligatorio de hasta 120 caracteres')
    porciones = numero(datos.get('porciones'), 'porciones')
    if not 0.01 <= porciones <= 10000:
        raise ValueError('Las porciones deben estar entre 0.01 y 10000')
    ingredientes = datos.get('ingredientes')
    if not isinstance(ingredientes, list) or not ingredientes:
        raise ValueError('Se requiere al menos un ingrediente')
    total_g, totales, normalizados = 0, dict.fromkeys(NUTRIENTES, 0.0), []
    for ingrediente in ingredientes:
        if not isinstance(ingrediente, dict):
            raise ValueError('Cada ingrediente debe ser un objeto con codigo y gramos')
        codigo = ingrediente.get('codigo')
        if not isinstance(codigo, str):
            raise ValueError('Código de ingrediente debe ser texto')
        producto = buscar_producto(productos, codigo)
        gramos = numero(ingrediente.get('gramos'), 'gramos')
        if not 0 < gramos <= 100000:
            raise ValueError('Gramos debe estar en (0,100000]')
        total_g += gramos
        normalizados.append({'codigo': codigo, 'gramos': gramos})
        for n in NUTRIENTES:
            valor = producto.nutriente_100g(n)
            totales[n] = None if valor is None or totales[n] is None else totales[n] + valor * gramos / 100
    if total_g > 1000000:
        raise ValueError('Masa total excesiva')
    def escala(factor):
        return {n: None if v is None else round(v * factor, 6) for n, v in totales.items()}
    return {'nombre': nombre.strip(), 'porciones': porciones, 'ingredientes': normalizados,
            'masa_total_g': total_g, 'porcion_g': total_g / porciones,
            'totales': escala(1), 'por_porcion': escala(1 / porciones),
            'por_100g': escala(100 / total_g),
            'metodo': 'Estimación por suma de ingredientes; sin pérdidas ni cambio de masa por cocción'}


class AlmacenRecetas:
    def __init__(self, ruta):
        self.ruta = Path(ruta)
        self.ruta.parent.mkdir(parents=True, exist_ok=True)
        with self.conectar() as conexion:
            conexion.execute('CREATE TABLE IF NOT EXISTS recetas (id INTEGER PRIMARY KEY, datos TEXT NOT NULL)')

    def conectar(self):
        return sqlite3.connect(self.ruta)

    def listar(self):
        with self.conectar() as conexion:
            return [dict(json.loads(datos), id=identificador) for identificador, datos in conexion.execute('SELECT id, datos FROM recetas ORDER BY id')]

    def guardar(self, datos, productos, identificador=None):
        receta = calcular_receta(datos, productos)
        # Solo persistir entradas; los cálculos se regeneran al consultar.
        entrada = {k: receta[k] for k in ('nombre', 'porciones', 'ingredientes')}
        texto = json.dumps(entrada, ensure_ascii=False, allow_nan=False)
        with self.conectar() as conexion:
            if identificador is None:
                identificador = conexion.execute('INSERT INTO recetas(datos) VALUES (?)', (texto,)).lastrowid
            elif conexion.execute('UPDATE recetas SET datos=? WHERE id=?', (texto, identificador)).rowcount != 1:
                raise ValueError('Receta inexistente')
        return dict(receta, id=identificador)

    def eliminar(self, identificador):
        with self.conectar() as conexion:
            if conexion.execute('DELETE FROM recetas WHERE id=?', (identificador,)).rowcount != 1:
                raise ValueError('Receta inexistente')

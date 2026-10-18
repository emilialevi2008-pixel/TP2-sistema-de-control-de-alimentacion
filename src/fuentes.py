"""Lectores tabulares: contrato común y errores estructurales explícitos."""
from abc import ABC, abstractmethod
import csv
from decimal import Decimal
import json
from pathlib import Path


class FuenteDatos(ABC):
    @abstractmethod
    def cargar(self, ruta):
        """Devolver una lista de diccionarios sin interpretar el dominio."""


class FuenteCSV(FuenteDatos):
    def cargar(self, ruta):
        with Path(ruta).open(encoding='utf-8-sig', newline='') as archivo:
            try:
                lector = csv.DictReader(archivo, strict=True)
                if not lector.fieldnames or len(set(lector.fieldnames)) != len(lector.fieldnames):
                    raise ValueError('CSV vacío o con encabezados duplicados')
                filas = []
                for numero, fila in enumerate(lector, 1):
                    if None in fila or any(v is None for v in fila.values()):
                        raise ValueError(f'CSV registro {numero}: cantidad de columnas incompatible con la cabecera')
                    filas.append(fila)
            except csv.Error as error:
                raise ValueError(f'CSV malformado: {error}') from error
        if not filas:
            raise ValueError('CSV sin registros de datos')
        return filas


def rechazar_constante(valor):
    raise ValueError(f'Constante JSON no válida: {valor}')


def objeto_sin_claves_repetidas(pares):
    resultado = {}
    for clave, valor in pares:
        if clave in resultado:
            raise ValueError(f'JSON con clave repetida: {clave}')
        resultado[clave] = valor
    return resultado


class FuenteJSON(FuenteDatos):
    def cargar(self, ruta):
        with Path(ruta).open(encoding='utf-8-sig') as archivo:
            filas = json.load(archivo, parse_float=Decimal, parse_constant=rechazar_constante,
                              object_pairs_hook=objeto_sin_claves_repetidas)
        if not isinstance(filas, list) or not filas or not all(isinstance(f, dict) for f in filas):
            raise ValueError('JSON debe ser una lista no vacía de objetos')
        return filas


def cargar(ruta):
    fuentes = {'.csv': FuenteCSV, '.json': FuenteJSON}
    extension = Path(ruta).suffix.lower()
    if extension not in fuentes:
        raise ValueError('Formato no admitido: usar CSV o JSON')
    return fuentes[extension]().cargar(ruta)

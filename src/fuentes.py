"""Interfaz común: ambos formatos entregan listas de diccionarios."""
from abc import ABC, abstractmethod
import csv
import json
from pathlib import Path


class FuenteDatos(ABC):
    @abstractmethod
    def cargar(self, ruta):
        """Cargar o propagar un error de lectura comprensible."""


class FuenteCSV(FuenteDatos):
    def cargar(self, ruta):
        with Path(ruta).open(encoding='utf-8-sig', newline='') as archivo:
            lector = csv.DictReader(archivo)
            if not lector.fieldnames or len(set(lector.fieldnames)) != len(lector.fieldnames):
                raise ValueError('CSV sin encabezados o con columnas duplicadas')
            return list(lector)


class FuenteJSON(FuenteDatos):
    def cargar(self, ruta):
        with Path(ruta).open(encoding='utf-8') as archivo:
            filas = json.load(archivo)
        if not isinstance(filas, list) or not all(isinstance(f, dict) for f in filas):
            raise ValueError('JSON debe ser una lista de objetos')
        return filas


def cargar(ruta):
    extension = Path(ruta).suffix.lower()
    fuentes = {'.csv': FuenteCSV, '.json': FuenteJSON}
    if extension not in fuentes:
        raise ValueError('Entrada debe ser CSV o JSON')
    return fuentes[extension]().cargar(ruta)

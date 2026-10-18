"""Modelo de una ficha y conversión de nutrientes a una base común."""
from dataclasses import dataclass
import math

NUTRIENTES = ('energia', 'proteinas', 'carbohidratos', 'grasas')


@dataclass(frozen=True)
class ProductoNutricional:
    codigo: str
    nombre: str
    categorias: tuple[str, ...]
    tipo: str
    base_g: float
    energia: float | None
    unidad_energia: str
    proteinas: float | None
    carbohidratos: float | None
    grasas: float | None
    unidad_masa: str

    def nutriente_100g(self, nutriente):
        if nutriente not in NUTRIENTES:
            raise ValueError('Nutriente desconocido')
        valor = getattr(self, nutriente)
        if valor is None:
            return None
        factor = (1 / 4.184 if self.unidad_energia == 'kJ' else 1) if nutriente == 'energia' else (0.001 if self.unidad_masa == 'mg' else 1)
        return valor * factor * 100 / self.base_g

    def ficha(self, porcion_g=100):
        if not math.isfinite(porcion_g) or porcion_g <= 0:
            raise ValueError('La porción debe ser positiva y finita')
        salida = {'codigo': self.codigo, 'nombre': self.nombre, 'categorias': list(self.categorias), 'tipo': self.tipo, 'porcion_g': porcion_g}
        for nutriente in NUTRIENTES:
            valor = self.nutriente_100g(nutriente)
            salida[nutriente] = None if valor is None else round(valor * porcion_g / 100, 6)
        return salida

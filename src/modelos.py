"""Modelo del dominio y trazabilidad de cada registro físico."""
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Any


@dataclass(frozen=True)
class ChequeElectronico:
    id_cheque: str
    importe: Decimal
    fecha_pago: date
    emisor: str
    estado: str

    def diferencias(self, otro):
        """Comparar exclusivamente importe y fecha_pago; el ID se resuelve antes."""
        errores = []
        if self.importe != otro.importe:
            errores.append('ERROR_IMPORTE')
        if self.fecha_pago != otro.fecha_pago:
            errores.append('ERROR_FECHA')
        return errores

    def diferencia_importe(self, otro):
        return self.importe - otro.importe


@dataclass
class Registro:
    fuente: str
    fila: int
    original: dict[str, Any]
    normalizado: dict[str, Any]
    errores: list[str]
    motivos: list[str]
    cheque: ChequeElectronico | None
    importe: Decimal | None
    exclusion_importe: str | None
    duplicado: bool = False
    cambios: dict[str, Any] = field(default_factory=dict)

    @property
    def codigo(self):
        return self.normalizado.get('id_cheque')

    @property
    def habilitado(self):
        return self.cheque is not None and not self.duplicado

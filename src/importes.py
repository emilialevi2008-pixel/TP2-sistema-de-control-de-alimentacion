"""Sumas brutas independientes de la validez de otros campos y de los matches."""
from decimal import Decimal

CERO = Decimal('0.00')


def calcular_total_bruto(registros):
    incluidos = [r for r in registros if r.importe is not None]
    excluidos = [{'fila':r.fila,'id_cheque':r.original.get('id_cheque'),
                  'valor':r.original.get('importe'),'motivo':r.exclusion_importe}
                 for r in registros if r.importe is None]
    return {'total':sum((r.importe for r in incluidos), CERO),
            'incluidos':len(incluidos),'filas_incluidas':[r.fila for r in incluidos],
            'excluidos':len(excluidos),'registros_excluidos':excluidos,
            'duplicados_incluidos':[r.fila for r in incluidos if r.duplicado]}


def formato_ars(importe):
    """Presentación solamente; los cálculos y exportación conservan Decimal."""
    return '$'+format(importe,',.2f').replace(',','_').replace('.',',').replace('_','.')

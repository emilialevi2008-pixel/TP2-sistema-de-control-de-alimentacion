"""Fechas sin adivinar día/mes y períodos elegidos por quien ejecuta."""
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
import re

ARGENTINA = re.compile(r'([0-9]{2})/([0-9]{2})/([0-9]{4})')
ISO = re.compile(r'[0-9]{4}-[0-9]{2}-[0-9]{2}')
SERIAL = re.compile(r'[0-9]+(?:[.,][0-9]+)?')


def mostrar_fecha(fecha):
    return f'{fecha.day:02d}/{fecha.month:02d}/{fecha.year:04d}'


def interpretar_fecha(valor, sistema_excel='1900'):
    """DMY explícito, ISO o serial Excel entero; nunca suponer formato mes/día."""
    if sistema_excel not in ('1900','1904'):
        raise ValueError('Sistema de fechas Excel debe ser 1900 o 1904')
    if isinstance(valor,datetime):
        if valor.tzinfo is not None or valor.time() != datetime.min.time():
            raise ValueError('Fecha con hora o zona: exportar solo la fecha de pago')
        return valor.date()
    if isinstance(valor,date):
        return valor
    if isinstance(valor,bool) or not isinstance(valor,(str,int,Decimal)):
        raise ValueError('Fecha inválida: usar DD/MM/AAAA, AAAA-MM-DD o serial Excel entero')
    texto = str(valor).strip()
    # Excel exporta a veces medianoche textual; no descartar otras horas sin aviso.
    for separador in (' ', 'T'):
        sufijo = separador+'00:00:00'
        if texto.endswith(sufijo):
            texto = texto[:-len(sufijo)]
            break
    argentino = ARGENTINA.fullmatch(texto)
    try:
        if argentino:
            dia,mes,anio = map(int,argentino.groups())
            return date(anio,mes,dia)
        if ISO.fullmatch(texto):
            return date.fromisoformat(texto)
        if SERIAL.fullmatch(texto):
            serial = Decimal(texto.replace(',','.'))
            if not serial.is_finite() or serial != serial.to_integral_value():
                raise ValueError('Serial Excel con hora: exportar solo la fecha sin fracción')
            if not (0 if sistema_excel=='1904' else 1) <= serial <= 2958465:
                raise ValueError('Serial Excel fuera de rango')
            dias = int(serial)
            if sistema_excel=='1904':
                return date(1904,1,1)+timedelta(days=dias)
            if dias==60:
                raise ValueError('Serial Excel 60 corresponde al inexistente 29/02/1900')
            return date(1899,12,31)+timedelta(days=dias-(dias>60))
    except (ValueError,OverflowError,InvalidOperation) as error:
        raise ValueError(f'Fecha inválida: {error}') from None
    raise ValueError('Fecha no interpretable con seguridad: usar DD/MM/AAAA o AAAA-MM-DD; no mes/día ni años de dos dígitos')


def fecha_del_periodo(texto):
    if not isinstance(texto,str) or not ARGENTINA.fullmatch(texto.strip()):
        raise ValueError('Las fechas del período deben ingresarse en DD/MM/AAAA')
    return interpretar_fecha(texto)


@dataclass(frozen=True)
class PeriodoConciliacion:
    inicio: date
    fin: date

    def __post_init__(self):
        if type(self.inicio) is not date or type(self.fin) is not date:
            raise ValueError('El período requiere fechas de calendario válidas')
        if self.inicio > self.fin:
            raise ValueError('La fecha inicial no puede ser posterior a la final')

    @classmethod
    def desde_texto(cls,inicio,fin):
        return cls(fecha_del_periodo(inicio),fecha_del_periodo(fin))

    def contiene(self,fecha):
        return self.inicio <= fecha <= self.fin

    def describir(self):
        return {'inicio':mostrar_fecha(self.inicio),'fin':mostrar_fecha(self.fin),'limites_incluidos':True}


def filtrar_periodo(filas,fuente,periodo,sistema_excel='1900'):
    """Conservar ordinales y justificar toda exclusión sin imputar fechas."""
    if sistema_excel not in ('1900','1904'):
        raise ValueError('Sistema de fechas Excel debe ser 1900 o 1904')
    elegidas,numeros,exclusiones = [],[],[]
    for numero,fila in enumerate(filas,1):
        original = fila.get('fecha_pago')
        try:
            fecha = interpretar_fecha(original,sistema_excel)
        except ValueError as error:
            exclusiones.append({'fuente':fuente,'fila':numero,'id_cheque':fila.get('id_cheque'),'fecha_original':original,
                                'tipo':'FECHA_INVALIDA','motivo':str(error)})
            continue
        if periodo.contiene(fecha):
            elegidas.append(fila)
            numeros.append(numero)
        else:
            exclusiones.append({'fuente':fuente,'fila':numero,'fecha':mostrar_fecha(fecha),
                                'tipo':'FUERA_PERIODO','motivo':'Fecha de pago fuera del período elegido'})
    return elegidas,numeros,{'registros_leidos':len(filas),'dentro_periodo':len(elegidas),
                            'fuera_periodo':sum(e['tipo']=='FUERA_PERIODO' for e in exclusiones),
                            'fecha_no_interpretable':sum(e['tipo']=='FECHA_INVALIDA' for e in exclusiones),
                            'exclusiones':exclusiones}

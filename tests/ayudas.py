from src.validaciones import limpiar_registros
from src.conciliacion import conciliar
from src.pipeline import resumir


def fila(codigo='ECH-000000000001',importe='100.00',fecha='2026-11-15',**otros):
    return dict({'id_cheque':codigo,'importe':importe,'fecha_pago':fecha,'emisor':'Emisor ficticio','estado':'EMITIDO'},**otros)


def flujo(banco,sistema):
    b=limpiar_registros(banco,'banco')
    s=limpiar_registros(sistema,'sistema')
    r=conciliar(b,s)
    return r,resumir(b,s,r)

"""Datos ECHEQ ficticios, deterministas: no representan operaciones reales."""
import argparse
import copy
import csv
from datetime import date, timedelta
from decimal import Decimal
import json
from pathlib import Path
import random

SEMILLA = 20261018
FECHA_GENERACION = '18/10/2026'
CAMPOS = ['id_cheque', 'importe', 'fecha_pago', 'emisor', 'estado']


def generar(semilla=SEMILLA):
    azar = random.Random(semilla)
    ids = [f'ECH-{n:012d}' for n in azar.sample(range(100000000000, 700000000000), 120)]
    base = [{'id_cheque': codigo, 'importe': format(Decimal(azar.randint(10000, 100000000))/100,'.2f'),
             'fecha_pago': (date(2026, 11, 1)+timedelta(days=i % 60)).isoformat(),
             'emisor': f'Emisor ficticio {i+1:03d}', 'estado': 'EMITIDO'} for i, codigo in enumerate(ids)]
    banco, sistema = copy.deepcopy(base), copy.deepcopy(base)
    sistema[0]['emisor'] = 'Endosante ficticio diferente'
    sistema[0]['estado'] = 'ENDOSADO'
    sistema[1]['id_cheque'] = ' '+sistema[1]['id_cheque'].lower()+' '
    sistema[1]['importe'] = sistema[1]['importe'].replace('.', ',')
    for i in range(80, 85):
        sistema[i]['importe'] = str(Decimal(sistema[i]['importe'])+Decimal('100.25'))
    for i in range(85, 90):
        sistema[i]['fecha_pago'] = (date.fromisoformat(sistema[i]['fecha_pago'])+timedelta(days=1)).isoformat()
    for i in range(90, 95):
        sistema[i]['importe'] = str(Decimal(sistema[i]['importe'])-Decimal('50.00'))
        sistema[i]['fecha_pago'] = (date.fromisoformat(sistema[i]['fecha_pago'])+timedelta(days=2)).isoformat()
    for i in range(105, 110):
        prefijo = ids[i][:12]
        if sum(c.startswith(prefijo) for c in ids) != 1:
            raise ValueError('La semilla generó un prefijo no único')
        sistema[i]['id_cheque'] = prefijo
    banco.append(copy.deepcopy(banco[110]))
    sistema.append(dict(sistema[111], importe=str(Decimal(sistema[111]['importe'])+1)))
    banco[112]['importe'] = '-100.00'
    sistema[113]['importe'] = ''
    sistema[114]['importe'] = 'no-numérico'
    banco[115]['fecha_pago'] = '2026-02-30'
    sistema[116]['id_cheque'] = ''
    sistema[117]['importe'] = '-1.00'
    sistema[117]['fecha_pago'] = '2026-13-01'
    sistema[118]['emisor'] = ''
    sistema[119]['estado'] = ''
    banco = [f for i, f in enumerate(banco) if i not in range(95,100)]
    sistema = [f for i, f in enumerate(sistema) if i not in range(100,105)]
    def fila(codigo):
        return {'id_cheque': codigo, 'importe': '1250.35', 'fecha_pago': '2026-12-15',
                'emisor': 'Emisor ficticio adicional', 'estado': 'EMITIDO'}
    banco.extend(fila(c) for c in ['ECH-777777000001','ECH-777777000002','ECH-888888123456','ECH-000000000001'])
    sistema.extend(fila(c) for c in ['ECH-777777','ECH-888888','ECH-888888123','ECH-000000000001'])
    # La muestra se entrega en día/mes/año, también sus casos inválidos deliberados.
    for registro in banco+sistema:
        registro['fecha_pago'] = '/'.join(reversed(registro['fecha_pago'].split('-')))
    return banco, sistema


def guardar(destino, semilla=SEMILLA):
    destino = Path(destino)
    destino.mkdir(parents=True, exist_ok=True)
    banco, sistema = generar(semilla)
    for nombre, filas in [('banco',banco),('sistema',sistema)]:
        with (destino/f'{nombre}.csv').open('w', encoding='utf-8-sig', newline='') as archivo:
            escritor = csv.DictWriter(archivo,fieldnames=CAMPOS)
            escritor.writeheader()
            escritor.writerows(filas)
        (destino/f'{nombre}.json').write_text(json.dumps(filas,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Semilla {semilla}; banco: {len(banco)} filas; sistema: {len(sistema)} filas')


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--salida',default='data')
    parser.add_argument('--semilla',type=int,default=SEMILLA)
    args=parser.parse_args()
    guardar(args.salida,args.semilla)

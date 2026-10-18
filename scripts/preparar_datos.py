"""Preparar extractos sin inventar nutrientes. Ver data/README.md."""
import csv
import gzip
import json
import sys
from pathlib import Path

CAMPOS = ['codigo', 'nombre', 'categorias', 'tipo', 'base_g', 'energia',
          'unidad_energia', 'proteinas', 'carbohidratos', 'grasas', 'unidad_masa']


def preparar(ciqual, off, destino):
    filas = []
    with open(ciqual, encoding='utf-8-sig') as archivo:
        for f in csv.DictReader(archivo, delimiter='\t'):
            claves = ['Energy, Regulation EU No 1169/2011 (kcal/100g)',
                      'Protein (g/100g)', 'Carbohydrate (g/100g)', 'Fat (g/100g)']
            valores = [f[k].replace(',', '.') for k in claves]
            try:
                list(map(float, valores))
            except ValueError:
                continue
            filas.append(dict(zip(CAMPOS, [
                'CIQ-' + f['alim_code'], f['alim_nom_eng'],
                '|'.join(filter(None, [f['alim_grp_nom_eng'], f['alim_ssgrp_nom_eng']])),
                'alimento', '100', valores[0], 'kcal', *valores[1:], 'g'])))
            if len(filas) == 60:
                break
    with gzip.open(off, 'rt', encoding='utf-8') as archivo:
        for linea in archivo:
            if not linea.strip():
                continue
            f = json.loads(linea)
            n = f.get('nutriments', {})
            # Solo sólidos: no convertir ml a g sin densidad.
            if f.get('code') == '4061458010702':
                continue
            filas.append(dict(zip(CAMPOS, [
                str(f['code']), f['product_name'], '|'.join(f.get('categories_tags', [])),
                'etiqueta', '100', n.get('energy-kcal_100g', ''), 'kcal',
                n.get('proteins_100g', ''), n.get('carbohydrates_100g', ''),
                n.get('fat_100g', ''), 'g'])))
    filas = [{k: str(v) for k, v in fila.items()} for fila in filas]
    destino = Path(destino)
    destino.mkdir(parents=True, exist_ok=True)
    with (destino / 'productos.csv').open('w', encoding='utf-8', newline='') as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=CAMPOS)
        escritor.writeheader()
        escritor.writerows(filas)
    (destino / 'productos.json').write_text(json.dumps(filas, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(f'{len(filas)} observaciones preparadas')


if __name__ == '__main__':
    preparar(*sys.argv[1:])

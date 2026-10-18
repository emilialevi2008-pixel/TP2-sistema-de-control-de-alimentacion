from decimal import Decimal
import json
from pathlib import Path
import tempfile
import unittest
from src.fuentes import FuenteDatos,FuenteCSV,FuenteJSON,cargar

RAIZ=Path(__file__).resolve().parents[1]


class FuentesTest(unittest.TestCase):
    def test_abstraccion(self):
        with self.assertRaises(TypeError): FuenteDatos()
        self.assertIsInstance(FuenteCSV(),FuenteDatos)
        self.assertIsInstance(FuenteJSON(),FuenteDatos)

    def test_csv_json_equivalentes_y_ids_textuales(self):
        for fuente in ['banco','sistema']:
            with self.subTest(fuente=fuente):
                a=cargar(RAIZ/f'data/{fuente}.csv');b=cargar(RAIZ/f'data/{fuente}.json')
                self.assertEqual(a,b)
                self.assertGreaterEqual(len(a),100)
                self.assertIn('ECH-000000000001',[r['id_cheque'] for r in a])

    def test_archivo_inexistente(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(FileNotFoundError): cargar(Path(d)/'no.csv')

    def test_csv_malformados(self):
        casos=['id_cheque,id_cheque\na,b\n','a,b\n1,2,3\n','a,b\n1\n','a,b\n"sin cerrar,2\n']
        with tempfile.TemporaryDirectory() as d:
            ruta=Path(d)/'mal.csv'
            for caso in casos:
                with self.subTest(caso=caso):
                    ruta.write_text(caso)
                    with self.assertRaises(ValueError): cargar(ruta)

    def test_json_malformados(self):
        casos=['{','{}','[1]','[{"a":1,"a":2}]','[{"importe":NaN}]']
        with tempfile.TemporaryDirectory() as d:
            ruta=Path(d)/'mal.json'
            for caso in casos:
                with self.subTest(caso=caso):
                    ruta.write_text(caso)
                    with self.assertRaises(ValueError): cargar(ruta)

    def test_archivos_vacios(self):
        with tempfile.TemporaryDirectory() as d:
            for nombre,contenido in [('a.csv',''),('b.csv','id_cheque,importe\n'),('a.json',''),('b.json','[]')]:
                with self.subTest(nombre=nombre):
                    ruta=Path(d)/nombre;ruta.write_text(contenido)
                    with self.assertRaises(ValueError): cargar(ruta)

    def test_json_numerico_decimal_sin_float(self):
        with tempfile.TemporaryDirectory() as d:
            ruta=Path(d)/'a.json';ruta.write_text('[{"importe":0.10}]')
            self.assertIsInstance(cargar(ruta)[0]['importe'],Decimal)
            self.assertEqual(cargar(ruta)[0]['importe'],Decimal('0.10'))

    def test_formato_no_admitido(self):
        with self.assertRaisesRegex(ValueError,'Formato'): cargar('a.xlsx')

import csv
from decimal import Decimal
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from scripts.generar_datos import guardar
from src.fuentes import cargar
from src.pipeline import ejecutar
from src.reportes import COLUMNAS,NOMBRES,guardar_reportes,decimal_json
from tests.ayudas import fila,flujo

RAIZ=Path(__file__).resolve().parents[1]


def ejecutar_muestra(banco,sistema):
    return ejecutar(banco,sistema,'01/01/2026','31/12/2026')


class PipelineTest(unittest.TestCase):
    def test_integracion_csv_json_mixtos_y_cuatro_reportes_equivalentes(self):
        with tempfile.TemporaryDirectory() as d:
            referencia=None
            for i,(b,s) in enumerate([('csv','csv'),('json','json'),('csv','json'),('json','csv')]):
                with self.subTest(banco=b,sistema=s):
                    r,resumen=ejecutar_muestra(RAIZ/f'data/banco.{b}',RAIZ/f'data/sistema.{s}')
                    destino=Path(d)/str(i)
                    guardar_reportes(r,resumen,destino)
                    self.assertEqual({p.name for p in destino.iterdir()},set(NOMBRES))
                    archivos={nombre:(destino/nombre).read_bytes() for nombre in NOMBRES}
                    if referencia is None: referencia=archivos
                    self.assertEqual(archivos,referencia)

    def test_totales_y_estados_de_muestra_de_referencia(self):
        _,s=ejecutar_muestra(RAIZ/'data/banco.csv',RAIZ/'data/sistema.csv')
        self.assertEqual(s['importes']['total_banco'],Decimal('50477968.91'))
        self.assertEqual(s['importes']['total_sistema'],Decimal('50070182.54'))
        self.assertEqual(s['importes']['diferencia_banco_sistema'],Decimal('407786.37'))
        self.assertEqual(s['importes']['importe_conciliado'],Decimal('40522469.11'))
        self.assertEqual(s['cheques_conciliados'],86)
        self.assertEqual(s['cheques_con_diferencias'],15)
        self.assertEqual(s['cheques_sin_correspondencia'],13)
        self.assertEqual(s['pendientes_revision'],23)
        self.assertEqual(s['cheques_ambiguos'],3)

    def test_conservacion_de_240_registros_y_conteos(self):
        r,s=ejecutar_muestra(RAIZ/'data/banco.csv',RAIZ/'data/sistema.csv')
        for fuente in ['banco','sistema']:
            filas=[getattr(x,fuente).fila for x in r if getattr(x,fuente) is not None]
            excluidas=[e['fila'] for e in s['filtrado'][fuente]['exclusiones']]
            self.assertEqual(sorted(filas+excluidas),list(range(1,121)))
            self.assertEqual(len(filas),119)
        pares=s['cheques_conciliados']+s['cheques_con_diferencias']
        self.assertEqual(2*pares+s['cheques_sin_correspondencia']+s['pendientes_revision']+2,240)
        self.assertEqual(pares+s['cheques_sin_correspondencia']+s['pendientes_revision'],s['total_resultados'])

    def test_reproducibilidad_de_datos_y_analisis(self):
        with tempfile.TemporaryDirectory() as d:
            guardar(d)
            for nombre in ['banco.csv','sistema.csv','banco.json','sistema.json']:
                self.assertEqual((Path(d)/nombre).read_bytes(),(RAIZ/'data'/nombre).read_bytes())
            a=ejecutar_muestra(Path(d)/'banco.csv',Path(d)/'sistema.json')[1]
            b=ejecutar_muestra(Path(d)/'banco.csv',Path(d)/'sistema.json')[1]
            self.assertEqual(a,b)

    def test_coherencia_resumen_detalle_errores_y_dos_errores(self):
        r,s=flujo([fila(),fila('ECH-000000000002','50')],
                  [fila(),fila('ECH-000000000002','60',fecha='2026-11-20')])
        with tempfile.TemporaryDirectory() as d:
            guardar_reportes(r,s,d)
            def leer(nombre):
                with (Path(d)/nombre).open(encoding='utf-8-sig',newline='') as f:
                    return list(csv.DictReader(f,delimiter=';'))
            todo=leer('reporte_conciliacion.csv');errores=leer('cheques_con_errores.csv')
            self.assertEqual(len(todo),s['total_resultados'])
            self.assertEqual(len(errores),1)
            self.assertEqual(tuple(todo[0]),COLUMNAS)
            self.assertEqual(set(errores[0]['tipo_error'].split('|')),{'ERROR_IMPORTE','ERROR_FECHA'})
            self.assertEqual(errores[0]['diferencia_importe'],'-10.00')
            j=json.loads((Path(d)/'resumen.json').read_text())
            m=leer('resumen_importes.csv')[0]
            for clave,valor in j['importes'].items():
                self.assertEqual(str(valor),m[clave])
            self.assertEqual(j['importes']['total_banco'],'150.00')
            self.assertEqual(j['importes']['importe_con_diferencias_banco'],'50.00')

    def test_monetarios_json_cadenas_y_csv_utf8_bom(self):
        r,s=flujo([fila(importe='0.10')],[fila(importe='0.20')])
        with tempfile.TemporaryDirectory() as d:
            guardar_reportes(r,s,d)
            j=json.loads((Path(d)/'resumen.json').read_text())
            for clave in ['total_banco','total_sistema','diferencia_banco_sistema','diferencia_absoluta','importe_conciliado']:
                self.assertIsInstance(j['importes'][clave],str)
                self.assertRegex(j['importes'][clave],r'^-?[0-9]+\.[0-9]{2}$')
            for nombre in NOMBRES:
                if nombre.endswith('.csv'):
                    self.assertTrue((Path(d)/nombre).read_bytes().startswith(b'\xef\xbb\xbf'))

    def test_todas_invalidas_conservan_auditoria_y_reportes(self):
        r,s=flujo([fila(importe='')],[fila(importe='-1',fecha='mal')])
        self.assertEqual(s['importes']['total_banco'],Decimal('0.00'))
        self.assertEqual(s['registros_invalidos'],{'banco':1,'sistema':1})
        self.assertEqual(len(s['auditoria']),2)
        with tempfile.TemporaryDirectory() as d:
            guardar_reportes(r,s,d)
            self.assertEqual(len(list(Path(d).iterdir())),4)

    def test_no_sobrescribir_archivo_entrada(self):
        r,s=flujo([fila()],[fila()])
        with tempfile.TemporaryDirectory() as d:
            entrada=Path(d)/'resumen.json';entrada.write_text('[]')
            with self.assertRaisesRegex(ValueError,'sobrescribiría'):
                guardar_reportes(r,s,d,(entrada,))
            self.assertEqual(entrada.read_text(),'[]')

    def test_reportes_repetidos_no_acumulan_y_preservan_otros_archivos(self):
        r,s=flujo([fila()],[fila()])
        with tempfile.TemporaryDirectory() as d:
            extra=Path(d)/'no_tocar.txt';extra.write_text('conservar')
            guardar_reportes(r,s,d)
            antes={n:(Path(d)/n).read_bytes() for n in NOMBRES}
            guardar_reportes(r,s,d)
            self.assertEqual(antes,{n:(Path(d)/n).read_bytes() for n in NOMBRES})
            self.assertEqual(extra.read_text(),'conservar')

    def test_cli_real_y_error_de_lectura(self):
        with tempfile.TemporaryDirectory() as d:
            proceso=subprocess.run([sys.executable,'-m','src.main','--banco','data/banco.json','--sistema','data/sistema.csv','--salida',d,'--desde','01/01/2026','--hasta','31/12/2026'],cwd=RAIZ,capture_output=True,text=True)
            self.assertEqual(proceso.returncode,0,proceso.stderr)
            self.assertIn('$407.786,37',proceso.stdout)
            self.assertEqual({p.name for p in Path(d).iterdir()},set(NOMBRES))
            antes=(Path(d)/'resumen.json').read_bytes()
            fallo=subprocess.run([sys.executable,'-m','src.main','--banco',str(Path(d)/'ausente.csv'),'--salida',d,'--desde','01/01/2026','--hasta','31/12/2026'],cwd=RAIZ,capture_output=True,text=True)
            self.assertEqual(fallo.returncode,2)
            self.assertIn('Error:',fallo.stderr)
            self.assertEqual((Path(d)/'resumen.json').read_bytes(),antes)

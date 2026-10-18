import csv
from decimal import Decimal
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from src.pipeline import ejecutar
from src.reportes import guardar_reportes
from tests.ayudas import fila

RAIZ=Path(__file__).resolve().parents[1]


class PeriodosTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.raiz=Path(self.tmp.name)
        self.b=self.raiz/'b.json';self.s=self.raiz/'s.json'

    def datos(self,banco,sistema):
        self.b.write_text(json.dumps(banco),encoding='utf-8')
        self.s.write_text(json.dumps(sistema),encoding='utf-8')

    def correr(self,inicio,fin,**opciones):
        return ejecutar(self.b,self.s,inicio,fin,**opciones)

    def test_limites_inclusivos_entre_anios_totales_y_ordinales(self):
        fechas=['17/12/2026','18/12/2026','31/12/2026','18/02/2027','19/02/2027']
        banco=[fila(f'ECH-{i+1:012d}',str((i+1)*10),f) for i,f in enumerate(fechas)]
        sistema=[dict(f) for f in banco]
        sistema[1]['fecha_pago']='2026-12-18'
        self.datos(banco,sistema)
        r,s=self.correr('18/12/2026','18/02/2027')
        self.assertEqual([x.banco.fila for x in r],[2,3,4])
        self.assertEqual(s['cheques_conciliados'],3)
        self.assertEqual(s['importes']['total_banco'],Decimal('90.00'))
        self.assertEqual(s['filtrado']['banco']['fuera_periodo'],2)
        self.assertEqual(s['periodo'],{'inicio':'18/12/2026','fin':'18/02/2027','limites_incluidos':True})

    def test_otro_periodo_no_reutiliza_fechas_anteriores(self):
        datos=[fila(fecha='18/10/2026'),fila('ECH-000000000002','20',fecha='15/04/2027')]
        self.datos(datos,datos)
        self.assertEqual(self.correr('18/10/2026','18/12/2026')[1]['importes']['total_banco'],Decimal('100.00'))
        self.assertEqual(self.correr('01/03/2027','15/04/2027')[1]['importes']['total_banco'],Decimal('20.00'))

    def test_un_dia_y_periodo_sin_resultados(self):
        self.datos([fila(fecha='18/10/2026')],[fila(fecha='2026-10-18')])
        self.assertEqual(self.correr('18/10/2026','18/10/2026')[1]['cheques_conciliados'],1)
        r,s=self.correr('01/03/2027','15/04/2027')
        self.assertEqual(r,[])
        self.assertEqual(s['importes']['total_banco'],Decimal('0.00'))
        self.assertIn('No hay registros',s['mensaje'])
        guardar_reportes(r,s,self.raiz/'salida')
        self.assertTrue((self.raiz/'salida/resumen.json').exists())

    def test_fecha_invalida_no_se_suma_y_queda_identificada(self):
        datos=[fila(fecha='31/02/2026'),fila('ECH-000000000002','20',fecha='18/10/2026')]
        self.datos(datos,datos)
        r,s=self.correr('01/01/2026','31/12/2026')
        self.assertEqual(s['importes']['total_banco'],Decimal('20.00'))
        self.assertEqual(s['filtrado']['banco']['fecha_no_interpretable'],1)
        rechazo=s['filtrado']['banco']['exclusiones'][0]
        self.assertEqual(rechazo['fila'],1)
        self.assertEqual(rechazo['tipo'],'FECHA_INVALIDA')
        self.assertTrue(rechazo['motivo'])
        self.assertEqual(r[0].banco.fila,2)

    def test_excel_de_fuentes_con_sistemas_distintos(self):
        self.datos([fila(fecha=46313)],[fila(fecha='44851')])
        r,s=self.correr('18/10/2026','18/10/2026',excel_sistema='1904')
        self.assertEqual(s['cheques_conciliados'],1)
        self.assertEqual(r[0].sistema.normalizado['fecha_pago'],'18/10/2026')

    def test_diferencias_y_ausencias_solo_en_periodo(self):
        self.datos([fila(importe='120',fecha='18/10/2026'),fila('ECH-000000000002','5',fecha='19/10/2026')],
                   [fila(importe='100',fecha='19/10/2026'),fila('ECH-000000000003','7',fecha='18/10/2026')])
        r,s=self.correr('18/10/2026','19/10/2026')
        self.assertEqual(s['cheques_con_diferencias'],1)
        self.assertEqual(r[0].tipos,['ERROR_IMPORTE','ERROR_FECHA'])
        self.assertEqual(s['cheques_sin_correspondencia'],2)
        self.assertIn('18/10/2026',r[0].descripcion)
        _,uno=self.correr('18/10/2026','18/10/2026')
        self.assertEqual(uno['cheques_con_diferencias'],0)
        self.assertEqual(uno['cheques_sin_correspondencia'],2)

    def test_todos_los_reportes_identifican_periodo_y_fechas_argentinas(self):
        self.datos([fila(fecha='2026-10-18')],[fila(fecha='19/10/2026')])
        r,s=self.correr('18/10/2026','19/10/2026')
        destino=self.raiz/'salida';guardar_reportes(r,s,destino)
        for nombre in ['reporte_conciliacion.csv','cheques_con_errores.csv','resumen_importes.csv']:
            with (destino/nombre).open(encoding='utf-8-sig') as f:
                datos=list(csv.DictReader(f,delimiter=';'))
            self.assertEqual(datos[0]['periodo_inicio'],'18/10/2026')
            self.assertEqual(datos[0]['periodo_fin'],'19/10/2026')
            if nombre!='resumen_importes.csv':
                self.assertEqual(datos[0]['fecha_banco'],'18/10/2026')
                self.assertEqual(datos[0]['fecha_sistema'],'19/10/2026')
        resumen=json.loads((destino/'resumen.json').read_text())
        self.assertEqual(resumen['periodo']['inicio'],'18/10/2026')
        # Solo los originales de auditoría mantienen exactamente el formato recibido.
        self.assertEqual(resumen['auditoria'][0]['original']['fecha_pago'],'2026-10-18')
        self.assertEqual(resumen['auditoria'][0]['normalizado']['fecha_pago'],'18/10/2026')

    def test_cli_solicita_periodo_y_no_lo_predetermina(self):
        self.datos([fila(fecha='18/10/2026')],[fila(fecha='18/10/2026')])
        comando=[sys.executable,'-m','src.main','--banco',str(self.b),'--sistema',str(self.s),'--salida',str(self.raiz/'salida')]
        r=subprocess.run(comando,input='18/10/2026\n18/10/2026\n',capture_output=True,text=True,cwd=RAIZ)
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertIn('Fecha de inicio',r.stdout)
        self.assertIn('18/10/2026 al 18/10/2026',r.stdout)
        r=subprocess.run(comando,input='',capture_output=True,text=True,cwd=RAIZ)
        self.assertEqual(r.returncode,2)
        self.assertIn('Faltan fechas',r.stderr)

    def test_cli_periodo_invertido_incompleto_o_no_argentino(self):
        for args in [['--desde','19/10/2026','--hasta','18/10/2026'],['--desde','18/10/2026'],
                     ['--desde','2026-10-18','--hasta','18/12/2026']]:
            with self.subTest(args=args):
                r=subprocess.run([sys.executable,'-m','src.main',*args],capture_output=True,text=True,input='',cwd=RAIZ)
                self.assertEqual(r.returncode,2)
                self.assertIn('Error:',r.stderr)

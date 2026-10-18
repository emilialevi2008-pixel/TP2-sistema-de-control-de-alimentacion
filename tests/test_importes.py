from decimal import Decimal
import unittest
from tests.ayudas import fila,flujo


class ImportesTest(unittest.TestCase):
    def test_total_banco_sistema_diferencia_y_absoluta(self):
        _,s=flujo([fila(importe='10.10'),fila('ECH-000000000002',importe='20.20')],
                  [fila(importe='40.40'),fila('ECH-000000000002',importe='0.00')])
        m=s['importes']
        self.assertEqual(m['total_banco'],Decimal('30.30'))
        self.assertEqual(m['total_sistema'],Decimal('40.40'))
        self.assertEqual(m['diferencia_banco_sistema'],Decimal('-10.10'))
        self.assertEqual(m['diferencia_absoluta'],Decimal('10.10'))

    def test_precision_decimal(self):
        _,s=flujo([fila(importe='0.10'),fila('ECH-000000000002',importe='0.20')],
                  [fila(importe='0.10'),fila('ECH-000000000002',importe='0.20')])
        self.assertEqual(s['importes']['total_banco'],Decimal('0.30'))
        self.assertIsInstance(s['importes']['total_banco'],Decimal)

    def test_duplicados_incluidos_en_bruto_no_en_conciliado(self):
        _,s=flujo([fila(importe='10'),fila(importe='20')],[fila(importe='10')])
        self.assertEqual(s['importes']['total_banco'],Decimal('30.00'))
        self.assertEqual(s['importes']['importe_conciliado'],Decimal('0.00'))
        self.assertEqual(s['totales_brutos']['banco']['duplicados_incluidos'],[1,2])

    def test_importes_invalidos_excluidos_y_documentados(self):
        banco=[fila('ECH-000000000001','-1'),fila('ECH-000000000002',''),
               fila('ECH-000000000003','abc'),fila('ECH-000000000004','2.50')]
        _,s=flujo(banco,[fila('ECH-000000000004','2.50')])
        self.assertEqual(s['importes']['total_banco'],Decimal('2.50'))
        self.assertEqual(s['totales_brutos']['banco']['incluidos'],1)
        excluidos=s['registros_excluidos_sumas']['banco']
        self.assertEqual([r['fila'] for r in excluidos],[1,2,3])
        self.assertTrue(all(r['motivo'] for r in excluidos))

    def test_fecha_o_id_invalidos_no_excluyen_importe_valido(self):
        _,s=flujo([fila(codigo='',importe='10'),fila('ECH-000000000002',importe='20',fecha='mal')],[fila()])
        self.assertEqual(s['importes']['total_banco'],Decimal('30.00'))
        self.assertEqual(s['importes']['registros_excluidos_banco'],0)
        self.assertEqual(s['registros_invalidos']['banco'],2)

    def test_conciliados_y_diferencias_sin_doble_conteo(self):
        b=[fila(importe='10'),fila('ECH-000000000002','20'),fila('ECH-000000000003','30')]
        c=[fila(importe='10'),fila('ECH-000000000002','25'),fila('ECH-000000000003','30',fecha='2026-11-16')]
        _,s=flujo(b,c)
        self.assertEqual(s['importes']['importe_conciliado'],Decimal('10.00'))
        self.assertEqual(s['importes']['importe_con_diferencias_banco'],Decimal('50.00'))
        self.assertEqual(s['importes']['importe_con_diferencias_sistema'],Decimal('55.00'))
        for fuente in ['banco','sistema']:
            self.assertEqual(sum(v[fuente] for v in s['importes_por_grupo'].values()),s['importes']['total_'+fuente])

    def test_errores_compensados_no_son_conciliacion(self):
        b=[fila(importe='10'),fila('ECH-000000000002','20')]
        c=[fila(importe='20'),fila('ECH-000000000002','10')]
        _,s=flujo(b,c)
        self.assertEqual(s['importes']['diferencia_banco_sistema'],Decimal('0.00'))
        self.assertEqual(s['cheques_conciliados'],0)
        self.assertEqual(s['cheques_con_diferencias'],2)

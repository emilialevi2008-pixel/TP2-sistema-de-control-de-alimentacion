from datetime import date,datetime
from decimal import Decimal
import unittest
from src.fechas import interpretar_fecha,mostrar_fecha,PeriodoConciliacion


class FechasTest(unittest.TestCase):
    def test_argentina_iso_y_medianoche_excel(self):
        for valor in ['18/10/2026','2026-10-18','18/10/2026 00:00:00','2026-10-18T00:00:00',datetime(2026,10,18)]:
            with self.subTest(valor=valor):
                self.assertEqual(interpretar_fecha(valor),date(2026,10,18))
        self.assertEqual(interpretar_fecha('01/02/2026'),date(2026,2,1))
        self.assertEqual(mostrar_fecha(date(2026,2,1)),'01/02/2026')

    def test_excel_1900_y_1904(self):
        for valor in [46313,'46313',Decimal('46313.0'),'46313,0']:
            self.assertEqual(interpretar_fecha(valor),date(2026,10,18))
        self.assertEqual(interpretar_fecha('44851','1904'),date(2026,10,18))
        self.assertEqual(interpretar_fecha(0,'1904'),date(1904,1,1))
        self.assertEqual(interpretar_fecha(59),date(1900,2,28))
        self.assertEqual(interpretar_fecha(61),date(1900,3,1))

    def test_invalidas_ambiguas_y_horas_no_se_adivinan(self):
        for valor in ['10/18/2026','01/02/03','2026/10/18','31/02/2026','2026-02-30',
                      '20261018','46313.5','60','0','-1','NaN',True,None,
                      '18/10/2026 12:00:00','2026-10-18T00:00:00Z',datetime(2026,10,18,12)]:
            with self.subTest(valor=valor),self.assertRaises(ValueError):
                interpretar_fecha(valor)

    def test_periodo_inclusivo_libre_y_entre_anios(self):
        p=PeriodoConciliacion.desde_texto('18/12/2026','18/02/2027')
        self.assertTrue(p.contiene(date(2026,12,18)))
        self.assertTrue(p.contiene(date(2027,2,18)))
        self.assertFalse(p.contiene(date(2027,2,19)))
        self.assertEqual(p.describir()['inicio'],'18/12/2026')
        otro=PeriodoConciliacion.desde_texto('01/03/2027','15/04/2027')
        self.assertFalse(otro.contiene(date(2027,2,18)))

    def test_periodo_invertido_o_formato_incorrecto(self):
        for inicio,fin in [('19/10/2026','18/10/2026'),('2026-10-18','18/12/2026'),('31/02/2026','18/12/2026')]:
            with self.subTest(inicio=inicio),self.assertRaises(ValueError):
                PeriodoConciliacion.desde_texto(inicio,fin)

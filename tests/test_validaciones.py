import copy
from decimal import Decimal
import unittest
from src.validaciones import limpiar_registros,validar_importe
from tests.ayudas import fila


class ValidacionesTest(unittest.TestCase):
    def test_normalizacion_sin_mutar_y_auditoria(self):
        f=fila(' ech-000000000001 ',' 100,25 ',emisor=' Empresa ficticia ',estado=' emitido ')
        copia=copy.deepcopy(f)
        r=limpiar_registros([f],'sistema')[0]
        self.assertEqual(f,copia)
        self.assertTrue(r.habilitado)
        self.assertEqual(r.cheque.importe,Decimal('100.25'))
        self.assertEqual(r.codigo,'ECH-000000000001')
        self.assertEqual(r.cambios['emisor'],{'antes':' Empresa ficticia ','despues':'Empresa ficticia'})

    def test_importe_negativo(self):
        with self.assertRaisesRegex(ValueError,'negativo'): validar_importe('-0.01')

    def test_importe_vacio(self):
        for v in ['',None,' ']:
            with self.subTest(valor=v),self.assertRaises(ValueError): validar_importe(v)

    def test_importe_no_numerico_o_no_finito(self):
        for v in ['abc','NaN','Infinity',True,0.1,'1e2',{},'1.000,00']:
            with self.subTest(valor=v),self.assertRaises(ValueError): validar_importe(v)

    def test_precision_no_redondea_ocultamente(self):
        with self.assertRaises(ValueError): validar_importe('0.001')
        self.assertEqual(validar_importe('0'),Decimal('0.00'))
        self.assertEqual(validar_importe('001,20'),Decimal('1.20'))
        with self.assertRaises(ValueError): validar_importe('1000000000000000.00')

    def test_fecha_imposible_y_formato(self):
        for fecha in ['2026-02-30','2026-13-01','2025-02-29','2026-1-01','20261115',None]:
            with self.subTest(fecha=fecha):
                r=limpiar_registros([fila(fecha=fecha)],'banco')[0]
                self.assertIn('FECHA_INVALIDA',r.errores)
                self.assertIsNotNone(r.importe)
        self.assertTrue(limpiar_registros([fila(fecha='2024-02-29')],'banco')[0].habilitado)

    def test_identificador_invalido_y_cero_inicial(self):
        for codigo in ['',None,12345678,'ECH-12345','ECH-1234567890123','ECH-１２３４５６','xECH-123456']:
            with self.subTest(codigo=codigo):
                r=limpiar_registros([fila(codigo)],'banco')[0]
                self.assertIn('ID_INVALIDO',r.errores)
                self.assertIsNone(r.codigo)
        self.assertEqual(limpiar_registros([fila()],'banco')[0].codigo,'ECH-000000000001')

    def test_campos_faltantes_y_obligatorios(self):
        for campo in ['id_cheque','importe','fecha_pago','emisor','estado']:
            with self.subTest(campo=campo):
                f=fila();f.pop(campo)
                r=limpiar_registros([f],'sistema')[0]
                self.assertIn('CAMPOS_FALTANTES',r.errores)
                self.assertIsNone(r.cheque)
        r=limpiar_registros([fila(emisor='',estado='')],'banco')[0]
        self.assertEqual(r.errores.count('CAMPO_OBLIGATORIO'),2)

    def test_deteccion_duplicados_incluye_fila_invalida(self):
        registros=limpiar_registros([fila(),fila(fecha='fecha rota')],'banco')
        self.assertTrue(all(r.duplicado for r in registros))
        self.assertFalse(any(r.habilitado for r in registros))

    def test_multiples_errores_invalidos(self):
        r=limpiar_registros([fila(importe='-1',fecha='2026-02-30')],'sistema')[0]
        self.assertEqual(r.errores,['IMPORTE_INVALIDO','FECHA_INVALIDA'])

    def test_errores_de_esquema_y_fuente(self):
        for entradas,fuente in [([], 'banco'),([1],'banco'),([fila()],'otra')]:
            with self.subTest(fuente=fuente),self.assertRaises(ValueError): limpiar_registros(entradas,fuente)
        r=limpiar_registros([dict(fila(),campo_extra='x')],'banco')[0]
        self.assertIn('CAMPOS_INESPERADOS',r.errores)

import unittest
from src.conciliacion import verificar_trazabilidad
from src.validaciones import limpiar_registros
from tests.ayudas import fila,flujo


class ConciliacionTest(unittest.TestCase):
    def test_coincidencia_exacta(self):
        r,s=flujo([fila()],[fila()])
        self.assertEqual(len(r),1)
        self.assertEqual(r[0].estado,'CONCILIADO')
        self.assertEqual(s['cheques_conciliados'],1)

    def test_prefijo_unico_valido(self):
        r,_=flujo([fila('ECH-123456789012')],[fila('ECH-123456')])
        self.assertEqual(r[0].estado,'CONCILIADO_ID_ABREVIADO')
        self.assertEqual(r[0].banco.fila,1)
        self.assertEqual(r[0].sistema.fila,1)

    def test_prefijo_ambiguo(self):
        r,s=flujo([fila('ECH-123456000001'),fila('ECH-123456000002')],[fila('ECH-123456')])
        self.assertEqual(s['cheques_ambiguos'],1)
        self.assertEqual(s['cheques_conciliados'],0)
        ambiguo=next(x for x in r if x.estado=='COINCIDENCIA_AMBIGUA')
        self.assertEqual(len(ambiguo.candidatos),2)
        self.assertEqual([x.estado for x in r if x.banco],['PENDIENTE_REVISION']*2)

    def test_error_importe(self):
        r,_=flujo([fila(importe='120.25')],[fila(importe='100.00')])
        self.assertEqual(r[0].estado,'ERROR_IMPORTE')
        self.assertEqual(r[0].banco.cheque.diferencia_importe(r[0].sistema.cheque).as_tuple().exponent,-2)
        self.assertIn('$20,25',r[0].descripcion)

    def test_error_fecha(self):
        r,_=flujo([fila()],[fila(fecha='2026-11-20')])
        self.assertEqual(r[0].estado,'ERROR_FECHA')
        self.assertIn('15/11/2026',r[0].descripcion)
        self.assertIn('20/11/2026',r[0].descripcion)

    def test_error_importe_y_fecha_simultaneos(self):
        r,s=flujo([fila()],[fila(importe='120',fecha='2026-11-20')])
        self.assertEqual(r[0].estado,'CON_DIFERENCIAS')
        self.assertEqual(r[0].tipos,['ERROR_IMPORTE','ERROR_FECHA'])
        self.assertEqual(s['cheques_con_diferencias'],1)

    def test_ausentes_en_ambas_fuentes(self):
        r,s=flujo([fila('ECH-111111000001')],[fila('ECH-222222000001')])
        self.assertEqual({x.estado for x in r},{'NO_ESTA_EN_BANCO','NO_ESTA_EN_SISTEMA'})
        self.assertEqual(s['cheques_sin_correspondencia'],2)

    def test_duplicado_no_se_concilia(self):
        for banco,sistema in [([fila(),fila()],[fila()]),([fila()],[fila(),fila()])]:
            with self.subTest(lado=len(banco)):
                r,s=flujo(banco,sistema)
                self.assertEqual(s['cheques_conciliados'],0)
                self.assertEqual(sum(x.estado=='ID_DUPLICADO' for x in r),2)
                self.assertEqual(sum(x.estado=='PENDIENTE_REVISION' for x in r),1)

    def test_emisor_y_estado_no_son_reglas_de_error(self):
        r,_=flujo([fila()],[fila(emisor='Otro endosante ficticio',estado='ENDOSADO')])
        self.assertEqual(r[0].estado,'CONCILIADO')

    def test_exactos_antes_de_prefijos_y_no_reutilizacion(self):
        b=[fila('ECH-123456789012')]
        s=[fila('ECH-123456'),fila('ECH-123456789012')]
        for entradas in [s,list(reversed(s))]:
            r,resumen=flujo(b,entradas)
            self.assertEqual(resumen['cheques_conciliados'],1)
            par=next(x for x in r if x.banco is not None)
            self.assertEqual(par.sistema.codigo,'ECH-123456789012')
            self.assertIn('BANCO_YA_ASIGNADO',[t for x in r for t in x.tipos])

    def test_dos_prefijos_compiten_sin_asignacion_por_orden(self):
        b=[fila('ECH-123456789012')]
        s=[fila('ECH-123456'),fila('ECH-123456789')]
        for entradas in [s,list(reversed(s))]:
            r,resumen=flujo(b,entradas)
            self.assertEqual(resumen['cheques_conciliados'],0)
            self.assertEqual(resumen['cheques_ambiguos'],2)
            self.assertEqual(sum(x.banco is not None for x in r),1)

    def test_candidato_invalido_no_fabrica_prefijo_unico(self):
        b=[fila('ECH-123456000001'),fila('ECH-123456000002',importe='-1')]
        r,s=flujo(b,[fila('ECH-123456')])
        self.assertEqual(s['cheques_ambiguos'],1)
        self.assertEqual(s['cheques_conciliados'],0)

    def test_contraparte_invalida_no_se_declara_ausente(self):
        for b,s in [([fila(fecha='mal')],[fila()]),([fila()],[fila(fecha='mal')])]:
            r,resumen=flujo(b,s)
            self.assertEqual(resumen['cheques_sin_correspondencia'],0)
            self.assertEqual(resumen['pendientes_revision'],2)

    def test_prefijo_unico_a_duplicado_bloqueado(self):
        r,s=flujo([fila('ECH-123456789012'),fila('ECH-123456789012')],[fila('ECH-123456')])
        self.assertEqual(s['cheques_conciliados'],0)
        self.assertIn('CONTRAPARTE_INVALIDA',[t for x in r for t in x.tipos])

    def test_trazabilidad_detecta_doble_uso(self):
        b=limpiar_registros([fila()],'banco');s=limpiar_registros([fila()],'sistema')
        r,_=flujo([fila()],[fila()])
        with self.assertRaisesRegex(ValueError,'uno a uno'):
            verificar_trazabilidad(r+r,b,s)

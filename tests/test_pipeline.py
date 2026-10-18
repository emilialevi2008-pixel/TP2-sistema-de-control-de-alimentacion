import copy
import json
from pathlib import Path
import tempfile
import unittest
from src.fuentes import FuenteDatos, FuenteCSV, FuenteJSON, cargar
from src.pipeline import (ejecutar, limpiar_datos, comparar_etiquetas, seleccionar,
                          buscar_producto, guardar_resultado)
from src.recetas import AlmacenRecetas, calcular_receta

RAIZ = Path(__file__).resolve().parents[1]


def ficha(**cambios):
    return dict({'codigo': '01234567', 'nombre': 'Prueba', 'categorias': 'cereal|desayuno',
                 'tipo': 'etiqueta', 'base_g': '100', 'energia': '100', 'unidad_energia': 'kcal',
                 'proteinas': '2', 'carbohidratos': '10', 'grasas': '3', 'unidad_masa': 'g'}, **cambios)


class PipelineTest(unittest.TestCase):
    def test_caso_normal(self):
        p, registro = limpiar_datos([ficha()])
        self.assertEqual(comparar_etiquetas(p)[0]['energia'], 100)
        self.assertEqual(p[0].codigo, '01234567')
        self.assertTrue(registro)

    def test_fuente_abstracta(self):
        with self.assertRaises(TypeError):
            FuenteDatos()
        self.assertIsInstance(FuenteCSV(), FuenteDatos)
        self.assertIsInstance(FuenteJSON(), FuenteDatos)

    def test_equivalencia_csv_json_y_repetibilidad(self):
        a, b = RAIZ/'data/productos.csv', RAIZ/'data/productos.json'
        self.assertEqual(cargar(a), cargar(b))
        self.assertEqual(ejecutar(a), ejecutar(b))
        self.assertEqual(ejecutar(a), ejecutar(a))
        self.assertGreaterEqual(ejecutar(a)['inspeccion']['validas'], 50)

    def test_conversion_conocida_y_base(self):
        p, _ = limpiar_datos([ficha(base_g='50', energia='209.2', unidad_energia='kJ', proteinas='1000', carbohidratos='2000', grasas='3000', unidad_masa='mg')])
        self.assertEqual(len(p), 1)
        self.assertAlmostEqual(p[0].nutriente_100g('energia'), 100)
        self.assertEqual(p[0].nutriente_100g('proteinas'), 2)
        self.assertEqual(p[0].ficha(50)['proteinas'], 1)

    def test_faltante_no_es_cero(self):
        p, _ = limpiar_datos([ficha(proteinas='')])
        self.assertIsNone(comparar_etiquetas(p)[0]['proteinas'])
        self.assertIsNone(comparar_etiquetas(p)[0]['diferencia_absoluta_vs_primero']['proteinas'])

    def test_invalidos_y_rangos(self):
        casos = [{'codigo':'123'}, {'codigo':'１２３４５６７８'}, {'codigo':12345678},
                 {'base_g':'0'}, {'energia':'-1'}, {'energia':'1001'}, {'proteinas':'101'},
                 {'grasas':'nan'}, {'carbohidratos':'inf'}, {'energia':True},
                 {'unidad_masa':'ml'}, {'unidad_energia':'J'}, {'nombre':''},
                 {'tipo':'receta'}, {'base_g':None}, {'energia':'abc'}]
        for cambios in casos:
            with self.subTest(cambios=cambios):
                p, registro = limpiar_datos([ficha(**cambios)])
                self.assertEqual(p, [])
                self.assertEqual(registro[0]['estado'], 'rechazada')
                self.assertTrue(registro[0]['motivo'])

    def test_esquema_invalido(self):
        for filas in [[], [{'codigo':'123'}]]:
            with self.assertRaises(ValueError):
                limpiar_datos(filas)

    def test_duplicados_y_conservacion(self):
        entradas = [ficha(), ficha(), ficha(codigo='error')]
        p, r = limpiar_datos(entradas)
        self.assertEqual(len(p), 1)
        rechazos = [i for i in r if i['estado']=='rechazada']
        self.assertEqual(len(entradas), len(p)+len(rechazos))
        self.assertIn('duplicado', rechazos[0]['motivo'])

    def test_auditoria_y_no_mutacion(self):
        entrada = ficha(nombre=' Prueba ', energia='100,5', categorias='desayuno|cereal|cereal')
        copia = copy.deepcopy(entrada)
        p, r = limpiar_datos([entrada])
        self.assertEqual(entrada, copia)
        self.assertEqual(p[0].energia, 100.5)
        self.assertEqual(r[0]['cambios']['nombre']['antes'], ' Prueba ')
        self.assertEqual(r[0]['original'], copia)

    def test_categoria_faltante(self):
        p, r = limpiar_datos([ficha(categorias='')])
        self.assertEqual(p[0].categorias, ('sin-categoria',))
        self.assertIn('categorias', r[0]['cambios'])

    def test_busqueda_y_filtros(self):
        p, _ = limpiar_datos([ficha(), ficha(codigo='01234568',nombre='Otra',energia='200')])
        self.assertEqual(buscar_producto(p,'01234567').nombre,'Prueba')
        self.assertEqual(len(seleccionar(p,categoria='desayuno')),2)
        self.assertEqual(len(seleccionar(p,texto='PRUE',max_energia=100,min_proteinas=2)),1)
        self.assertEqual(seleccionar(p,categoria='inexistente'),[])
        with self.assertRaisesRegex(ValueError,'No existe'):
            buscar_producto(p,'00000000')
        with self.assertRaises(ValueError):
            seleccionar(p,codigos=['01234567','01234567'])

    def test_diferencias_y_orden(self):
        p, _ = limpiar_datos([ficha(codigo='01234568',energia='200'),ficha()])
        t = comparar_etiquetas(p)
        self.assertEqual(t[0]['codigo'],'01234567')
        self.assertEqual(t[1]['diferencia_absoluta_vs_primero']['energia'],100)
        self.assertEqual(t[0]['diferencia_absoluta_vs_primero']['energia'],0)
        with self.assertRaises(ValueError):
            comparar_etiquetas([])

    def test_errores_lectura_no_ocultos(self):
        with tempfile.TemporaryDirectory() as d:
            ruta=Path(d)/'mal.json';ruta.write_text('{')
            with self.assertRaises(ValueError): cargar(ruta)
            ruta.write_text('{}')
            with self.assertRaisesRegex(ValueError,'lista'): cargar(ruta)
            with self.assertRaises(OSError): cargar(Path(d)/'ausente.csv')
            with self.assertRaises(ValueError): cargar(Path(d)/'algo.txt')
            ruta=Path(d)/'mal.csv';ruta.write_text('codigo,codigo\n1,2\n')
            with self.assertRaises(ValueError): cargar(ruta)

    def test_exportacion(self):
        r=ejecutar(RAIZ/'data/productos.csv')
        with tempfile.TemporaryDirectory() as d:
            guardar_resultado(r,d)
            self.assertEqual(json.loads((Path(d)/'resultado.json').read_text()),r)
            self.assertEqual(json.loads((Path(d)/'incidencias.json').read_text()),r['incidencias'])

    def test_receta_calculo_y_faltantes(self):
        p,_=limpiar_datos([ficha(),ficha(codigo='01234568',proteinas=None)])
        datos={'nombre':'Mi receta','porciones':2,'ingredientes':[{'codigo':'01234567','gramos':200}]}
        r=calcular_receta(datos,p)
        self.assertEqual(r['totales']['energia'],200)
        self.assertEqual(r['por_porcion']['energia'],100)
        self.assertEqual(r['por_100g']['energia'],100)
        datos['ingredientes'].append({'codigo':'01234568','gramos':100})
        self.assertIsNone(calcular_receta(datos,p)['totales']['proteinas'])

    def test_receta_invalida(self):
        p,_=limpiar_datos([ficha()])
        for datos in [[],{}, {'nombre':'a','porciones':0}, {'nombre':'a','porciones':1,'ingredientes':[]}, {'nombre':'a','porciones':1,'ingredientes':[{'codigo':'01234567','gramos':-1}]}]:
            with self.subTest(datos=datos), self.assertRaises(ValueError):
                calcular_receta(datos,p)

    def test_crud_persistente(self):
        p,_=limpiar_datos([ficha()])
        datos={'nombre':'a','porciones':1,'ingredientes':[{'codigo':'01234567','gramos':100}]}
        with tempfile.TemporaryDirectory() as d:
            ruta=Path(d)/'r.sqlite';a=AlmacenRecetas(ruta);r=a.guardar(datos,p)
            a=AlmacenRecetas(ruta)
            self.assertEqual(a.listar()[0]['nombre'],'a')
            a.guardar(dict(datos,nombre='b'),p,r['id'])
            self.assertEqual(a.listar()[0]['nombre'],'b')
            a.eliminar(r['id']);self.assertEqual(a.listar(),[])
            with self.assertRaises(ValueError): a.eliminar(r['id'])
            with self.assertRaises(ValueError): a.guardar(datos,p,999)


class SinResultadosTest(unittest.TestCase):
    def test_sin_coincidencias_conserva_auditoria(self):
        r=ejecutar(RAIZ/'data/productos.csv',categoria='no existe')
        self.assertEqual(r['tabla'],[])
        self.assertIn('Sin productos',r['mensaje'])
        self.assertEqual(r['inspeccion']['validas'],65)

    def test_todas_rechazadas_se_exportan(self):
        with tempfile.TemporaryDirectory() as d:
            ruta=Path(d)/'mal.json'
            ruta.write_text(json.dumps([ficha(codigo='inválido')]))
            r=ejecutar(ruta)
            self.assertEqual(r['inspeccion']['rechazadas'],1)
            guardar_resultado(r,d)
            self.assertEqual(json.loads((Path(d)/'incidencias.json').read_text())[0]['estado'],'rechazada')

    def test_limites_de_filtro_invalidos(self):
        p,_=limpiar_datos([ficha()])
        for limite in [float('nan'),float('inf'),-1]:
            with self.subTest(limite=limite), self.assertRaises(ValueError):
                seleccionar(p,max_energia=limite)


if __name__ == '__main__':
    unittest.main()

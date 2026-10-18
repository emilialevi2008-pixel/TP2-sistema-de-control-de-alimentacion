import json
from pathlib import Path
import tempfile
from threading import Thread
import unittest
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from src.web import crear_servidor


class WebTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory()
        cls.servidor=crear_servidor(puerto=0, entrada=Path(__file__).resolve().parents[1]/'data/productos.csv', almacen=Path(cls.tmp.name)/'r.sqlite')
        cls.hilo=Thread(target=cls.servidor.serve_forever,daemon=True);cls.hilo.start()
        cls.base=f'http://127.0.0.1:{cls.servidor.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.servidor.shutdown();cls.servidor.server_close();cls.hilo.join();cls.tmp.cleanup()

    def pedir(self,ruta,metodo='GET',datos=None,extra=None):
        req=Request(self.base+ruta,method=metodo,data=None if datos is None else json.dumps(datos).encode(),headers={'Content-Type':'application/json',**(extra or {})})
        with urlopen(req) as r:return r.status,r.read()

    def test_arranque_y_comparacion(self):
        estado,cuerpo=self.pedir('/')
        self.assertEqual(estado,200);self.assertIn(b'Comparaci',cuerpo)
        _,cuerpo=self.pedir('/api/productos');self.assertEqual(len(json.loads(cuerpo)['productos']),65)
        _,cuerpo=self.pedir('/api/comparar?codigo=3023290234839&codigo=3175681213081')
        tabla=json.loads(cuerpo);self.assertEqual(len(tabla),2)
        self.assertEqual(tabla[0]['porcion_g'],100)

    def test_crud_http(self):
        datos={'nombre':'HTTP','porciones':2,'ingredientes':[{'codigo':'CIQ-25001','gramos':200}]}
        estado,cuerpo=self.pedir('/api/recetas','POST',datos);self.assertEqual(estado,201)
        r=json.loads(cuerpo);identificador=r['id']
        self.pedir(f'/api/recetas/{identificador}','PUT',dict(datos,nombre='Editada'))
        _,cuerpo=self.pedir('/api/recetas');self.assertEqual(json.loads(cuerpo)[0]['nombre'],'Editada')
        self.pedir(f'/api/recetas/{identificador}','DELETE',{})
        _,cuerpo=self.pedir('/api/recetas');self.assertEqual(json.loads(cuerpo),[])

    def test_errores_http(self):
        for ruta,metodo,datos in [('/ausente','GET',None),('/api/comparar?codigo=error','GET',None),('/api/recetas','POST',{})]:
            with self.subTest(ruta=ruta), self.assertRaises(HTTPError) as error:
                self.pedir(ruta,metodo,datos)
            self.assertIn(error.exception.code,(400,404))
            self.assertIn('error',json.loads(error.exception.read()))

    def test_origen_ajeno(self):
        with self.assertRaises(HTTPError) as e:
            self.pedir('/api/recetas','POST',{}, {'Origin':'https://sitio-ajeno.invalid'})
        self.assertEqual(e.exception.code,400)

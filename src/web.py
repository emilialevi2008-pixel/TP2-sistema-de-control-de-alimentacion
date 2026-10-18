"""Servidor local sin dependencias externas. No es un servicio multiusuario."""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
from urllib.parse import urlsplit, parse_qs
from .fuentes import cargar
from .pipeline import limpiar_datos, seleccionar, comparar_etiquetas
from .recetas import AlmacenRecetas, calcular_receta


def crear_servidor(host='127.0.0.1', puerto=8000, entrada='data/productos.csv', almacen='local/recetas.sqlite'):
    productos, incidencias = limpiar_datos(cargar(entrada))
    if not productos:
        raise ValueError('El catálogo no tiene fichas válidas')
    recetas = AlmacenRecetas(almacen)

    class Handler(BaseHTTPRequestHandler):
        def responder(self, estado, contenido, tipo='application/json; charset=utf-8'):
            cuerpo = contenido if isinstance(contenido, bytes) else json.dumps(contenido, ensure_ascii=False, allow_nan=False).encode()
            self.send_response(estado)
            self.send_header('Content-Type', tipo)
            self.send_header('Content-Length', str(len(cuerpo)))
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.write(cuerpo)

        def entrada_json(self):
            # Protección básica contra escrituras desde páginas de otros orígenes.
            origen = self.headers.get('Origin')
            if origen and urlsplit(origen).netloc != self.headers.get('Host'):
                raise ValueError('Origen de escritura no permitido')
            if self.headers.get_content_type() != 'application/json':
                raise ValueError('Se requiere Content-Type application/json')
            longitud = int(self.headers.get('Content-Length', '0'))
            if not 0 < longitud <= 100000:
                raise ValueError('Tamaño de petición inválido')
            return json.loads(self.rfile.read(longitud))

        def do_GET(self):
            try:
                url = urlsplit(self.path)
                params = parse_qs(url.query)
                if url.path == '/':
                    return self.responder(200, Path(__file__).with_name('index.html').read_bytes(), 'text/html; charset=utf-8')
                if url.path == '/api/productos':
                    return self.responder(200, {'productos': [p.ficha() for p in productos], 'incidencias': incidencias})
                if url.path == '/api/comparar':
                    seleccion = seleccionar(productos, codigos=params.get('codigo'), categoria=params.get('categoria', [None])[0])
                    return self.responder(200, comparar_etiquetas(seleccion))
                if url.path == '/api/recetas':
                    return self.responder(200, [dict(calcular_receta(r, productos), id=r['id']) for r in recetas.listar()])
                return self.responder(404, {'error': 'Ruta inexistente'})
            except (ValueError, OSError) as error:
                self.responder(400, {'error': str(error)})

        def escribir(self):
            try:
                ruta = urlsplit(self.path).path
                coincidencia = re.fullmatch(r'/api/recetas/([1-9][0-9]*)', ruta)
                if self.command == 'POST' and ruta == '/api/recetas':
                    return self.responder(201, recetas.guardar(self.entrada_json(), productos))
                if coincidencia and self.command == 'PUT':
                    return self.responder(200, recetas.guardar(self.entrada_json(), productos, int(coincidencia[1])))
                if coincidencia and self.command == 'DELETE':
                    self.entrada_json()
                    recetas.eliminar(int(coincidencia[1]))
                    return self.responder(200, {'eliminada': True})
                self.responder(404, {'error': 'Ruta inexistente'})
            except (ValueError, UnicodeError) as error:
                self.responder(400, {'error': str(error)})

        do_POST = escribir
        do_PUT = escribir
        do_DELETE = escribir

    return ThreadingHTTPServer((host, puerto), Handler)


def main():
    parser = argparse.ArgumentParser(description='Interfaz web local del comparador')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--puerto', type=int, default=8000)
    parser.add_argument('--entrada', default='data/productos.csv')
    parser.add_argument('--almacen', default='local/recetas.sqlite')
    args = parser.parse_args()
    servidor = crear_servidor(args.host, args.puerto, args.entrada, args.almacen)
    print(f'Servidor iniciado en puerto {servidor.server_port}', flush=True)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        servidor.server_close()


if __name__ == '__main__':
    main()

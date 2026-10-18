"""Prueba de navegador opcional: requiere Playwright y Chromium del sistema."""
from pathlib import Path
import sys
import tempfile
from threading import Thread
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.web import crear_servidor
from playwright.sync_api import sync_playwright, expect


def main():
    with tempfile.TemporaryDirectory() as d:
        servidor = crear_servidor(puerto=0, entrada=Path(__file__).resolve().parents[1]/'data/productos.csv', almacen=Path(d)/'recetas.sqlite')
        hilo = Thread(target=servidor.serve_forever, daemon=True)
        hilo.start()
        try:
            with sync_playwright() as pw:
                navegador = pw.chromium.launch(executable_path='/usr/bin/chromium', headless=True, args=['--no-sandbox'])
                pagina = navegador.new_page(viewport={'width': 1440, 'height': 1000})
                errores = []
                pagina.on('pageerror', lambda e: errores.append(str(e)))
                pagina.goto(f'http://127.0.0.1:{servidor.server_port}')
                expect(pagina.locator('#productos .card')).to_have_count(65)
                pagina.locator('#tipo').select_option('etiqueta')
                expect(pagina.locator('#productos .card')).to_have_count(5)
                pagina.locator('#productos input').nth(0).check()
                pagina.locator('#productos input').nth(1).check()
                pagina.locator('#comparar').click()
                expect(pagina.locator('#tabla tr')).to_have_count(3)
                with pagina.expect_download() as descarga:
                    pagina.locator('#exportar').click()
                assert descarga.value.suggested_filename == 'comparacion.json'
                pagina.locator('#buscar').fill('NO EXISTE ESTE PRODUCTO')
                expect(pagina.locator('#productos .card')).to_have_count(0)
                pagina.locator('#buscar').fill('')
                pagina.locator('#maxenergia').fill('150')
                expect(pagina.locator('#productos .card')).to_have_count(2)
                pagina.locator('#maxenergia').fill('')
                pagina.locator('#nombre').fill('Receta de prueba navegador')
                pagina.locator('#porciones').fill('2')
                pagina.locator('#ingrediente').select_option('CIQ-25001')
                pagina.locator('#gramos').fill('200')
                pagina.locator('#agregar').click()
                pagina.get_by_role('button', name='Guardar receta').click()
                expect(pagina.locator('#listarecetas .card')).to_have_count(1)
                pagina.reload()
                expect(pagina.locator('#listarecetas .card')).to_have_count(1)
                pagina.get_by_role('button',name='Editar',exact=True).click()
                pagina.locator('#nombre').fill('Receta editada')
                pagina.get_by_role('button', name='Guardar receta').click()
                expect(pagina.locator('#listarecetas')).to_contain_text('Receta editada')
                pagina.locator('#listarecetas input[type=checkbox]').check()
                pagina.locator('#productos input').nth(0).check()
                pagina.locator('#comparar').click()
                expect(pagina.locator('#tabla')).to_contain_text('Receta editada')
                pagina.get_by_role('button', name='Eliminar', exact=True).click()
                expect(pagina.locator('#listarecetas .card')).to_have_count(0)
                pagina.locator('#nombre').fill('Inválida')
                pagina.locator('#ingredientes').fill('codigo-inexistente,100')
                pagina.get_by_role('button', name='Guardar receta').click()
                expect(pagina.locator('#mensaje')).to_contain_text('No existe el producto')
                pagina.set_viewport_size({'width':390,'height':844})
                assert pagina.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
                assert not errores, errores
                pagina.screenshot(path='/tmp/tp2-movil.png', full_page=True)
                navegador.close()
                print('Chromium OK: catálogo, filtros, comparación, descarga, CRUD, persistencia, error y ancho móvil. Sin errores JS.')
        finally:
            servidor.shutdown()
            servidor.server_close()
            hilo.join()


if __name__ == '__main__':
    main()

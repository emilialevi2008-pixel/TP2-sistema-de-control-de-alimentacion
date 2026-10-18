"""Ejecutar con python -m src.main --banco ... --sistema ... --salida ..."""
import argparse
import sys
from .importes import formato_ars
from .pipeline import ejecutar
from .reportes import guardar_reportes


def mostrar_resumen(resumen):
    importes = resumen['importes']
    print('='*48)
    print('     CONCILIACIÓN DE CHEQUES ECHEQ')
    print('='*48)
    print('\nRESUMEN DE IMPORTES (ARS)')
    for titulo,clave in [('Importe total banco','total_banco'),('Importe total sistema','total_sistema'),
                        ('Diferencia banco-sistema','diferencia_banco_sistema'),('Diferencia absoluta','diferencia_absoluta'),
                        ('Importe conciliado','importe_conciliado')]:
        print(f'{titulo:28} {formato_ars(importes[clave]):>18}')
    print('\nRESUMEN DE CONCILIACIÓN')
    for titulo,clave in [('Cheques conciliados','cheques_conciliados'),('Cheques con diferencias','cheques_con_diferencias'),
                        ('Sin correspondencia','cheques_sin_correspondencia'),('Pendientes de revisión','pendientes_revision')]:
        print(f'{titulo:28} {resumen[clave]:>18}')
    print(f"Ambiguos (incluidos en revisión): {resumen['cheques_ambiguos']}")
    for fuente in ('banco','sistema'):
        total=resumen['totales_brutos'][fuente]
        print(f"{fuente}: {total['incluidos']} importes incluidos; {total['excluidos']} excluidos; {len(total['duplicados_incluidos'])} filas duplicadas incluidas en bruto")
    print('Un saldo global cero no demuestra conciliación individual.')


def main(argv=None):
    parser = argparse.ArgumentParser(description='Conciliar archivos ECHEQ sintéticos: CSV y/o JSON')
    parser.add_argument('--banco',default='data/banco.csv')
    parser.add_argument('--sistema',default='data/sistema.csv')
    parser.add_argument('--salida',default='outputs')
    args = parser.parse_args(argv)
    try:
        resultados,resumen = ejecutar(args.banco,args.sistema)
        rutas = guardar_reportes(resultados,resumen,args.salida,(args.banco,args.sistema))
    except (ValueError,OSError,UnicodeError) as error:
        print(f'Error: {error}',file=sys.stderr)
        return 2
    mostrar_resumen(resumen)
    print('\nReportes generados:')
    for ruta in rutas:
        print(ruta)
    return 0


if __name__=='__main__':
    raise SystemExit(main())

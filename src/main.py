"""CLI reproducible: python -m src.main --help."""
import argparse
import json
import sys
from .pipeline import ejecutar, guardar_resultado


def main():
    parser = argparse.ArgumentParser(description='Comparador nutricional por 100 g (kcal y g)')
    parser.add_argument('--entrada', default='data/productos.csv')
    parser.add_argument('--salida', default='outputs')
    parser.add_argument('--codigos', nargs='+', help='Códigos textuales; conserva ceros iniciales')
    parser.add_argument('--categoria')
    parser.add_argument('--texto', default='')
    parser.add_argument('--tipo', choices=['etiqueta', 'alimento'])
    parser.add_argument('--max-energia', type=float)
    parser.add_argument('--min-proteinas', type=float)
    args = vars(parser.parse_args())
    entrada, salida = args.pop('entrada'), args.pop('salida')
    try:
        resultado = ejecutar(entrada, **args)
        guardar_resultado(resultado, salida)
    except (ValueError, OSError) as error:
        print(f'Error: {error}', file=sys.stderr)
        return 2
    print(json.dumps(resultado['inspeccion'], ensure_ascii=False))
    print(f'Comparación por 100 g e incidencias guardadas en {salida}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

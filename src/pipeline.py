"""Flujo reproducible y resumen único usado por terminal y exportaciones."""
from collections import Counter
from .conciliacion import conciliar
from .fuentes import cargar
from .fechas import PeriodoConciliacion, filtrar_periodo
from .importes import CERO, calcular_total_bruto
from .validaciones import CAMPOS, limpiar_registros

GRUPOS = ('conciliados','con_diferencias','sin_correspondencia','pendientes_revision')


def inspeccionar(registros):
    esquemas = Counter(tuple(sorted(r.original)) for r in registros)
    return {'filas':len(registros), 'campos_esperados':list(CAMPOS),
            'esquemas_encontrados':[{'campos':list(campos),'filas':n} for campos,n in sorted(esquemas.items())]}


def resumir(banco,sistema,resultados):
    fuentes = {'banco':banco,'sistema':sistema}
    brutos = {fuente:calcular_total_bruto(filas) for fuente,filas in fuentes.items()}
    conteos = Counter(r.grupo for r in resultados)
    importes_grupo = {grupo:{fuente:sum((getattr(r,fuente).importe for r in resultados
                              if r.grupo==grupo and getattr(r,fuente) is not None
                              and getattr(r,fuente).importe is not None),CERO)
                            for fuente in fuentes} for grupo in GRUPOS}
    for fuente in fuentes:
        if sum((v[fuente] for v in importes_grupo.values()),CERO) != brutos[fuente]['total']:
            raise ValueError('Los grupos monetarios no conservan el total bruto')
    if importes_grupo['conciliados']['banco'] != importes_grupo['conciliados']['sistema']:
        raise ValueError('Los importes conciliados no son iguales en ambas fuentes')
    delta = brutos['banco']['total']-brutos['sistema']['total']
    importes = {'total_banco':brutos['banco']['total'],'total_sistema':brutos['sistema']['total'],
                'diferencia_banco_sistema':delta,'diferencia_absoluta':abs(delta),
                'importe_conciliado':importes_grupo['conciliados']['banco'],
                'importe_con_diferencias_banco':importes_grupo['con_diferencias']['banco'],
                'importe_con_diferencias_sistema':importes_grupo['con_diferencias']['sistema'],
                'registros_incluidos_banco':brutos['banco']['incluidos'],
                'registros_excluidos_banco':brutos['banco']['excluidos'],
                'registros_incluidos_sistema':brutos['sistema']['incluidos'],
                'registros_excluidos_sistema':brutos['sistema']['excluidos']}
    auditoria = [{'fuente':r.fuente,'fila':r.fila,'original':r.original,'normalizado':r.normalizado,
                  'cambios':r.cambios,'errores':r.errores+(['ID_DUPLICADO'] if r.duplicado else []),
                  'motivos':r.motivos+(['ID duplicado en la misma fuente'] if r.duplicado else []),
                  'accion':'revision' if not r.habilitado else 'normalizada'}
                 for filas in fuentes.values() for r in filas if r.cambios or not r.habilitado]
    incidencias = Counter(t for r in resultados for t in set(r.tipos))
    return {'moneda':'ARS','base_conteo':'Filas físicas por fuente y resultados de conciliación; un par cuenta como un resultado',
            'registros_banco':len(banco),'registros_sistema':len(sistema),
            'registros_validos':{k:sum(r.cheque is not None for r in v) for k,v in fuentes.items()},
            'registros_invalidos':{k:sum(r.cheque is None for r in v) for k,v in fuentes.items()},
            'registros_duplicados':{k:sum(r.duplicado for r in v) for k,v in fuentes.items()},
            'registros_habilitados':{k:sum(r.habilitado for r in v) for k,v in fuentes.items()},
            'cheques_conciliados':conteos['conciliados'],'cheques_con_diferencias':conteos['con_diferencias'],
            'cheques_sin_correspondencia':conteos['sin_correspondencia'],
            'cheques_ambiguos':sum(r.estado=='COINCIDENCIA_AMBIGUA' for r in resultados),
            'pendientes_revision':conteos['pendientes_revision'],'total_resultados':len(resultados),
            'estados':dict(sorted(Counter(r.estado for r in resultados).items())),
            'incidencias_por_tipo':dict(sorted(incidencias.items())),
            'importes':importes,'totales_brutos':brutos,'importes_por_grupo':importes_grupo,
            'registros_excluidos_sumas':{k:v['registros_excluidos'] for k,v in brutos.items()},
            'inspeccion':{k:inspeccionar(v) for k,v in fuentes.items()},'auditoria':auditoria}


def ejecutar(ruta_banco,ruta_sistema,inicio,fin,excel_banco='1900',excel_sistema='1900'):
    periodo = PeriodoConciliacion.desde_texto(inicio,fin)
    registros,filtrado = {},{}
    for fuente,ruta,excel in [('banco',ruta_banco,excel_banco),('sistema',ruta_sistema,excel_sistema)]:
        elegidas,numeros,informe = filtrar_periodo(cargar(ruta),fuente,periodo,excel)
        registros[fuente] = limpiar_registros(elegidas,fuente,numeros,excel) if elegidas else []
        filtrado[fuente] = informe
    banco,sistema = registros['banco'],registros['sistema']
    resultados = conciliar(banco,sistema)
    for resultado in resultados:
        if resultado.grupo=='sin_correspondencia':
            resultado.descripcion += ' dentro del período elegido (solo fechas válidas)'
    resumen = resumir(banco,sistema,resultados)
    resumen['periodo'] = periodo.describir()
    resumen['sistema_excel'] = {'banco':excel_banco,'sistema':excel_sistema}
    resumen['filtrado'] = filtrado
    resumen['incidencias_filtrado'] = dict(sorted(Counter(e['tipo'] for f in filtrado.values() for e in f['exclusiones']).items()))
    resumen['mensaje'] = 'Conciliación del período completada' if banco or sistema else 'No hay registros con fecha válida dentro del período elegido'
    return resultados,resumen

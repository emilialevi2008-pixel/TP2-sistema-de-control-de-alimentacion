"""Motor conservador y determinista: exactos primero, prefijos sin arbitrariedad."""
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from .importes import formato_ars
from .fechas import mostrar_fecha
from .modelos import Registro


@dataclass
class ResultadoConciliacion:
    banco: Registro | None
    sistema: Registro | None
    estado: str
    tipos: list[str]
    descripcion: str
    candidatos: list[dict] = field(default_factory=list)

    @property
    def grupo(self):
        if self.estado.startswith('CONCILIADO'):
            return 'conciliados'
        if self.estado in ('ERROR_IMPORTE','ERROR_FECHA','CON_DIFERENCIAS'):
            return 'con_diferencias'
        if self.estado in ('NO_ESTA_EN_BANCO','NO_ESTA_EN_SISTEMA'):
            return 'sin_correspondencia'
        return 'pendientes_revision'


def emparejar(banco, sistema, abreviado=False):
    errores = banco.cheque.diferencias(sistema.cheque)
    descripciones = []
    if 'ERROR_IMPORTE' in errores:
        delta = banco.cheque.diferencia_importe(sistema.cheque)
        quien = 'banco' if delta > 0 else 'sistema'
        otro = 'sistema' if delta > 0 else 'banco'
        descripciones.append(f'El importe del {quien} supera al del {otro} en {formato_ars(abs(delta))}')
    if 'ERROR_FECHA' in errores:
        descripciones.append(f'La fecha bancaria es {mostrar_fecha(banco.cheque.fecha_pago)} y la contable es {mostrar_fecha(sistema.cheque.fecha_pago)}')
    if errores:
        estado = errores[0] if len(errores)==1 else 'CON_DIFERENCIAS'
        if abreviado:
            descripciones.append('Correspondencia por prefijo único, con diferencias pendientes')
    else:
        estado = 'CONCILIADO_ID_ABREVIADO' if abreviado else 'CONCILIADO'
        descripciones.append('ID abreviado con candidato único; importe y fecha coinciden' if abreviado else 'ID exacto, importe y fecha de pago coinciden')
    return ResultadoConciliacion(banco,sistema,estado,errores,'; '.join(descripciones))


def indexar(registros):
    indice = defaultdict(list)
    for registro in registros:
        if registro.codigo is not None:
            indice[registro.codigo].append(registro)
    return indice


def conciliar(banco, sistema):
    indice = indexar(banco)
    resultados, usados_banco, usados_sistema = [], set(), set()

    def agregar(resultado):
        if resultado.banco is not None:
            if resultado.banco.fila in usados_banco:
                raise ValueError('Una fila bancaria se intenta utilizar más de una vez')
            usados_banco.add(resultado.banco.fila)
        if resultado.sistema is not None:
            if resultado.sistema.fila in usados_sistema:
                raise ValueError('Una fila contable se intenta utilizar más de una vez')
            usados_sistema.add(resultado.sistema.fila)
        resultados.append(resultado)

    def pendiente(registro, tipo, descripcion, candidatos=(), ambiguo=False):
        return ResultadoConciliacion(None,registro,'COINCIDENCIA_AMBIGUA' if ambiguo else 'PENDIENTE_REVISION',
                                     [tipo],descripcion,[{'id_cheque':b.codigo,'fila_banco':b.fila} for b in candidatos])

    # Cada registro inválido/duplicado conserva una fila propia para revisión.
    for registros in (banco,sistema):
        for r in registros:
            if not r.habilitado:
                tipos = list(r.errores)+(['ID_DUPLICADO'] if r.duplicado else [])
                motivos = list(r.motivos)+(['El identificador aparece duplicado en esta fuente; no se concilia automáticamente'] if r.duplicado else [])
                agregar(ResultadoConciliacion(r if r.fuente=='banco' else None,
                                             r if r.fuente=='sistema' else None,
                                             'ID_DUPLICADO' if r.duplicado else 'DATOS_INVALIDOS',tipos,'; '.join(motivos)))

    # Exactos reservados antes de cualquier prefijo, independientemente del orden.
    restantes = []
    for s in sistema:
        if not s.habilitado:
            continue
        candidatos = indice.get(s.codigo,[])
        if candidatos:
            if len(candidatos)==1 and candidatos[0].habilitado:
                agregar(emparejar(candidatos[0],s))
            else:
                agregar(pendiente(s,'CONTRAPARTE_INVALIDA','El ID exacto existe en banco, pero sus filas son inválidas o duplicadas',candidatos))
        else:
            restantes.append(s)

    # Calcular todas las propuestas antes de resolver para no depender del orden.
    propuestas = defaultdict(list)
    for s in restantes:
        candidatos = [b for codigo, filas in indice.items()
                      if len(codigo)>len(s.codigo) and codigo.startswith(s.codigo) for b in filas]
        ids = {b.codigo for b in candidatos}
        if not candidatos:
            agregar(ResultadoConciliacion(None,s,'NO_ESTA_EN_BANCO',['NO_ESTA_EN_BANCO'],
                                         'El cheque figura en el sistema, pero no en el banco'))
        elif len(ids)>1:
            agregar(pendiente(s,'COINCIDENCIA_AMBIGUA','El identificador abreviado coincide con más de un cheque bancario',candidatos,True))
        elif len(candidatos)>1 or not candidatos[0].habilitado:
            agregar(pendiente(s,'CONTRAPARTE_INVALIDA','El prefijo apunta a un ID bancario duplicado o inválido',candidatos))
        elif candidatos[0].fila in usados_banco:
            agregar(pendiente(s,'BANCO_YA_ASIGNADO','El único candidato bancario ya tiene una coincidencia exacta; no se reutiliza',candidatos))
        else:
            propuestas[candidatos[0].fila].append((candidatos[0],s))
    for pares in propuestas.values():
        if len(pares)==1:
            b,s = pares[0]
            agregar(emparejar(b,s,True))
        else:
            for b,s in pares:
                agregar(pendiente(s,'COINCIDENCIA_AMBIGUA','Varios identificadores contables compiten por la misma fila bancaria; ninguna asignación automática', [b], True))

    # Un candidato no resuelto no debe convertirse falsamente en «ausente».
    codigos_sistema = [s.codigo for s in sistema if s.codigo is not None]
    for b in banco:
        if b.fila not in usados_banco:
            posibles = [c for c in codigos_sistema if b.codigo==c or len(b.codigo)>len(c) and b.codigo.startswith(c)]
            if posibles:
                agregar(ResultadoConciliacion(b,None,'PENDIENTE_REVISION',['CONTRAPARTE_NO_RESUELTA'],
                                             'Existe una posible contraparte contable inválida, duplicada o ambigua; requiere revisión'))
            else:
                agregar(ResultadoConciliacion(b,None,'NO_ESTA_EN_SISTEMA',['NO_ESTA_EN_SISTEMA'],
                                             'El cheque figura en el banco, pero no en el sistema'))
    resultados.sort(key=lambda r:(r.banco is None,r.banco.fila if r.banco else r.sistema.fila))
    verificar_trazabilidad(resultados,banco,sistema)
    return resultados


def verificar_trazabilidad(resultados,banco,sistema):
    for fuente,registros in [('banco',banco),('sistema',sistema)]:
        esperadas = Counter(r.fila for r in registros)
        observadas = Counter(getattr(r,fuente).fila for r in resultados if getattr(r,fuente) is not None)
        if observadas != esperadas or any(v != 1 for v in observadas.values()):
            raise ValueError(f'No se conserva la correspondencia uno a uno en {fuente}')

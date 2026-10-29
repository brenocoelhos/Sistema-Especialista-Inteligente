"""Motor independente da interface; pontuação e recomendações auditáveis."""
import json
import math
from pathlib import Path

BASE = Path(__file__).with_name('regras_carreiras.json')

def carregar_base(caminho=BASE):
    base = json.loads(Path(caminho).read_text(encoding='utf-8'))
    ids = {p['id'] for p in base['perguntas']}
    if len(ids) != len(base['perguntas']) or len(base['trilhas']) != 10:
        raise ValueError('A base deve conter perguntas únicas e dez trilhas.')
    for t in base['trilhas']:
        if set(t['pesos']) != ids or any(w < 0 for w in t['pesos'].values()) or sum(t['pesos'].values()) <= 0:
            raise ValueError('Pesos inválidos: ' + t['nome'])
        for p in t['penalidades']:
            if p['atributo'] not in ids or not 1 <= p['abaixo_de'] <= 5 or not 0 <= p['pontos'] <= 100:
                raise ValueError('Penalidade inválida')
        if any(s['id'] not in base['competencias'] or not 1 <= s['minimo'] <= 3 for s in t['requisitos']):
            raise ValueError('Requisito inválido')
    return base

def ranking(base, respostas):
    ids = {p['id'] for p in base['perguntas']}
    if set(respostas) != ids:
        raise ValueError('Responda todas as perguntas da base.')
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) or not 1 <= v <= 5 for v in respostas.values()):
        raise ValueError('Respostas devem estar entre 1 e 5.')
    resultado = []
    for t in base['trilhas']:
        total = sum(t['pesos'].values())
        parcelas = {k: 100 * (respostas[k] - 1) / 4 * w / total for k, w in t['pesos'].items()}
        aplicadas = [p for p in t['penalidades'] if respostas[p['atributo']] < p['abaixo_de']]
        bruto = sum(parcelas.values())
        nota = max(0, bruto - sum(p['pontos'] for p in aplicadas))
        resultado.append({'id': t['id'], 'nome': t['nome'], 'compatibilidade': nota,
                          'bruto': bruto, 'contribuicoes': parcelas, 'penalidades': aplicadas})
    return sorted(resultado, key=lambda r: (-r['compatibilidade'], r['nome']))

def plano(base, trilha_id, conhecimentos, horas=5):
    if isinstance(horas, bool) or not isinstance(horas, (int, float)) or not math.isfinite(horas) or horas <= 0:
        raise ValueError('Horas semanais devem ser positivas.')
    if any(k not in base['competencias'] or isinstance(v, bool) or not isinstance(v, int) or not 0 <= v <= 3 for k, v in conhecimentos.items()):
        raise ValueError('Conhecimentos inválidos.')
    t = next(t for t in base['trilhas'] if t['id'] == trilha_id)
    gaps = []
    semana = 1
    for requisito in t['requisitos']:
        atual = conhecimentos.get(requisito['id'], 0)
        if atual < requisito['minimo']:
            comp = base['competencias'][requisito['id']]
            estimativa = comp['horas_por_nivel'] * (requisito['minimo'] - atual)
            duracao = math.ceil(estimativa / horas)
            gaps.append({'competencia': comp['nome'], 'atual': atual, 'meta': requisito['minimo'],
                         'estudar': comp['estudar'], 'horas': estimativa,
                         'periodo': f'Semanas {semana}–{semana + duracao - 1}'})
            semana += duracao
    return {'trilha': t['nome'], 'gaps': gaps, 'semanas': semana - 1,
            'nivel': 'Em formação para Júnior' if gaps else 'Requisitos Júnior declarados atendidos',
            'certificacoes': t['certificacoes'], 'projeto': t['projeto']}

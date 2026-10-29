import json
from html import escape
import pandas as pd
import streamlit as st
from motor import carregar_base, ranking, plano

st.set_page_config(page_title='Bússola TI | Sua próxima direção', layout='wide')
st.html('''<style>
.stApp {background: #f5f6fa; color: #202c40;}
.block-container {max-width: 1120px; padding-top: 2.8rem; padding-bottom: 3rem;}
h1,h2,h3 {letter-spacing: -.035em; color: #17263d;}
h1 {font-size: 2.7rem !important; font-weight: 750 !important;}
h3 {font-size: 1.35rem !important;}
[data-testid="stSidebar"] {background: #17263d;}
[data-testid="stSidebar"] p, [data-testid="stSidebar"] h2 {color: #f2f5fc;}
.brand {font-size: 1.4rem; font-weight: 750; letter-spacing: -.04em; color: #fff; margin: 1rem 0 .3rem;}
.brand-note {color: #b4c2d8; font-size: .88rem; line-height: 1.7; margin-bottom: 2.4rem;}
.nav-step {display: flex; align-items: center; gap: 12px; color: #b4c2d8; padding: 14px 12px; margin: 8px 0; border-radius: 10px; font-size: .9rem;}
.nav-step.active {background: #2c405d; color: white; font-weight: 650;}
.step-number {border: 1px solid #667a97; border-radius: 8px; padding: 4px 9px; font-size: .8rem;}
.active .step-number {background: #d7e9e7; color: #174e49; border-color: #d7e9e7;}
.eyebrow {font-size: .73rem; font-weight: 700; letter-spacing: .16em; color: #38766e; text-transform: uppercase; margin-bottom: .6rem;}
.intro {font-size: 1.06rem; line-height: 1.7; color: #607087; max-width: 720px; margin-bottom: 1.7rem;}
[data-testid="stForm"] {background: white; border: 1px solid #e1e6ef; border-radius: 16px; padding: 28px; box-shadow: 0 5px 22px #17263d05;}
[data-testid="stSlider"] {padding: .35rem 0 .8rem;}
[data-testid="stMetric"] {background: #fff; border: 1px solid #e1e6ef; border-radius: 14px; padding: 22px; margin-bottom: 1rem;}
[data-testid="stMetricValue"] {color: #24695e;}
.stButton button, .stDownloadButton button, [data-testid="stFormSubmitButton"] button {border-radius: 9px; min-height: 44px; font-weight: 600;}
.scale {background: #edf3f5; color: #455b6f; padding: 14px 18px; border-radius: 10px; font-size: .86rem; line-height: 1.8; margin: .7rem 0 1.5rem;}
.roadmap {background: white; border: 1px solid #e1e6ef; border-left: 3px solid #38766e; border-radius: 12px; padding: 20px 24px; margin: 12px 0;}
.roadmap h4 {font-size: 1.05rem; margin: 5px 0 10px; color: #17263d;}
.roadmap p {color: #607087; margin: 0; line-height: 1.65;}
.roadmap-meta {font-size: .76rem; font-weight: 650; color: #38766e; letter-spacing: .03em;}
@media (max-width: 640px) {.block-container {padding: 1.5rem 1rem;} h1 {font-size: 2rem !important;} [data-testid="stForm"] {padding: 16px;}}
</style>''')
base = carregar_base()
if 'passo' not in st.session_state:
    st.session_state.passo = 0
    st.session_state.respostas = {}
    st.session_state.conhecimentos = {}
etapas = ['Perfil pessoal', 'Afinidades técnicas', 'Objetivos de carreira', 'Resultados e plano']
passo = st.session_state.passo
with st.sidebar:
    st.html('<div class="brand">Bússola TI</div><div class="brand-note">Clareza para escolher.<br>Um plano para evoluir.</div>')
    for i, etapa in enumerate(etapas):
        st.html(f'<div class="nav-step {"active" if i == passo else ""}"><span class="step-number">{i + 1:02}</span>{etapa}</div>')
    st.divider()
    st.caption('10 trilhas de tecnologia\n\nRecomendações a partir do seu perfil, dos seus interesses e do seu ritmo.')
st.html(f'<div class="eyebrow">Seu próximo passo em tecnologia / {passo + 1:02} de 04</div>')
titulos = ['Toda trajetória começa com você.', 'O que desperta seu interesse?', 'Que trabalho faz sentido para você?', 'Encontre sua próxima direção.']
descricoes = ['Conte um pouco sobre seu momento e o que você já sabe. Vamos usar isso para construir um plano possível para a sua rotina.', 'Indique sua afinidade com cada área. Pense no que você gosta de explorar, mesmo que ainda não tenha experiência.', 'Agora, pense nos desafios e experiências que gostaria de encontrar no seu dia a dia profissional.', 'Explore suas afinidades, compare caminhos e transforme as competências que faltam em próximos passos.']
st.title(titulos[passo])
st.html(f'<div class="intro">{descricoes[passo]}</div>')
st.progress((passo + 1) / 4)
st.write('')

if passo == 0:
    with st.form('perfil'):
        st.subheader('Seu ponto de partida')
        esquerda, direita = st.columns([2, 1], gap='large')
        nome = esquerda.text_input('Como gostaria de ser chamado? (opcional)', value=st.session_state.get('nome', ''), placeholder='Seu nome')
        horas = direita.number_input('Horas de estudo por semana', 1, 40, st.session_state.get('horas', 5))
        st.divider()
        st.subheader('Seu repertório atual')
        st.caption('Não é uma prova. Escolha o nível que melhor representa sua experiência hoje.')
        st.html('<div class="scale"><b>0</b> Ainda não conheço &nbsp; · &nbsp; <b>1</b> Conheço conceitos &nbsp; · &nbsp; <b>2</b> Aplico com apoio &nbsp; · &nbsp; <b>3</b> Aplico com autonomia</div>')
        conhecimentos = {}
        cols = st.columns(2, gap='large')
        for i, (id, c) in enumerate(base['competencias'].items()):
            with cols[i % 2]:
                conhecimentos[id] = st.select_slider(c['nome'], options=[0, 1, 2, 3], value=st.session_state.conhecimentos.get(id, 0), key='skill_' + id)
        if st.form_submit_button('Continuar', type='primary'):
            st.session_state.update(nome=nome, horas=horas, conhecimentos=conhecimentos, passo=1)
            st.rerun()
elif passo in (1, 2):
    st.html('<div class="scale"><b>1</b> Nenhuma afinidade &nbsp; · &nbsp; <b>2</b> Pouca &nbsp; · &nbsp; <b>3</b> Moderada &nbsp; · &nbsp; <b>4</b> Alta &nbsp; · &nbsp; <b>5</b> Muito alta</div>')
    grupo = 'tecnica' if passo == 1 else 'objetivos'
    with st.form('perguntas_' + grupo):
        st.subheader(etapas[passo])
        valores = {}
        for p in base['perguntas']:
            if p['grupo'] == grupo:
                valores[p['id']] = st.slider(p['texto'], 1, 5, st.session_state.respostas.get(p['id'], 3), key='q_' + p['id'])
        anterior, proximo = st.columns(2)
        voltar = anterior.form_submit_button('Voltar')
        avancar = proximo.form_submit_button('Ver resultados' if passo == 2 else 'Continuar', type='primary')
        if voltar or avancar:
            st.session_state.respostas.update(valores)
            st.session_state.passo += 1 if avancar else -1
            st.rerun()
else:
    resultados = ranking(base, st.session_state.respostas)
    if st.session_state.nome:
        st.subheader(f'Perfil de {st.session_state.nome}')
    st.caption('SUAS TRÊS PRINCIPAIS AFINIDADES')
    for col, r in zip(st.columns(3), resultados[:3]):
        col.metric(r['nome'], f"{r['compatibilidade']:.1f}%")
    if resultados[0]['compatibilidade'] - resultados[1]['compatibilidade'] < 3:
        st.warning('As primeiras trilhas têm aderência próxima (diferença inferior a 3 pontos). Explore projetos nas duas antes de decidir. Empates exatos são ordenados alfabeticamente.')
    if resultados[0]['compatibilidade'] < 40:
        st.warning('A aderência geral é baixa. O primeiro lugar é relativo a este perfil e não indica forte recomendação.')
    frame = pd.DataFrame([{'Trilha': r['nome'], 'Aderência (%)': round(r['compatibilidade'], 1)} for r in resultados])
    st.subheader('Um olhar sobre as dez trilhas')
    st.bar_chart(frame.set_index('Trilha'), horizontal=True, x_label='Aderência (%)', color='#38766e')
    with st.expander('Ver ranking em tabela'):
        st.dataframe(frame, hide_index=True, use_container_width=True)
    st.divider()
    st.subheader('Do interesse à prática')
    nomes = {t['id']: t['nome'] for t in base['trilhas']}
    selecionada = st.selectbox('Explore o plano de qualquer trilha', [r['id'] for r in resultados], format_func=nomes.get)
    r = next(r for r in resultados if r['id'] == selecionada)
    with st.expander('Como esta pontuação foi calculada'):
        st.write('Cada resposta é normalizada: (resposta − 1) ÷ 4. A soma ponderada é dividida pela soma dos pesos e multiplicada por 100. As penalidades são subtraídas em pontos percentuais, com piso zero.')
        perguntas = {p['id']: p['texto'] for p in base['perguntas']}
        st.dataframe(pd.DataFrame([{'Dimensão': perguntas[k], 'Resposta': st.session_state.respostas[k], 'Contribuição (p.p.)': round(v, 2)} for k, v in r['contribuicoes'].items()]), hide_index=True)
        st.write(f"Pontuação antes das penalidades: {r['bruto']:.1f}%")
        for p in r['penalidades']:
            st.write(f"−{p['pontos']} p.p.: {p['motivo']}")
        if not r['penalidades']:
            st.write('Nenhuma penalidade aplicada.')
    acao = plano(base, selecionada, st.session_state.conhecimentos, st.session_state.horas)
    st.subheader('Sua trilha de desenvolvimento')
    st.write(acao['nivel'])
    st.caption('Meta educacional: nível 2 em cada competência exigida. Autoavaliação não comprova senioridade; experiência e avaliação prática são necessárias. Cloud Architecture é uma direção de carreira, e este plano cobre fundamentos iniciais.')
    if acao['gaps']:
        for indice, gap in enumerate(acao['gaps'], 1):
            st.html(f'<div class="roadmap"><div class="roadmap-meta">ETAPA {indice:02} · {escape(gap["periodo"])} · {gap["horas"]}h de estudo</div><h4>{escape(gap["competencia"])}</h4><p>{escape(gap["estudar"])}</p><p><small>Nível atual: {gap["atual"]} &nbsp; / &nbsp; Meta: {gap["meta"]}</small></p></div>')
        st.write(f"Estimativa de estudo: {acao['semanas']} semanas, com {st.session_state.horas} horas semanais. Ajuste o ritmo conforme a prática; a estimativa não inclui a execução do portfólio.")
    else:
        st.success('Nenhuma lacuna declarada para a meta Júnior. Valide suas competências com o projeto abaixo.')
    st.subheader('Projeto para o GitHub')
    st.write(acao['projeto'])
    st.write('Inclua README com problema, instalação, decisões técnicas, exemplos de uso, testes e limitações. Não publique segredos nem dados pessoais.')
    st.subheader('Formação e certificações opcionais')
    for c in acao['certificacoes']:
        st.write('• ' + c)
    st.caption('Estas são categorias de formação para pesquisa; não representam credenciais específicas verificadas nem requisitos obrigatórios de contratação.')
    exportacao = {'versao_base': base['versao'], 'respostas': st.session_state.respostas, 'conhecimentos': st.session_state.conhecimentos, 'ranking': resultados, 'plano': acao}
    st.download_button('Baixar diagnóstico JSON', json.dumps(exportacao, ensure_ascii=False, indent=2), 'diagnostico.json', 'application/json')
    if st.button('Revisar respostas'):
        st.session_state.passo = 0
        st.rerun()
st.divider()
with st.expander('Sobre esta orientação'):
    st.write(base['metodologia'])
st.caption('Bússola TI · Os dados ficam nesta sessão. Você decide quando exportar seu diagnóstico.')

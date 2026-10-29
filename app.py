import json
import pandas as pd
import streamlit as st
from motor import carregar_base, ranking, plano

st.set_page_config(page_title='Bússola TI', page_icon='🧭', layout='wide')
base = carregar_base()
st.title('🧭 Bússola TI')
st.caption('Consultor de carreiras • afinidades, competências e próximos passos')
st.info(base['metodologia'])
if 'passo' not in st.session_state:
    st.session_state.passo = 0
    st.session_state.respostas = {}
    st.session_state.conhecimentos = {}
etapas = ['Perfil pessoal', 'Afinidades técnicas', 'Objetivos de carreira', 'Resultados e plano']
passo = st.session_state.passo
st.progress((passo + 1) / 4, text=f'Passo {passo + 1}: {etapas[passo]}')

if passo == 0:
    with st.form('perfil'):
        nome = st.text_input('Como gostaria de ser chamado? (opcional)', value=st.session_state.get('nome', ''))
        horas = st.number_input('Horas disponíveis por semana', 1, 40, st.session_state.get('horas', 5))
        st.write('Conhecimento atual: 0 = ainda não conheço; 1 = conheço conceitos; 2 = aplico com apoio; 3 = aplico com autonomia.')
        conhecimentos = {}
        cols = st.columns(2)
        for i, (id, c) in enumerate(base['competencias'].items()):
            with cols[i % 2]:
                conhecimentos[id] = st.select_slider(c['nome'], options=[0, 1, 2, 3], value=st.session_state.conhecimentos.get(id, 0), key='skill_' + id)
        if st.form_submit_button('Continuar', type='primary'):
            st.session_state.update(nome=nome, horas=horas, conhecimentos=conhecimentos, passo=1)
            st.rerun()
elif passo in (1, 2):
    st.write('1 = nenhuma afinidade • 2 = pouca • 3 = moderada • 4 = alta • 5 = muito alta')
    grupo = 'tecnica' if passo == 1 else 'objetivos'
    with st.form('perguntas_' + grupo):
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
    for col, r in zip(st.columns(3), resultados[:3]):
        col.metric(r['nome'], f"{r['compatibilidade']:.1f}%")
    if resultados[0]['compatibilidade'] - resultados[1]['compatibilidade'] < 3:
        st.warning('As primeiras trilhas têm aderência próxima (diferença inferior a 3 pontos). Explore projetos nas duas antes de decidir. Empates exatos são ordenados alfabeticamente.')
    if resultados[0]['compatibilidade'] < 40:
        st.warning('A aderência geral é baixa. O primeiro lugar é relativo a este perfil e não indica forte recomendação.')
    frame = pd.DataFrame([{'Trilha': r['nome'], 'Aderência (%)': round(r['compatibilidade'], 1)} for r in resultados])
    st.bar_chart(frame.set_index('Trilha'), horizontal=True, x_label='Aderência (%)')
    st.dataframe(frame, hide_index=True, use_container_width=True)
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
        st.dataframe(pd.DataFrame(acao['gaps']), hide_index=True, use_container_width=True)
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
st.caption('Os dados ficam na sessão da aplicação. O diagnóstico só é exportado quando você solicita o download.')

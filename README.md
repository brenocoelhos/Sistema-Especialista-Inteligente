# Bússola TI — Sistema Especialista de Carreiras

Projeto educacional em Python 3.10+ e Streamlit com dez trilhas, entrada Likert, ranking completo e Top 3, regras de conflito, análise de competências e roadmap exportável.

## Executar

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Abra o endereço local informado pelo Streamlit. Não é necessária chave de API.

## Arquitetura e modelagem

- `regras_carreiras.json`: perguntas, pesos, penalidades, competências, ordem pedagógica, esforço estimado, formação e projetos das dez trilhas.
- `motor.py`: carregamento, validação, ranking e plano, independente do Streamlit.
- `app.py`: quatro etapas, autoavaliação, gráficos, explicações e download JSON.
- `test_motor.py`: extremos, perfil ambíguo, empate, penalidades, entradas inválidas e lacunas.

A aderência é `max(0, 100 × soma(peso × (resposta − 1)/4) / soma(pesos) − penalidades)`. Pesos entre zero e cinco expressam importância relativa; zero exclui a dimensão. A base inicial foi modelada para demonstração acadêmica e deve ser revisada por especialistas e validada com usuários antes de uso profissional. Cada trilha possui uma regra explícita de baixa afinidade com uma dimensão central, com desconto de dez pontos. Não são probabilidades e os percentuais não somam cem. Respostas moderadas produzem 50%; afinidade máxima produz 100%. Empates exatos usam o nome da trilha; diferenças menores que três pontos geram aviso.

Conhecimento usa escala própria: 0 desconhecido, 1 conceitos, 2 aplicação com apoio, 3 autonomia. A meta Júnior desta base exige nível 2 nas competências listadas. Lacunas seguem a ordem pedagógica dos requisitos no JSON. O esforço é calculado por níveis faltantes e horas por nível; cada bloco é arredondado para semanas inteiras conforme disponibilidade. Competências já atendidas são omitidas. O projeto de portfólio é sugerido mesmo sem lacunas.

O sistema distingue formação inicial e atendimento autodeclarado da meta Júnior. Não infere Pleno ou Sênior a partir de afinidade ou autoavaliação. Arquitetura cloud é apresentada como direção de desenvolvimento, com plano de fundamentos. Certificações são categorias opcionais para pesquisa, sem promessa de contratação ou recomendação comercial específica.

## Verificação

```powershell
python -m unittest -v
```

Para validar o fluxo manualmente: preencha o perfil, avance pelas afinidades e objetivos, inspecione o ranking, alterne as dez trilhas e baixe o diagnóstico. Revise respostas e confirme que os valores permanecem. Experimente todas as afinidades em 1, 3 e 5; todas as competências em 0 e depois em 2.

## Evolução e entrega

As cinco fases do enunciado são representadas pela base JSON, motor, plano, interface e testes. Próximas validações acadêmicas: entrevistas com profissionais, calibração de pesos e metas, comparação de perfis reais com avaliação de especialistas. O projeto está pronto para versionamento; a publicação no GitHub exige escolher um repositório e conta de destino.

Os dados não são gravados pela aplicação em arquivo ou banco. O usuário pode exportar seu diagnóstico. Em implantação compartilhada, revise as políticas do servidor e da plataforma.

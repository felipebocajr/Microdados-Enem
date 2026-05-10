import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# ─── Configuração da Página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="ENEM 2022 — Nordeste vs Brasil",
    page_icon="📊",
    layout="wide",
)

# ─── Constantes ──────────────────────────────────────────────────────────────
UF_REGIAO = {
    'AC': 'Norte', 'AM': 'Norte', 'AP': 'Norte', 'PA': 'Norte',
    'RO': 'Norte', 'RR': 'Norte', 'TO': 'Norte',
    'AL': 'Nordeste', 'BA': 'Nordeste', 'CE': 'Nordeste', 'MA': 'Nordeste',
    'PB': 'Nordeste', 'PE': 'Nordeste', 'PI': 'Nordeste', 'RN': 'Nordeste',
    'SE': 'Nordeste',
    'DF': 'Centro-Oeste', 'GO': 'Centro-Oeste', 'MS': 'Centro-Oeste',
    'MT': 'Centro-Oeste',
    'ES': 'Sudeste', 'MG': 'Sudeste', 'RJ': 'Sudeste', 'SP': 'Sudeste',
    'PR': 'Sul', 'RS': 'Sul', 'SC': 'Sul',
}

CORES_REGIAO = {
    'Norte': '#27AE60', 'Nordeste': '#D35400', 'Centro-Oeste': '#F1C40F',
    'Sudeste': '#8E44AD', 'Sul': '#1ABC9C',
}
COR_NE = '#D35400'
COR_DEMAIS = '#2980B9'

COLS = [
    'SG_UF_PROVA',
    'TP_PRESENCA_CN', 'TP_PRESENCA_CH', 'TP_PRESENCA_LC', 'TP_PRESENCA_MT',
    'NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO',
    'TP_STATUS_REDACAO', 'TP_SEXO', 'TP_COR_RACA', 'TP_FAIXA_ETARIA',
    'TP_ESCOLA', 'IN_TREINEIRO', 'TP_LINGUA', 'TP_LOCALIZACAO_ESC',
    'Q002', 'Q006', 'Q025',
]

FAIXA_GRUPO = {
    1: '<17', 2: '17-18', 3: '17-18',
    4: '19-21', 5: '19-21', 6: '19-21',
    7: '22-25', 8: '22-25', 9: '22-25', 10: '22-25',
    11: '26-30',
    **{i: '31+' for i in range(12, 21)},
}
FAIXA_IDADE = {
    1: 16, 2: 17, 3: 18, 4: 19, 5: 20, 6: 21, 7: 22, 8: 23, 9: 24, 10: 25,
    11: 28, 12: 33, 13: 38, 14: 43, 15: 48, 16: 53, 17: 58, 18: 63, 19: 68, 20: 73,
}

RENDA_GRUPO = {
    'A': 'Sem renda', 'B': 'Até 1 SM',
    'C': '1-2 SM', 'D': '1-2 SM',
    'E': '2-3 SM', 'F': '2-3 SM',
    'G': '3-5 SM', 'H': '3-5 SM',
    'I': '5-10 SM', 'J': '5-10 SM', 'K': '5-10 SM', 'L': '5-10 SM',
    'M': '10-20 SM', 'N': '10-20 SM', 'O': '10-20 SM', 'P': '10-20 SM',
    'Q': '>20 SM',
}
ORDEM_RENDA = ['Sem renda', 'Até 1 SM', '1-2 SM', '2-3 SM', '3-5 SM',
               '5-10 SM', '10-20 SM', '>20 SM']

PERGUNTAS = {
    1:  "O Nordeste ocupa qual posição no ranking nacional de evasão (candidatos que faltaram às provas) em comparação com as outras regiões do país?",
    2:  "Existe uma disparidade na taxa de notas zeradas na Redação entre os candidatos do Nordeste e os do restante do país?",
    3:  "Qual é a colocação do Nordeste no ranking nacional de desempenho médio na prova de Redação em relação às demais regiões?",
    4:  "Qual é a proporção de candidatos cuja mãe possui ensino superior completo no Nordeste em comparação com o restante do Brasil?",
    5:  "Qual é a proporção de candidatos que atingiram média geral acima de 700 pontos no Nordeste em comparação com o restante do país?",
    6:  "Como se compara a distribuição por sexo dos candidatos do Nordeste com a do Brasil?",
    7:  "Existe diferença significativa na média geral de notas entre homens e mulheres no Nordeste comparada à diferença observada no Brasil?",
    8:  "Ao cruzar renda familiar, tipo de escola e média geral de notas, qual é o perfil do candidato de alto desempenho no Nordeste comparado ao cenário nacional?",
    9:  "Qual é a proporção de candidatos com redação em branco versus os que zeraram por violação de regras — Nordeste vs Brasil?",
    10: "Em qual área de conhecimento o Nordeste apresenta a menor diferença em relação à média nacional — e em qual apresenta a maior defasagem?",
    11: "Qual é a diferença de desempenho entre candidatos de escolas urbanas e rurais no Nordeste — e essa disparidade é maior ou menor do que no Brasil?",
    12: "Qual é a proporção de candidatos com média geral abaixo de 400 no Nordeste vs Brasil — e quais estados nordestinos concentram mais esse grupo?",
    13: "A taxa de ausência no segundo dia de prova é maior do que no primeiro dia no Nordeste? Essa diferença é mais acentuada do que no Brasil?",
    14: "Qual é a média de notas dos treineiros do Nordeste comparada à dos treineiros do restante do Brasil?",
    15: "Como se divide a escolha entre Inglês e Espanhol no Nordeste em comparação com a média nacional?",
    16: "Candidatos indígenas do Nordeste apresentam desempenho médio mais próximo ou mais distante da média nacional do que indígenas de outras regiões?",
    17: "Como se compara a taxa de nota máxima na redação entre candidatos do Nordeste e das demais regiões do Brasil?",
    18: "Como se compara o desempenho médio por faixa etária entre candidatos do Nordeste e do Brasil — em qual faixa a defasagem é maior?",
    19: "Qual é a idade média dos candidatos com média acima de 700 no Nordeste comparada à do Brasil?",
    20: "O acesso à internet em casa influencia mais o desempenho dos candidatos do Nordeste do que o dos candidatos das demais regiões?",
}

PERGUNTAS_LABELS = {
    1:  "Pergunta 1: Evasão por Região",
    2:  "Pergunta 2: Notas Zero na Redação",
    3:  "Pergunta 3: Ranking da Redação",
    4:  "Pergunta 4: Mães com Ensino Superior",
    5:  "Pergunta 5: Alto Desempenho (>700)",
    6:  "Pergunta 6: Distribuição por Sexo",
    7:  "Pergunta 7: Gap de Gênero",
    8:  "Pergunta 8: Renda, Escola e Desempenho",
    9:  "Pergunta 9: Redação em Branco vs Violação",
    10: "Pergunta 10: Defasagem por Área",
    11: "Pergunta 11: Escolas Urbanas vs Rurais",
    12: "Pergunta 12: Desempenho Crítico (<400)",
    13: "Pergunta 13: Ausência: 1º vs 2º Dia",
    14: "Pergunta 14: Treineiros",
    15: "Pergunta 15: Inglês vs Espanhol",
    16: "Pergunta 16: Candidatos Indígenas",
    17: "Pergunta 17: Nota Máxima na Redação",
    18: "Pergunta 18: Desempenho por Idade",
    19: "Pergunta 19: Idade da Elite (>700)",
    20: "Pergunta 20: Acesso à Internet",
}


# ─── Carregamento de Dados ───────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_data():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        'microdados_enem_2022.parquet')
    df = pd.read_parquet(path)

    for c in ['SG_UF_PROVA', 'TP_SEXO', 'Q002', 'Q006', 'Q025']:
        df[c] = df[c].astype('category')

    df['REGIAO'] = df['SG_UF_PROVA'].map(UF_REGIAO)
    df['IS_NE'] = df['REGIAO'] == 'Nordeste'
    df['GRUPO'] = df['IS_NE'].map({True: 'Nordeste', False: 'Demais Regiões'})

    notas = df[['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO']]
    df['MEDIA_GERAL'] = notas.mean(axis=1)

    df['FAIXA_GRUPO'] = df['TP_FAIXA_ETARIA'].map(FAIXA_GRUPO)
    df['IDADE_APROX'] = df['TP_FAIXA_ETARIA'].map(FAIXA_IDADE)
    return df


# ─── Helpers ─────────────────────────────────────────────────────────────────
def _cores_regioes(regioes):
    return [CORES_REGIAO.get(r, '#95A5A6') for r in regioes]


def _bar_ne_demais(result, y_col, y_label, title, fmt=".1f", pct=False):
    sfx = "%" if pct else ""
    colors = [COR_NE if g == 'Nordeste' else COR_DEMAIS for g in result['GRUPO']]
    fig = go.Figure(go.Bar(
        x=result['GRUPO'], y=result[y_col],
        marker_color=colors,
        text=[f"{v:{fmt}}{sfx}" for v in result[y_col]],
        textposition='outside',
    ))
    fig.update_layout(title=title, xaxis_title="", yaxis_title=y_label,
                      yaxis=dict(range=[0, result[y_col].max() * 1.3]))
    return fig


# ─── Gráficos ────────────────────────────────────────────────────────────────

def grafico_p1(df):
    evadido = (
        (df['TP_PRESENCA_CN'] == 0) | (df['TP_PRESENCA_CH'] == 0) |
        (df['TP_PRESENCA_LC'] == 0) | (df['TP_PRESENCA_MT'] == 0)
    )
    res = df.assign(EV=evadido).groupby('REGIAO')['EV'].mean().reset_index()
    res['TAXA'] = res['EV'] * 100
    res = res.sort_values('TAXA', ascending=True)

    fig = go.Figure(go.Bar(
        x=res['REGIAO'], y=res['TAXA'],
        marker_color=_cores_regioes(res['REGIAO']),
        text=[f"{v:.1f}%" for v in res['TAXA']], textposition='outside',
    ))
    fig.update_layout(title="Taxa de Evasão por Região", xaxis_title="Região",
                      yaxis_title="Taxa de Evasão (%)",
                      yaxis=dict(range=[0, res['TAXA'].max() * 1.25]))

    rank = res.sort_values('TAXA', ascending=False).reset_index(drop=True)
    rank['POS'] = range(1, len(rank) + 1)
    pos = rank.loc[rank['REGIAO'] == 'Nordeste', 'POS'].values[0]
    taxa = rank.loc[rank['REGIAO'] == 'Nordeste', 'TAXA'].values[0]
    return fig, f"O Nordeste ocupa a **{pos}ª posição** no ranking de evasão com taxa de **{taxa:.1f}%**."


def grafico_p2(df):
    pres = df[df['TP_PRESENCA_LC'] == 1]
    res = pres.assign(ZEROU=(pres['NU_NOTA_REDACAO'] == 0)).groupby('GRUPO')['ZEROU'].mean().reset_index()
    res['TAXA'] = res['ZEROU'] * 100
    fig = _bar_ne_demais(res, 'TAXA', 'Taxa de Nota Zero (%)',
                         'Taxa de Notas Zeradas na Redação', pct=True)
    ne = res.loc[res['GRUPO'] == 'Nordeste', 'TAXA'].values[0]
    out = res.loc[res['GRUPO'] == 'Demais Regiões', 'TAXA'].values[0]
    d = "maior" if ne > out else "menor"
    return fig, f"Nordeste: **{ne:.1f}%** | Demais: **{out:.1f}%** — taxa **{abs(ne-out):.1f} p.p. {d}** no Nordeste."


def grafico_p3(df):
    pres = df[(df['TP_PRESENCA_LC'] == 1) & df['NU_NOTA_REDACAO'].notna()]
    res = pres.groupby('REGIAO')['NU_NOTA_REDACAO'].mean().reset_index(name='MEDIA')
    res = res.sort_values('MEDIA', ascending=True)

    fig = go.Figure(go.Bar(
        x=res['REGIAO'], y=res['MEDIA'],
        marker_color=_cores_regioes(res['REGIAO']),
        text=[f"{v:.1f}" for v in res['MEDIA']], textposition='outside',
    ))
    fig.update_layout(title="Média da Redação por Região", xaxis_title="Região",
                      yaxis_title="Média", yaxis=dict(range=[0, res['MEDIA'].max() * 1.15]))

    rank = res.sort_values('MEDIA', ascending=False).reset_index(drop=True)
    rank['POS'] = range(1, len(rank) + 1)
    pos = rank.loc[rank['REGIAO'] == 'Nordeste', 'POS'].values[0]
    m = rank.loc[rank['REGIAO'] == 'Nordeste', 'MEDIA'].values[0]
    return fig, f"O Nordeste ocupa a **{pos}ª posição** com média de **{m:.1f}** pontos na Redação."


def grafico_p4(df):
    tmp = df[df['Q002'].notna()]
    res = tmp.assign(SUP=tmp['Q002'].isin(['F', 'G'])).groupby('GRUPO')['SUP'].mean().reset_index()
    res['TAXA'] = res['SUP'] * 100
    fig = _bar_ne_demais(res, 'TAXA', 'Proporção (%)',
                         'Mãe com Ensino Superior Completo', pct=True)
    ne = res.loc[res['GRUPO'] == 'Nordeste', 'TAXA'].values[0]
    out = res.loc[res['GRUPO'] == 'Demais Regiões', 'TAXA'].values[0]
    return fig, f"Nordeste: **{ne:.1f}%** | Demais: **{out:.1f}%** das mães com ensino superior."


def grafico_p5(df):
    tmp = df[df['MEDIA_GERAL'].notna()]
    res = tmp.assign(A7=(tmp['MEDIA_GERAL'] > 700)).groupby('GRUPO')['A7'].mean().reset_index()
    res['TAXA'] = res['A7'] * 100
    fig = _bar_ne_demais(res, 'TAXA', 'Proporção (%)',
                         'Candidatos com Média Geral > 700', fmt=".2f", pct=True)
    ne = res.loc[res['GRUPO'] == 'Nordeste', 'TAXA'].values[0]
    out = res.loc[res['GRUPO'] == 'Demais Regiões', 'TAXA'].values[0]
    razao = out / ne if ne > 0 else float('inf')
    return fig, (f"Nordeste: **{ne:.2f}%** | Demais: **{out:.2f}%** — "
                 f"proporção **{razao:.1f}x maior** nas demais regiões.")


def grafico_p6(df):
    res = df.groupby(['GRUPO', 'TP_SEXO']).size().reset_index(name='N')
    res['PCT'] = res['N'] / res.groupby('GRUPO')['N'].transform('sum') * 100
    res['SEXO'] = res['TP_SEXO'].map({'M': 'Masculino', 'F': 'Feminino'})

    fig = px.bar(res, x='GRUPO', y='PCT', color='SEXO', barmode='group',
                 text=res['PCT'].apply(lambda v: f"{v:.1f}%"),
                 color_discrete_map={'Masculino': '#3498DB', 'Feminino': '#E74C3C'})
    fig.update_layout(title="Distribuição por Sexo", xaxis_title="",
                      yaxis_title="Proporção (%)", legend_title="Sexo")
    fig.update_traces(textposition='outside')

    ne_f = res.loc[(res['GRUPO'] == 'Nordeste') & (res['SEXO'] == 'Feminino'), 'PCT'].values[0]
    br_f = res.loc[(res['GRUPO'] == 'Demais Regiões') & (res['SEXO'] == 'Feminino'), 'PCT'].values[0]
    return fig, f"Feminino — Nordeste: **{ne_f:.1f}%** | Demais: **{br_f:.1f}%**."


def grafico_p7(df):
    tmp = df[df['MEDIA_GERAL'].notna()]
    res = tmp.groupby(['GRUPO', 'TP_SEXO'])['MEDIA_GERAL'].mean().reset_index()
    res['SEXO'] = res['TP_SEXO'].map({'M': 'Masculino', 'F': 'Feminino'})

    fig = px.bar(res, x='GRUPO', y='MEDIA_GERAL', color='SEXO', barmode='group',
                 text=res['MEDIA_GERAL'].apply(lambda v: f"{v:.1f}"),
                 color_discrete_map={'Masculino': '#3498DB', 'Feminino': '#E74C3C'})
    fig.update_layout(title="Média Geral por Sexo", xaxis_title="",
                      yaxis_title="Média Geral", legend_title="Sexo")
    fig.update_traces(textposition='outside')

    ne_m = res.loc[(res['GRUPO'] == 'Nordeste') & (res['SEXO'] == 'Masculino'), 'MEDIA_GERAL'].values[0]
    ne_f = res.loc[(res['GRUPO'] == 'Nordeste') & (res['SEXO'] == 'Feminino'), 'MEDIA_GERAL'].values[0]
    br_m = res.loc[(res['GRUPO'] == 'Demais Regiões') & (res['SEXO'] == 'Masculino'), 'MEDIA_GERAL'].values[0]
    br_f = res.loc[(res['GRUPO'] == 'Demais Regiões') & (res['SEXO'] == 'Feminino'), 'MEDIA_GERAL'].values[0]
    return fig, (f"Gap (M−F): Nordeste **{ne_m - ne_f:+.1f}** pts | "
                 f"Demais **{br_m - br_f:+.1f}** pts.")


def grafico_p8(df):
    tmp = df[(df['MEDIA_GERAL'].notna()) & df['Q006'].notna() & df['TP_ESCOLA'].isin([2, 3])].copy()
    tmp['RENDA'] = tmp['Q006'].map(RENDA_GRUPO)
    tmp['ESCOLA'] = tmp['TP_ESCOLA'].map({2: 'Pública', 3: 'Privada'})
    tmp['ALTO'] = tmp['MEDIA_GERAL'] > 600

    res = tmp.groupby(['GRUPO', 'RENDA', 'ESCOLA']).agg(
        TOTAL=('ALTO', 'count'), SOMA=('ALTO', 'sum')).reset_index()
    res['TAXA'] = res['SOMA'] / res['TOTAL'] * 100
    res['RENDA'] = pd.Categorical(res['RENDA'], categories=ORDEM_RENDA, ordered=True)
    res = res.sort_values('RENDA')

    fig = px.bar(res, x='RENDA', y='TAXA', color='GRUPO', facet_col='ESCOLA',
                 barmode='group',
                 text=res['TAXA'].apply(lambda v: f"{v:.0f}%"),
                 color_discrete_map={'Nordeste': COR_NE, 'Demais Regiões': COR_DEMAIS},
                 category_orders={'RENDA': ORDEM_RENDA,
                                  'GRUPO': ['Nordeste', 'Demais Regiões']})
    fig.update_layout(title="Taxa de Alto Desempenho (Média > 600) por Renda e Escola",
                      yaxis_title="Taxa (%)", height=500)
    fig.update_traces(textposition='outside')
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

    return fig, ("Quanto maior a renda, maior a taxa de alto desempenho. "
                 "A diferença entre Nordeste e demais regiões **diminui** nas faixas de renda mais altas.")


def grafico_p9(df):
    pres = df[(df['TP_PRESENCA_LC'] == 1) & df['TP_STATUS_REDACAO'].notna()].copy()
    pres['CAT'] = 'Nota normal'
    pres.loc[pres['TP_STATUS_REDACAO'] == 4, 'CAT'] = 'Em branco'
    pres.loc[pres['TP_STATUS_REDACAO'].isin([2, 3, 6, 7, 8, 9]), 'CAT'] = 'Violação de regras'

    anormal = pres[pres['CAT'] != 'Nota normal']
    totais = pres.groupby('GRUPO').size().reset_index(name='TOTAL')
    res = anormal.groupby(['GRUPO', 'CAT']).size().reset_index(name='N').merge(totais)
    res['TAXA'] = res['N'] / res['TOTAL'] * 100

    fig = px.bar(res, x='GRUPO', y='TAXA', color='CAT', barmode='group',
                 text=res['TAXA'].apply(lambda v: f"{v:.2f}%"),
                 color_discrete_map={'Em branco': '#E74C3C', 'Violação de regras': '#F39C12'})
    fig.update_layout(title="Redação: Em Branco vs Violação de Regras",
                      xaxis_title="", yaxis_title="Taxa (%)", legend_title="Categoria")
    fig.update_traces(textposition='outside')

    ne_b = res.loc[(res['GRUPO'] == 'Nordeste') & (res['CAT'] == 'Em branco'), 'TAXA']
    ne_b = ne_b.values[0] if len(ne_b) else 0
    ne_v = res.loc[(res['GRUPO'] == 'Nordeste') & (res['CAT'] == 'Violação de regras'), 'TAXA']
    ne_v = ne_v.values[0] if len(ne_v) else 0
    return fig, f"Nordeste — em branco: **{ne_b:.2f}%** | violação: **{ne_v:.2f}%**."


def grafico_p10(df):
    areas = {'Ciências da Natureza': 'NU_NOTA_CN', 'Ciências Humanas': 'NU_NOTA_CH',
             'Linguagens': 'NU_NOTA_LC', 'Matemática': 'NU_NOTA_MT',
             'Redação': 'NU_NOTA_REDACAO'}
    rows = []
    for area, col in areas.items():
        m_ne = df.loc[df['IS_NE'] & df[col].notna(), col].mean()
        m_out = df.loc[~df['IS_NE'] & df[col].notna(), col].mean()
        rows.append({'Área': area, 'Nordeste': m_ne, 'Demais': m_out,
                     'Defasagem': m_out - m_ne})
    res = pd.DataFrame(rows).sort_values('Defasagem')

    cores = ['#27AE60' if d <= 0 else '#E74C3C' for d in res['Defasagem']]
    fig = go.Figure(go.Bar(
        x=res['Área'], y=res['Defasagem'], marker_color=cores,
        text=[f"{v:+.1f}" for v in res['Defasagem']], textposition='outside',
    ))
    fig.update_layout(title="Defasagem do Nordeste em Relação às Demais Regiões",
                      xaxis_title="Área", yaxis_title="Defasagem (pts)")

    menor = res.iloc[0]
    maior = res.iloc[-1]
    return fig, (f"Menor defasagem: **{menor['Área']}** ({menor['Defasagem']:+.1f} pts) | "
                 f"Maior: **{maior['Área']}** ({maior['Defasagem']:+.1f} pts).")


def grafico_p11(df):
    tmp = df[df['TP_LOCALIZACAO_ESC'].isin([1, 2]) & df['MEDIA_GERAL'].notna()].copy()
    tmp['LOCAL'] = tmp['TP_LOCALIZACAO_ESC'].map({1: 'Urbana', 2: 'Rural'})
    res = tmp.groupby(['GRUPO', 'LOCAL'])['MEDIA_GERAL'].mean().reset_index()

    fig = px.bar(res, x='GRUPO', y='MEDIA_GERAL', color='LOCAL', barmode='group',
                 text=res['MEDIA_GERAL'].apply(lambda v: f"{v:.1f}"),
                 color_discrete_map={'Urbana': '#3498DB', 'Rural': '#E67E22'})
    fig.update_layout(title="Média Geral: Escolas Urbanas vs Rurais",
                      xaxis_title="", yaxis_title="Média Geral", legend_title="Localização")
    fig.update_traces(textposition='outside')

    ne_u = res.loc[(res['GRUPO'] == 'Nordeste') & (res['LOCAL'] == 'Urbana'), 'MEDIA_GERAL'].values[0]
    ne_r = res.loc[(res['GRUPO'] == 'Nordeste') & (res['LOCAL'] == 'Rural'), 'MEDIA_GERAL'].values[0]
    br_u = res.loc[(res['GRUPO'] == 'Demais Regiões') & (res['LOCAL'] == 'Urbana'), 'MEDIA_GERAL'].values[0]
    br_r = res.loc[(res['GRUPO'] == 'Demais Regiões') & (res['LOCAL'] == 'Rural'), 'MEDIA_GERAL'].values[0]
    return fig, (f"Gap urbana−rural: Nordeste **{ne_u - ne_r:.1f}** pts | "
                 f"Demais **{br_u - br_r:.1f}** pts.")


def grafico_p12(df):
    tmp = df[df['MEDIA_GERAL'].notna()].copy()
    tmp['CRIT'] = tmp['MEDIA_GERAL'] < 400

    # NE vs Demais
    g = tmp.groupby('GRUPO')['CRIT'].mean().reset_index()
    g['TAXA'] = g['CRIT'] * 100

    # Por estado NE
    ne = tmp[tmp['IS_NE']]
    uf = ne.groupby('SG_UF_PROVA')['CRIT'].mean().reset_index()
    uf['TAXA'] = uf['CRIT'] * 100
    uf = uf.sort_values('TAXA', ascending=False)

    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=['Nordeste vs Demais', 'Por Estado (NE)'],
                        column_widths=[0.35, 0.65])
    fig.add_trace(go.Bar(
        x=g['GRUPO'], y=g['TAXA'],
        marker_color=[COR_NE if x == 'Nordeste' else COR_DEMAIS for x in g['GRUPO']],
        text=[f"{v:.1f}%" for v in g['TAXA']], textposition='outside', showlegend=False,
    ), row=1, col=1)
    fig.add_trace(go.Bar(
        x=uf['SG_UF_PROVA'].astype(str), y=uf['TAXA'],
        marker_color=COR_NE,
        text=[f"{v:.1f}%" for v in uf['TAXA']], textposition='outside', showlegend=False,
    ), row=1, col=2)
    fig.update_layout(title="Proporção com Média < 400 (Desempenho Crítico)", height=450)
    fig.update_yaxes(title_text="Taxa (%)", row=1, col=1)

    ne_t = g.loc[g['GRUPO'] == 'Nordeste', 'TAXA'].values[0]
    pior = uf.iloc[0]
    return fig, (f"Nordeste: **{ne_t:.1f}%** com média < 400. "
                 f"Estado com maior proporção: **{pior['SG_UF_PROVA']}** ({pior['TAXA']:.1f}%).")


def grafico_p13(df):
    # Dia 1 = LC + CH (+Redação), Dia 2 = CN + MT
    d1 = (df['TP_PRESENCA_LC'] == 0) | (df['TP_PRESENCA_CH'] == 0)
    d2 = (df['TP_PRESENCA_CN'] == 0) | (df['TP_PRESENCA_MT'] == 0)
    rows = []
    for grupo in ['Nordeste', 'Demais Regiões']:
        mask = df['GRUPO'] == grupo
        rows.append({'Grupo': grupo, 'Dia': '1º dia (LC+CH)', 'Taxa': d1[mask].mean() * 100})
        rows.append({'Grupo': grupo, 'Dia': '2º dia (CN+MT)', 'Taxa': d2[mask].mean() * 100})
    res = pd.DataFrame(rows)

    fig = px.bar(res, x='Grupo', y='Taxa', color='Dia', barmode='group',
                 text=res['Taxa'].apply(lambda v: f"{v:.1f}%"),
                 color_discrete_map={'1º dia (LC+CH)': '#3498DB', '2º dia (CN+MT)': '#E74C3C'})
    fig.update_layout(title="Taxa de Ausência: 1º vs 2º Dia", xaxis_title="",
                      yaxis_title="Taxa de Ausência (%)", legend_title="Dia")
    fig.update_traces(textposition='outside')

    ne1 = res.loc[(res['Grupo'] == 'Nordeste') & (res['Dia'] == '1º dia (LC+CH)'), 'Taxa'].values[0]
    ne2 = res.loc[(res['Grupo'] == 'Nordeste') & (res['Dia'] == '2º dia (CN+MT)'), 'Taxa'].values[0]
    return fig, (f"Nordeste — 1º dia: **{ne1:.1f}%** | 2º dia: **{ne2:.1f}%** "
                 f"(diferença de **{ne2 - ne1:+.1f} p.p.**).")


def grafico_p14(df):
    tmp = df[df['MEDIA_GERAL'].notna()].copy()
    tmp['TIPO'] = tmp['IN_TREINEIRO'].map({0: 'Regular', 1: 'Treineiro'})
    tmp = tmp[tmp['TIPO'].notna()]
    res = tmp.groupby(['GRUPO', 'TIPO'])['MEDIA_GERAL'].mean().reset_index()

    fig = px.bar(res, x='GRUPO', y='MEDIA_GERAL', color='TIPO', barmode='group',
                 text=res['MEDIA_GERAL'].apply(lambda v: f"{v:.1f}"),
                 color_discrete_map={'Regular': '#3498DB', 'Treineiro': '#E74C3C'})
    fig.update_layout(title="Média Geral: Treineiros vs Regulares",
                      xaxis_title="", yaxis_title="Média Geral", legend_title="Tipo")
    fig.update_traces(textposition='outside')

    ne = res.loc[(res['GRUPO'] == 'Nordeste') & (res['TIPO'] == 'Treineiro'), 'MEDIA_GERAL'].values[0]
    br = res.loc[(res['GRUPO'] == 'Demais Regiões') & (res['TIPO'] == 'Treineiro'), 'MEDIA_GERAL'].values[0]
    return fig, f"Treineiros — Nordeste: **{ne:.1f}** | Demais: **{br:.1f}** (diferença de **{br-ne:.1f}** pts)."


def grafico_p15(df):
    tmp = df[df['TP_LINGUA'].notna()].copy()
    tmp['LINGUA'] = tmp['TP_LINGUA'].map({0: 'Inglês', 1: 'Espanhol'})
    res = tmp.groupby(['GRUPO', 'LINGUA']).size().reset_index(name='N')
    res['PCT'] = res['N'] / res.groupby('GRUPO')['N'].transform('sum') * 100

    fig = px.bar(res, x='GRUPO', y='PCT', color='LINGUA', barmode='group',
                 text=res['PCT'].apply(lambda v: f"{v:.1f}%"),
                 color_discrete_map={'Inglês': '#3498DB', 'Espanhol': '#E74C3C'})
    fig.update_layout(title="Escolha de Língua Estrangeira",
                      xaxis_title="", yaxis_title="Proporção (%)", legend_title="Língua")
    fig.update_traces(textposition='outside')

    ne_e = res.loc[(res['GRUPO'] == 'Nordeste') & (res['LINGUA'] == 'Espanhol'), 'PCT'].values[0]
    br_e = res.loc[(res['GRUPO'] == 'Demais Regiões') & (res['LINGUA'] == 'Espanhol'), 'PCT'].values[0]
    return fig, f"Espanhol — Nordeste: **{ne_e:.1f}%** | Demais: **{br_e:.1f}%**."


def grafico_p16(df):
    ind = df[(df['TP_COR_RACA'] == 5) & df['MEDIA_GERAL'].notna()]
    media_nac = df.loc[df['MEDIA_GERAL'].notna(), 'MEDIA_GERAL'].mean()

    res = ind.groupby('REGIAO')['MEDIA_GERAL'].mean().reset_index(name='MEDIA')
    res = res.sort_values('MEDIA', ascending=True)

    fig = go.Figure(go.Bar(
        x=res['REGIAO'], y=res['MEDIA'],
        marker_color=_cores_regioes(res['REGIAO']),
        text=[f"{v:.1f}" for v in res['MEDIA']], textposition='outside',
    ))
    fig.add_hline(y=media_nac, line_dash="dash", line_color="gray",
                  annotation_text=f"Média nacional geral: {media_nac:.1f}")
    fig.update_layout(title="Média dos Candidatos Indígenas por Região",
                      xaxis_title="Região", yaxis_title="Média Geral")

    ne_m = res.loc[res['REGIAO'] == 'Nordeste', 'MEDIA'].values[0]
    return fig, (f"Indígenas do Nordeste: média **{ne_m:.1f}** "
                 f"(**{ne_m - media_nac:+.1f}** pts vs média nacional geral).")


def grafico_p17(df):
    pres = df[(df['TP_PRESENCA_LC'] == 1) & df['NU_NOTA_REDACAO'].notna()]
    total = pres.groupby('REGIAO').size().reset_index(name='TOTAL')
    nota_max = pres[pres['NU_NOTA_REDACAO'] == 1000].groupby('REGIAO').size().reset_index(name='MAX')
    res = total.merge(nota_max, on='REGIAO', how='left').fillna(0)
    res['TAXA'] = res['MAX'] / res['TOTAL'] * 100
    res = res.sort_values('TAXA', ascending=True)

    fig = go.Figure(go.Bar(
        x=res['REGIAO'], y=res['TAXA'],
        marker_color=_cores_regioes(res['REGIAO']),
        text=[f"{v:.3f}%" for v in res['TAXA']], textposition='outside',
    ))
    fig.update_layout(title="Taxa de Nota 1000 na Redação por Região",
                      xaxis_title="Região", yaxis_title="Taxa (%)",
                      yaxis=dict(range=[0, res['TAXA'].max() * 1.4]))

    ne = res.loc[res['REGIAO'] == 'Nordeste', 'TAXA'].values[0]
    melhor = res.iloc[-1]
    return fig, (f"Nordeste: **{ne:.4f}%** de nota 1000 | "
                 f"Maior taxa: **{melhor['REGIAO']}** ({melhor['TAXA']:.4f}%).")


def grafico_p18(df):
    tmp = df[df['MEDIA_GERAL'].notna() & df['FAIXA_GRUPO'].notna()]
    ordem = ['<17', '17-18', '19-21', '22-25', '26-30', '31+']
    res = tmp.groupby(['GRUPO', 'FAIXA_GRUPO'])['MEDIA_GERAL'].mean().reset_index()
    res['FAIXA_GRUPO'] = pd.Categorical(res['FAIXA_GRUPO'], categories=ordem, ordered=True)
    res = res.sort_values('FAIXA_GRUPO')

    fig = px.line(res, x='FAIXA_GRUPO', y='MEDIA_GERAL', color='GRUPO', markers=True,
                  color_discrete_map={'Nordeste': COR_NE, 'Demais Regiões': COR_DEMAIS})
    fig.update_layout(title="Média Geral por Faixa Etária", xaxis_title="Faixa Etária",
                      yaxis_title="Média Geral", legend_title="")

    piv = res.pivot(index='FAIXA_GRUPO', columns='GRUPO', values='MEDIA_GERAL')
    piv['GAP'] = piv['Demais Regiões'] - piv['Nordeste']
    faixa_max = piv['GAP'].idxmax()
    gap_max = piv['GAP'].max()
    return fig, f"Maior defasagem na faixa **{faixa_max}** (**{gap_max:.1f}** pts)."


def grafico_p19(df):
    tmp = df[df['MEDIA_GERAL'].notna() & df['IDADE_APROX'].notna()]
    elite = tmp[tmp['MEDIA_GERAL'] > 700]
    m_ne = elite.loc[elite['IS_NE'], 'IDADE_APROX'].mean()
    m_br = elite.loc[~elite['IS_NE'], 'IDADE_APROX'].mean()

    ordem = ['<17', '17-18', '19-21', '22-25', '26-30', '31+']
    res = elite.groupby(['GRUPO', 'FAIXA_GRUPO']).size().reset_index(name='N')
    res['PCT'] = res['N'] / res.groupby('GRUPO')['N'].transform('sum') * 100
    res['FAIXA_GRUPO'] = pd.Categorical(res['FAIXA_GRUPO'], categories=ordem, ordered=True)
    res = res.sort_values('FAIXA_GRUPO')

    fig = px.bar(res, x='FAIXA_GRUPO', y='PCT', color='GRUPO', barmode='group',
                 text=res['PCT'].apply(lambda v: f"{v:.1f}%"),
                 color_discrete_map={'Nordeste': COR_NE, 'Demais Regiões': COR_DEMAIS})
    fig.update_layout(title="Distribuição Etária — Candidatos com Média > 700",
                      xaxis_title="Faixa Etária", yaxis_title="Proporção (%)", legend_title="")
    fig.update_traces(textposition='outside')

    direcao = "mais velhos" if m_ne > m_br else "mais novos"
    return fig, (f"Idade média (elite): Nordeste **{m_ne:.1f}** anos | "
                 f"Demais **{m_br:.1f}** anos — elite nordestina é **{direcao}**.")


def grafico_p20(df):
    tmp = df[df['MEDIA_GERAL'].notna() & df['Q025'].notna()].copy()
    # Determina dinamicamente qual grupo é "com internet" (maior média)
    medias = tmp.groupby('Q025')['MEDIA_GERAL'].mean()
    if medias.get('B', 0) > medias.get('A', 0):
        label = {'A': 'Sem internet', 'B': 'Com internet'}
    else:
        label = {'A': 'Com internet', 'B': 'Sem internet'}
    tmp['INTERNET'] = tmp['Q025'].map(label)

    res = tmp.groupby(['GRUPO', 'INTERNET'])['MEDIA_GERAL'].mean().reset_index()

    fig = px.bar(res, x='GRUPO', y='MEDIA_GERAL', color='INTERNET', barmode='group',
                 text=res['MEDIA_GERAL'].apply(lambda v: f"{v:.1f}"),
                 color_discrete_map={'Com internet': '#27AE60', 'Sem internet': '#E74C3C'})
    fig.update_layout(title="Média Geral por Acesso à Internet em Casa",
                      xaxis_title="", yaxis_title="Média Geral", legend_title="Internet")
    fig.update_traces(textposition='outside')

    ne_c = res.loc[(res['GRUPO'] == 'Nordeste') & (res['INTERNET'] == 'Com internet'), 'MEDIA_GERAL'].values[0]
    ne_s = res.loc[(res['GRUPO'] == 'Nordeste') & (res['INTERNET'] == 'Sem internet'), 'MEDIA_GERAL'].values[0]
    br_c = res.loc[(res['GRUPO'] == 'Demais Regiões') & (res['INTERNET'] == 'Com internet'), 'MEDIA_GERAL'].values[0]
    br_s = res.loc[(res['GRUPO'] == 'Demais Regiões') & (res['INTERNET'] == 'Sem internet'), 'MEDIA_GERAL'].values[0]
    g_ne, g_br = ne_c - ne_s, br_c - br_s
    mais = "mais" if g_ne > g_br else "menos"
    return fig, (f"Gap com/sem internet: Nordeste **{g_ne:.1f}** pts | Demais **{g_br:.1f}** pts. "
                 f"O acesso impacta **{mais}** no Nordeste.")


# ─── Mapeamento de funções ───────────────────────────────────────────────────
FUNCOES = {
    1: grafico_p1, 2: grafico_p2, 3: grafico_p3, 4: grafico_p4,
    5: grafico_p5, 6: grafico_p6, 7: grafico_p7, 8: grafico_p8,
    9: grafico_p9, 10: grafico_p10, 11: grafico_p11, 12: grafico_p12,
    13: grafico_p13, 14: grafico_p14, 15: grafico_p15, 16: grafico_p16,
    17: grafico_p17, 18: grafico_p18, 19: grafico_p19, 20: grafico_p20,
}


# ─── Tab: Contexto ─────────────────────────────────────────────────────────
def _card(icon, title, body):
    st.markdown(f"""
    <div style="
        background: #ffffff;
        border: 1px solid #e9ecef;
        border-radius: 12px;
        padding: 1.5rem 1.8rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    ">
        <div style="display: flex; align-items: flex-start; gap: 1rem;">
            <div style="font-size: 1.8rem; line-height: 1;">{icon}</div>
            <div>
                <h3 style="margin: 0 0 0.5rem 0; color: #1a3a5c;">{title}</h3>
                <div style="color: #2c3e50; line-height: 1.7; font-size: 1rem;">{body}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def tab_contexto():
    st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h1 style="color: #1a3a5c; margin-bottom: 0.3rem;">📖 Contexto da Análise</h1>
        <div style="background: #f0f4f8; border-radius: 8px; padding: 0.8rem 1.2rem; color: #34495e; font-size: 1rem;">
            Por que comparar o Nordeste com o restante do Brasil nos microdados do ENEM 2022
        </div>
    </div>
    """, unsafe_allow_html=True)

    _card(
        "🎯",
        "Por que esta análise importa?",
        """
        O <strong>ENEM</strong> (Exame Nacional do Ensino Médio) é a principal porta de entrada para o
        ensino superior no Brasil, com mais de <strong>3 milhões de inscritos</strong> a cada edição.
        Universidades federais, programas como <strong>Prouni</strong> e <strong>FIES</strong> utilizam a nota do
        exame como critério de seleção — o que torna o ENEM um instrumento decisivo na
        trajetória de milhões de jovens brasileiros.
        """
    )

    _card(
        "🌎",
        "A questão regional",
        """
        O Brasil convive com <strong>desigualdades regionais históricas</strong>. O Nordeste, em
        particular, concentra indicadores socioeconômicos abaixo da média nacional em
        dimensões como renda <em>per capita</em>, acesso a saneamento e infraestrutura escolar.<br><br>
        <em>Essas disparidades estruturais se refletem nos resultados educacionais?</em>
        """
    )

    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #1a3a5c 0%, #1e5799 100%);
        border-radius: 12px;
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
        color: #ffffff;
    ">
        <h3 style="margin: 0 0 0.8rem 0; color: #ffffff;">📋 Dimensões analisadas</h3>
        <p style="margin-bottom: 1rem; opacity: 0.9; font-size: 1rem;">
            Esta análise compara o desempenho dos candidatos nordestinos com o <strong>restante do
            Brasil</strong> (as demais 4 regiões somadas) em <strong>20 dimensões</strong> diferentes:
        </p>
        <table style="width: 100%; border-collapse: separate; border-spacing: 0.5rem;">
            <tr>
                <td style="background: rgba(255,255,255,0.12); border-radius: 8px; padding: 0.8rem 1rem; width: 50%;">
                    <span style="font-weight: 700;">👥 Presença e evasão</span><br>
                    <span style="opacity: 0.85; font-size: 0.9rem;">quem falta mais?</span>
                </td>
                <td style="background: rgba(255,255,255,0.12); border-radius: 8px; padding: 0.8rem 1rem; width: 50%;">
                    <span style="font-weight: 700;">📚 Desempenho por área</span><br>
                    <span style="opacity: 0.85; font-size: 0.9rem;">em qual disciplina a defasagem é maior?</span>
                </td>
            </tr>
            <tr>
                <td style="background: rgba(255,255,255,0.12); border-radius: 8px; padding: 0.8rem 1rem;">
                    <span style="font-weight: 700;">🏦 Perfil socioeconômico</span><br>
                    <span style="opacity: 0.85; font-size: 0.9rem;">renda, escolaridade dos pais e tipo de escola</span>
                </td>
                <td style="background: rgba(255,255,255,0.12); border-radius: 8px; padding: 0.8rem 1rem;">
                    <span style="font-weight: 700;">👤 Fatores demográficos</span><br>
                    <span style="opacity: 0.85; font-size: 0.9rem;">sexo, idade, localização e etnia</span>
                </td>
            </tr>
            <tr>
                <td style="background: rgba(255,255,255,0.12); border-radius: 8px; padding: 0.8rem 1rem;">
                    <span style="font-weight: 700;">🌐 Acesso a recursos</span><br>
                    <span style="opacity: 0.85; font-size: 0.9rem;">internet em casa, idioma estrangeiro</span>
                </td>
                <td></td>
            </tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

    _card(
        "🔍",
        "O que esperamos encontrar",
        """
        A hipótese é que as <strong>desigualdades estruturais</strong> entre o Nordeste e as demais
        regiões se manifestam nos microdados do ENEM — mas <strong>não de forma uniforme</strong>.<br><br>
        Algumas defasagens podem ser maiores do que o esperado em áreas específicas,
        enquanto em outras o Nordeste pode surpreender positivamente. O objetivo é
        <strong>quantificar</strong> essas diferenças para informar políticas públicas baseadas em
        evidência.
        """
    )

# ─── Tab: Tratamento de Dados ──────────────────────────────────────────────
def _etapa_card(num, titulo, descricao, motivo, icone):
    st.markdown(f"""
    <div style="
        background: #ffffff;
        border: 1px solid #e9ecef;
        border-radius: 12px;
        padding: 1.3rem 1.8rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04);
        display: flex;
        align-items: flex-start;
        gap: 1.2rem;
    ">
        <div style="
            background: {'#D35400' if num == 7 else '#1a3a5c'};
            color: #ffffff;
            border-radius: 50%;
            width: 2.4rem;
            height: 2.4rem;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 0.95rem;
            flex-shrink: 0;
        ">{num}</div>
        <div style="flex: 1;">
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.4rem;">
                <span style="font-size: 1.15rem;">{icone}</span>
                <h3 style="margin: 0; color: #1a3a5c; font-size: 1.1rem;">{titulo}</h3>
            </div>
            <p style="color: #2c3e50; margin: 0 0 0.5rem 0; line-height: 1.6;">{descricao}</p>
            <div style="
                background: #f0f4f8;
                border-radius: 6px;
                padding: 0.5rem 0.9rem;
                font-size: 0.88rem;
                color: #34495e;
                display: inline-block;
            ">
                💡 {motivo}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def tab_tratamento():
    st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h1 style="color: #1a3a5c; margin-bottom: 0.3rem;">⚙️ Pipeline de Tratamento dos Dados</h1>
        <div style="background: #f0f4f8; border-radius: 8px; padding: 0.8rem 1.2rem; color: #34495e; font-size: 1rem;">
            Todas as transformações aplicadas dos microdados brutos até o dataset final
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
        border-radius: 12px;
        padding: 1.2rem 1.8rem;
        margin-bottom: 1.8rem;
        color: #ffffff;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
    ">
        <div><strong>📄 Arquivo original:</strong> CSV · ~1,5 GB · 76 colunas · 3.476.105 linhas</div>
        <div><strong>📦 Arquivo final:</strong> Parquet · ~36 MB · 27 colunas</div>
        <div style="
            background: #27AE60;
            padding: 0.25rem 0.9rem;
            border-radius: 20px;
            font-weight: 700;
            font-size: 0.9rem;
        ">⬇ 42× menor</div>
    </div>
    """, unsafe_allow_html=True)

    _etapa_card(1,
        "Seleção de colunas",
        "Das 76 colunas originais, selecionamos <strong>21</strong> relevantes para as perguntas desta análise.",
        "Reduzir o consumo de memória (~441 MB → menos no carregamento) e manter apenas variáveis diretamente ligadas às hipóteses investigadas.",
        "📑")

    _etapa_card(2,
        "Encoding Latin-1",
        "O arquivo original utiliza <code>encoding='latin-1'</code> (ISO-8859-1).",
        "Arquivos governamentais brasileiros frequentemente usam essa codificação para suportar caracteres acentuados como <strong>ç</strong>, <strong>ã</strong>, <strong>õ</strong>.",
        "🔤")

    _etapa_card(3,
        "Separador ponto-e-vírgula",
        "O CSV usa <code>;</code> como delimitador (<code>sep=';'</code>).",
        "Padrão adotado pelo INEP na divulgação de microdados — evita conflitos com vírgulas decimais nos valores numéricos.",
        "🔀")

    _etapa_card(4,
        "Conversão numérica",
        "Colunas como <code>NU_NOTA_CN</code>, <code>TP_PRESENCA_CN</code>, <code>TP_FAIXA_ETARIA</code> etc. vêm como texto no CSV. Aplicamos <code>pd.to_numeric(..., errors='coerce')</code> para convertê-las a <code>int64</code>/<code>float64</code>.",
        "Permitir cálculos estatísticos (média, soma) e filtros numéricos. Valores inválidos são convertidos para <strong>NaN</strong>.",
        "🔢")

    _etapa_card(5,
        "Colunas categóricas",
        "As colunas <code>SG_UF_PROVA</code>, <code>TP_SEXO</code>, <code>Q002</code>, <code>Q006</code> e <code>Q025</code> são convertidas para o dtype <code>category</code> do Pandas.",
        "Colunas com baixa cardinalidade (poucos valores únicos) ocupam menos memória como categorias — especialmente relevante num dataset de 3,5M de linhas.",
        "🏷️")

    # Etapa 6 — colunas derivadas com tabela estilizada
    st.markdown(f"""
    <div style="
        background: #ffffff;
        border: 1px solid #e9ecef;
        border-radius: 12px;
        padding: 1.3rem 1.8rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04);
        display: flex;
        align-items: flex-start;
        gap: 1.2rem;
    ">
        <div style="
            background: #1a3a5c;
            color: #ffffff;
            border-radius: 50%;
            width: 2.4rem;
            height: 2.4rem;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 0.95rem;
            flex-shrink: 0;
        ">6</div>
        <div style="flex: 1;">
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.4rem;">
                <span style="font-size: 1.15rem;">🧩</span>
                <h3 style="margin: 0; color: #1a3a5c; font-size: 1.1rem;">Colunas derivadas</h3>
            </div>
            <p style="color: #2c3e50; margin: 0 0 0.8rem 0; line-height: 1.6;">
                Criamos <strong>6 colunas auxiliares</strong> a partir dos dados brutos:
            </p>
            <table style="width: 100%; border-collapse: collapse; font-size: 0.92rem; border-radius: 8px; overflow: hidden;">
                <thead>
                    <tr style="background: #1a3a5c; color: #ffffff;">
                        <th style="padding: 0.5rem 0.8rem; text-align: left;">Coluna</th>
                        <th style="padding: 0.5rem 0.8rem; text-align: left;">Origem</th>
                        <th style="padding: 0.5rem 0.8rem; text-align: left;">Propósito</th>
                    </tr>
                </thead>
                <tbody>
                    <tr style="background: #f8f9fa;">
                        <td style="padding: 0.5rem 0.8rem; border-bottom: 1px solid #eee;"><code>REGIAO</code></td>
                        <td style="padding: 0.5rem 0.8rem; border-bottom: 1px solid #eee;"><code>SG_UF_PROVA</code> → dicionário UF→Região</td>
                        <td style="padding: 0.5rem 0.8rem; border-bottom: 1px solid #eee;">Agrupar candidatos por região geográfica</td>
                    </tr>
                    <tr>
                        <td style="padding: 0.5rem 0.8rem; border-bottom: 1px solid #eee;"><code>IS_NE</code></td>
                        <td style="padding: 0.5rem 0.8rem; border-bottom: 1px solid #eee;"><code>REGIAO == 'Nordeste'</code></td>
                        <td style="padding: 0.5rem 0.8rem; border-bottom: 1px solid #eee;">Flag booleana para filtrar o grupo de interesse</td>
                    </tr>
                    <tr style="background: #f8f9fa;">
                        <td style="padding: 0.5rem 0.8rem; border-bottom: 1px solid #eee;"><code>GRUPO</code></td>
                        <td style="padding: 0.5rem 0.8rem; border-bottom: 1px solid #eee;"><code>IS_NE</code> → Nordeste / Demais Regiões</td>
                        <td style="padding: 0.5rem 0.8rem; border-bottom: 1px solid #eee;">Variável categórica usada em todos os gráficos comparativos</td>
                    </tr>
                    <tr>
                        <td style="padding: 0.5rem 0.8rem; border-bottom: 1px solid #eee;"><code>MEDIA_GERAL</code></td>
                        <td style="padding: 0.5rem 0.8rem; border-bottom: 1px solid #eee;">Média das 5 notas (CN, CH, LC, MT, Redação)</td>
                        <td style="padding: 0.5rem 0.8rem; border-bottom: 1px solid #eee;">Indicador sintético de desempenho</td>
                    </tr>
                    <tr style="background: #f8f9fa;">
                        <td style="padding: 0.5rem 0.8rem; border-bottom: 1px solid #eee;"><code>FAIXA_GRUPO</code></td>
                        <td style="padding: 0.5rem 0.8rem; border-bottom: 1px solid #eee;">Agrupamento de <code>TP_FAIXA_ETARIA</code> em 6 categorias</td>
                        <td style="padding: 0.5rem 0.8rem; border-bottom: 1px solid #eee;">Facilitar visualização etária</td>
                    </tr>
                    <tr>
                        <td style="padding: 0.5rem 0.8rem;"><code>IDADE_APROX</code></td>
                        <td style="padding: 0.5rem 0.8rem;"><code>TP_FAIXA_ETARIA</code> → valor central da faixa</td>
                        <td style="padding: 0.5rem 0.8rem;">Permitir cálculo de idade média</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
    """, unsafe_allow_html=True)

    _etapa_card(7,
        "Conversão para Parquet",
        "Após o tratamento, os dados são salvos em formato <strong>Parquet</strong> com compressão <strong>Snappy</strong>. O arquivo final tem <strong>~36 MB</strong>.",
        "Parquet é um formato colunar otimizado para leitura rápida — o app carrega os dados inteiros em <strong>menos de 1 segundo</strong>, contra 20–30 segundos do CSV original.",
        "🚀")

# ─── Tab: Visão Geral ────────────────────────────────────────────────────────
def tab_visao_geral(df):
    st.markdown(
        "Use os filtros abaixo para explorar os microdados do ENEM 2022 e comparar "
        "o desempenho do **Nordeste** com o **restante do Brasil**."
    )

    # ── Filtros ───────────────────────────────────────────────────────────────
    col_f1, col_f2, col_f3 = st.columns(3)

    # Filtro 1: Gênero
    sexo_map = {'M': 'Masculino', 'F': 'Feminino'}
    sexos_disp = sorted({sexo_map.get(str(s), str(s)) for s in df['TP_SEXO'].dropna().unique()})
    with col_f1:
        sexos_sel = st.multiselect(
            "⚥ Gênero", options=sexos_disp, default=sexos_disp, key="vg_sexo"
        )

    # Filtro 2 (escolha): Tipo de Escola
    escola_map = {2: 'Pública', 3: 'Privada'}
    escolas_present = sorted(df['TP_ESCOLA'].dropna().unique().astype(int).tolist())
    escolas_disp = [escola_map.get(v, str(v)) for v in escolas_present]
    with col_f2:
        escolas_sel = st.multiselect(
            "🏫 Tipo de Escola", options=escolas_disp, default=escolas_disp, key="vg_escola"
        )

    faixas_disp = ['<17', '17-18', '19-21', '22-25', '26-30', '31+']
    with col_f3:
        faixas_sel = st.multiselect(
            "🎂 Faixa Etária", options=faixas_disp, default=faixas_disp, key="vg_faixa"
        )

    # ── Filtragem ─────────────────────────────────────────────────────────────
    mask = (
        df['TP_SEXO'].map(lambda x: sexo_map.get(x, x)).isin(sexos_sel)
        & df['TP_ESCOLA'].map(lambda x: escola_map.get(x, x)).isin(escolas_sel)
        & df['FAIXA_GRUPO'].isin(faixas_sel)
    )
    dff = df[mask]

    if dff.empty:
        st.warning("Nenhum candidato encontrado com os filtros selecionados.")
        return

    # ── Candidatos válidos (sem duplicatas e sem ausentes completos) ───────────
    dff_validos = dff.drop_duplicates()
    presente = (
        (dff_validos['TP_PRESENCA_CN'] == 1) | (dff_validos['TP_PRESENCA_CH'] == 1)
        | (dff_validos['TP_PRESENCA_LC'] == 1) | (dff_validos['TP_PRESENCA_MT'] == 1)
    )
    dff_validos = dff_validos[presente]

    # ── KPIs ──────────────────────────────────────────────────────────────────
    st.markdown("---")
    k1, k2, k3, k4 = st.columns(4)
    total = len(dff_validos)
    media_geral = dff_validos['MEDIA_GERAL'].mean()
    media_red = dff_validos['NU_NOTA_REDACAO'].mean()
    presenca_plena = (
        (dff_validos['TP_PRESENCA_CN'] == 1) & (dff_validos['TP_PRESENCA_CH'] == 1)
        & (dff_validos['TP_PRESENCA_LC'] == 1) & (dff_validos['TP_PRESENCA_MT'] == 1)
    ).mean() * 100

    k1.metric("👥 Candidatos Presentes", f"{total:,}".replace(",", "."))
    k2.metric("📊 Média Geral", f"{media_geral:.1f}" if pd.notna(media_geral) else "—")
    k3.metric("✍️ Média Redação", f"{media_red:.1f}" if pd.notna(media_red) else "—")
    k4.metric("✅ Presença Plena", f"{presenca_plena:.1f}%")

    st.markdown("---")

    # ── Radar: perfil de notas por área — Nordeste vs Demais (sem Redação) ─────
    areas_label = ['Ciências da Natureza', 'Ciências Humanas', 'Linguagens', 'Matemática']
    areas_col   = ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT']

    ne_vals  = [dff_validos.loc[dff_validos['IS_NE']  & dff_validos[c].notna(), c].mean()
                for c in areas_col]
    dem_vals = [dff_validos.loc[~dff_validos['IS_NE'] & dff_validos[c].notna(), c].mean()
                for c in areas_col]

    # fechar o polígono
    cats  = areas_label + [areas_label[0]]
    ne_r  = ne_vals  + [ne_vals[0]]
    dem_r = dem_vals + [dem_vals[0]]

    r_min = max(0, min(ne_vals + dem_vals) - 15)
    r_max = max(ne_vals + dem_vals) + 15

    col_s1, col_s2 = st.columns(2)

    with col_s1:
        fig1 = go.Figure()
        fig1.add_trace(go.Scatterpolar(
            r=ne_r, theta=cats, fill='toself', name='Nordeste',
            line=dict(color=COR_NE, width=2),
            fillcolor=COR_NE,
            opacity=0.40,
            mode='lines+markers+text',
            text=[f"{v:.1f}" for v in ne_r],
            textposition='top center',
            textfont=dict(color='#000000', size=11, family='Arial'),
        ))
        fig1.add_trace(go.Scatterpolar(
            r=dem_r, theta=cats, fill='toself', name='Demais Regiões',
            line=dict(color=COR_DEMAIS, width=2),
            fillcolor=COR_DEMAIS,
            opacity=0.25,
            mode='lines+markers+text',
            text=[f"{v:.1f}" for v in dem_r],
            textposition='bottom center',
            textfont=dict(color='#000000', size=11, family='Arial'),
        ))
        fig1.update_layout(
            template='plotly_white',
            title=dict(
                text='Perfil de Notas por Área — Nordeste vs Demais',
                font=dict(color='#2c3e50', size=16),
            ),
            polar=dict(
                bgcolor='#fafafa',
                radialaxis=dict(
                    visible=True,
                    range=[r_min, r_max],
                    tickfont=dict(color='#444444', size=10),
                    gridcolor='#dddddd',
                ),
                angularaxis=dict(tickfont=dict(color='#2c3e50', size=11)),
            ),
            paper_bgcolor='#ffffff',
            plot_bgcolor='#ffffff',
            legend=dict(
                orientation='h', y=-0.18,
                font=dict(color='#2c3e50'),
            ),
            height=470,
        )
        st.plotly_chart(fig1, use_container_width=True)

    # ── Média por tipo de escola — Nordeste vs Demais ─────────────────────────
    with col_s2:
        dff_esc = dff_validos[
            dff_validos['TP_ESCOLA'].isin([2, 3]) & dff_validos['MEDIA_GERAL'].notna()
        ].copy()
        dff_esc['Escola'] = dff_esc['TP_ESCOLA'].map({2: 'Pública', 3: 'Privada'})
        res_esc = dff_esc.groupby(['GRUPO', 'Escola'])['MEDIA_GERAL'].mean().reset_index()
        fig2 = px.bar(
            res_esc, x='Escola', y='MEDIA_GERAL', color='GRUPO', barmode='group',
            text=res_esc['MEDIA_GERAL'].apply(lambda v: f"{v:.1f}"),
            color_discrete_map={'Nordeste': COR_NE, 'Demais Regiões': COR_DEMAIS},
            labels={'MEDIA_GERAL': 'Média Geral', 'GRUPO': '', 'Escola': 'Tipo de Escola'},
            title='Média Geral por Tipo de Escola — Nordeste vs Demais',
        )
        fig2.update_traces(textposition='outside')
        fig2.update_layout(height=450, legend_title_text='', yaxis=dict(
            range=[0, res_esc['MEDIA_GERAL'].max() * 1.18]
        ))
        st.plotly_chart(fig2, use_container_width=True)

    # ── Histograma + Boxplot ──────────────────────────────────────────────────
    col_h1, col_h2 = st.columns(2)

    with col_h1:
        dff_hist = dff_validos[dff_validos['MEDIA_GERAL'].notna() & dff_validos['GRUPO'].notna()]
        fig3 = px.histogram(
            dff_hist, x='MEDIA_GERAL', color='GRUPO', barmode='overlay', nbins=60,
            opacity=0.70,
            color_discrete_map={'Nordeste': COR_NE, 'Demais Regiões': COR_DEMAIS},
            labels={'MEDIA_GERAL': 'Média Geral', 'GRUPO': 'Grupo'},
            title='Distribuição da Média Geral — Nordeste vs Demais',
        )
        fig3.update_layout(height=430, legend_title_text='Grupo')
        st.plotly_chart(fig3, use_container_width=True)

    with col_h2:
        dff_box = dff_validos[dff_validos['MEDIA_GERAL'].notna() & dff_validos['REGIAO'].notna()]
        fig4 = px.box(
            dff_box, x='REGIAO', y='MEDIA_GERAL', color='REGIAO',
            color_discrete_map=CORES_REGIAO,
            labels={'REGIAO': 'Região', 'MEDIA_GERAL': 'Média Geral'},
            title='Boxplot da Média Geral por Região',
        )
        fig4.update_layout(height=430, showlegend=False)
        st.plotly_chart(fig4, use_container_width=True)

    # ── Média por Estado (barras horizontais com legenda de região) ───────────
    col_b1, col_b2 = st.columns(2)

    with col_b1:
        uf_med = (
            dff_validos[dff_validos['MEDIA_GERAL'].notna()]
            .groupby('SG_UF_PROVA', observed=True)['MEDIA_GERAL']
            .mean().reset_index()
        )
        uf_med.columns = ['UF', 'Média']
        uf_med['UF'] = uf_med['UF'].astype(str)
        uf_med['Região'] = uf_med['UF'].map(UF_REGIAO)
        uf_med = uf_med.sort_values('Média')

        fig5 = px.bar(
            uf_med, x='Média', y='UF', color='Região',
            color_discrete_map=CORES_REGIAO, orientation='h',
            text=uf_med['Média'].apply(lambda v: f"{v:.1f}"),
            labels={'Média': 'Média Geral', 'UF': 'Estado', 'Região': 'Região'},
            title='Média Geral por Estado',
        )
        fig5.update_traces(textposition='outside')
        fig5.update_layout(
            height=max(420, len(uf_med) * 22 + 100),
            legend_title_text='Região',
            xaxis=dict(range=[0, uf_med['Média'].max() * 1.12]),
        )
        st.plotly_chart(fig5, use_container_width=True)

    with col_b2:
        areas = {'Ciências da Natureza': 'NU_NOTA_CN', 'Ciências Humanas': 'NU_NOTA_CH',
                 'Linguagens': 'NU_NOTA_LC', 'Matemática': 'NU_NOTA_MT',
                 'Redação': 'NU_NOTA_REDACAO'}
        rows = []
        for area, col in areas.items():
            m_ne = dff_validos.loc[dff_validos['IS_NE'] & dff_validos[col].notna(), col].mean()
            m_dm = dff_validos.loc[~dff_validos['IS_NE'] & dff_validos[col].notna(), col].mean()
            if pd.notna(m_ne):
                rows.append({'Área': area, 'Grupo': 'Nordeste', 'Média': m_ne})
            if pd.notna(m_dm):
                rows.append({'Área': area, 'Grupo': 'Demais Regiões', 'Média': m_dm})
        if rows:
            res_area = pd.DataFrame(rows)
            fig6 = px.bar(
                res_area, x='Área', y='Média', color='Grupo', barmode='group',
                text=res_area['Média'].apply(lambda v: f"{v:.1f}"),
                color_discrete_map={'Nordeste': COR_NE, 'Demais Regiões': COR_DEMAIS},
                title='Média por Área de Conhecimento — Nordeste vs Demais',
            )
            fig6.update_traces(textposition='outside')
            fig6.update_layout(height=430, legend_title_text='Grupo')
            st.plotly_chart(fig6, use_container_width=True)

    # ── Média por Faixa Etária (linhas) ───────────────────────────────────────
    ordem_fx = ['<17', '17-18', '19-21', '22-25', '26-30', '31+']
    dff_fx = dff_validos[dff_validos['MEDIA_GERAL'].notna() & dff_validos['FAIXA_GRUPO'].notna()]
    res_fx = dff_fx.groupby(['GRUPO', 'FAIXA_GRUPO'])['MEDIA_GERAL'].mean().reset_index()
    res_fx['FAIXA_GRUPO'] = pd.Categorical(res_fx['FAIXA_GRUPO'], categories=ordem_fx, ordered=True)
    res_fx = res_fx.sort_values('FAIXA_GRUPO')

    fig7 = px.line(
        res_fx, x='FAIXA_GRUPO', y='MEDIA_GERAL', color='GRUPO', markers=True,
        color_discrete_map={'Nordeste': COR_NE, 'Demais Regiões': COR_DEMAIS},
        labels={'FAIXA_GRUPO': 'Faixa Etária', 'MEDIA_GERAL': 'Média Geral', 'GRUPO': ''},
        title='Média Geral por Faixa Etária — Nordeste vs Demais',
    )
    fig7.update_layout(height=400, legend_title_text='')
    st.plotly_chart(fig7, use_container_width=True)


# ─── Layout Principal ────────────────────────────────────────────────────────
def main():
    st.markdown("""
    <style>
        [data-testid="stSidebarContent"] { padding-top: 1rem; }
        .pergunta-box {
            background: linear-gradient(135deg, #1a3a5c 0%, #1e5799 100%);
            border-left: 6px solid #D35400;
            border-radius: 8px;
            padding: 1.1rem 1.4rem;
            color: #ffffff;
            font-size: 1.12rem;
            font-weight: 500;
            line-height: 1.6;
            margin-bottom: 1.2rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.18);
        }
        .pergunta-num {
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: #D35400;
            margin-bottom: 0.35rem;
        }
        .sidebar-pergunta-full {
            background: #1e1e2e;
            border-radius: 6px;
            padding: 0.7rem 0.9rem;
            font-size: 0.83rem;
            color: #d0d0e0;
            line-height: 1.55;
            margin-top: 0.4rem;
        }
    </style>
    """, unsafe_allow_html=True)

    st.title("📊 ENEM 2022 — Nordeste vs Brasil")
    st.caption("Análise comparativa dos microdados do ENEM 2022")

    with st.spinner("Carregando microdados (~3,5 milhões de registros)…"):
        df = load_data()

    st.sidebar.title("Perguntas")
    st.sidebar.caption("Fonte: INEP — Microdados ENEM 2022")
    PERGUNTA_OPTIONS = ["Visão Geral"] + [PERGUNTAS_LABELS[i] for i in range(1, 21)]
    escolha_pergunta = st.sidebar.radio(
        "Selecione uma pergunta para analisar:",
        PERGUNTA_OPTIONS,
        label_visibility="collapsed",
    )

    # Pergunta selecionada na sidebar tem prioridade sobre as tabs
    pergunta_idx = None
    for i in range(1, 21):
        if escolha_pergunta == PERGUNTAS_LABELS[i]:
            pergunta_idx = i
            break

    if pergunta_idx is not None:
        st.markdown(
            f'<div class="pergunta-box">'
            f'<div class="pergunta-num">Pergunta {pergunta_idx}</div>'
            f'{PERGUNTAS[pergunta_idx]}'
            f'</div>',
            unsafe_allow_html=True,
        )
        with st.spinner("Gerando gráfico…"):
            fig, insight = FUNCOES[pergunta_idx](df)
        st.plotly_chart(fig, use_container_width=True)
        st.success(insight)
    else:
        NAV_OPTIONS = ["Contexto", "Dashboard", "Tratamento de Dados"]
        tabs = st.tabs(NAV_OPTIONS)
        with tabs[0]:
            tab_contexto()
        with tabs[1]:
            tab_visao_geral(df)
        with tabs[2]:
            tab_tratamento()


if __name__ == '__main__':
    main()

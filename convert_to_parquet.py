import pandas as pd
import os

COLS = [
    'SG_UF_PROVA',
    'TP_PRESENCA_CN', 'TP_PRESENCA_CH', 'TP_PRESENCA_LC', 'TP_PRESENCA_MT',
    'NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO',
    'TP_STATUS_REDACAO', 'TP_SEXO', 'TP_COR_RACA', 'TP_FAIXA_ETARIA',
    'TP_ESCOLA', 'IN_TREINEIRO', 'TP_LINGUA', 'TP_LOCALIZACAO_ESC',
    'Q002', 'Q006', 'Q025',
]

CATEGORY_COLS = ['SG_UF_PROVA', 'TP_SEXO', 'Q002', 'Q006', 'Q025']

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   'microdados_enem_2022', 'DADOS', 'MICRODADOS_ENEM_2022.csv')
DST = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   'microdados_enem_2022.parquet')

print(f"Lendo {SRC}...")
dtypes = {c: 'category' for c in CATEGORY_COLS}
df = pd.read_csv(SRC, sep=';', encoding='latin-1', usecols=COLS, dtype=dtypes)
print(f"Carregado: {len(df):,} linhas, {len(df.columns)} colunas, memoria: {df.memory_usage(deep=True).sum() / 1024**2:.1f} MB")

for c in ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO']:
    df[c] = pd.to_numeric(df[c], errors='coerce')
for c in ['TP_PRESENCA_CN', 'TP_PRESENCA_CH', 'TP_PRESENCA_LC', 'TP_PRESENCA_MT',
          'TP_STATUS_REDACAO', 'TP_FAIXA_ETARIA', 'TP_ESCOLA', 'IN_TREINEIRO',
          'TP_LINGUA', 'TP_LOCALIZACAO_ESC', 'TP_COR_RACA']:
    df[c] = pd.to_numeric(df[c], errors='coerce')

print(f"Escrevendo {DST}...")
df.to_parquet(DST, compression='snappy', index=False)

size_mb = os.path.getsize(DST) / 1024**2
print(f"Parquet salvo: {size_mb:.1f} MB")

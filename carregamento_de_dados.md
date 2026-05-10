# Carregamento de Dados na EC2 (AWS)

Os microdados do ENEM 2022 tem ~1.5GB em CSV (ou ~36MB apos conversao para Parquet),
tamanho que inviabiliza upload direto para GitHub ou Streamlit Community Cloud.
Este documento descreve como transferir os dados para uma instancia EC2.

## Opcao 1 — SCP Direto (recomendado)

Transfira o arquivo Parquet diretamente para a EC2 via SCP:

```bash
# Suba o arquivo parquet
scp -i /caminho/para/sua-chave.pem \
    microdados_enem_2022.parquet \
    ec2-user@<ip-da-ec2>:/home/ec2-user/app/

# Suba o codigo da aplicacao tambem
scp -i /caminho/para/sua-chave.pem \
    app.py requirements.txt convert_to_parquet.py \
    ec2-user@<ip-da-ec2>:/home/ec2-user/app/
```

> O arquivo Parquet tem ~36MB — a transferencia via SCP leva menos de 1 minuto dependendo
> da sua conexao.

## Opcao 2 — S3 como Intermediario

Util para EC2 sem IP publico fixo ou quando voce precisa transferir os dados uma vez e
reutilizar em varias instancias.

```bash
# 1. LOCAL: Suba o parquet para um bucket S3
aws s3 cp microdados_enem_2022.parquet s3://seu-bucket/enem/

# 2. EC2: Baixe de dentro da instancia
aws s3 cp s3://seu-bucket/enem/microdados_enem_2022.parquet /home/ec2-user/app/
```

A EC2 precisa de uma IAM Role com permissao `s3:GetObject` no bucket, ou credentials
configuradas via `aws configure`.

## Opcao 3 — Download Direto do INEP na EC2

Baixe o ZIP oficial direto do site do INEP e converta na propria EC2.

```bash
# Na EC2:
# 1. Baixar o ZIP (~620MB)
wget -O microdados_enem_2022.zip \
    "https://download.inep.gov.br/microdados/microdados_enem_2022.zip"

# 2. Extrair
unzip microdados_enem_2022.zip -d microdados_enem_2022

# 3. Instalar dependencias e converter para Parquet
uv pip install pandas pyarrow
python convert_to_parquet.py

# 4. Remover arquivos grandes para liberar espaco (opcional)
rm microdados_enem_2022.zip
rm -rf microdados_enem_2022/
```

> O site do INEP esta em https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/enem
> O download direto do ZIP costuma ser mais lento (servidor governamental), entao as
> opcoes 1 e 2 sao preferiveis se voce ja tem o arquivo localmente.

## Executando o App na EC2

Apos transferir os arquivos, na EC2:

```bash
uv pip install -r requirements.txt
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

Certifique-se de que o Security Group da EC2 libera a porta 8501 (TCP) para seu IP ou
para 0.0.0.0/0 (acesso publico).

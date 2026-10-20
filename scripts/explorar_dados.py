
import pandas as pd
from pathlib import Path

# Localizando a pasta principal do projeto
raiz = Path(__file__).resolve().parent.parent

# Caminho do arquivo CSV original
arquivo = raiz / "dados" / "brutos" / "goias_serie_b_2025.csv"

# Lendo o arquivo CSV
df = pd.read_csv(arquivo, encoding="utf-8-sig")

# Exibindo as primeiras cinco linhas
print("\nPRIMEIRAS 5 LINHAS:")
print(df.head().to_string(index=False))

# Identificando as colunas
print("\nCOLUNAS ENCONTRADAS:")
print(df.columns.tolist())

# Quantidade de linhas e colunas
print("\nDIMENSÕES DA BASE:")
print(df.shape)

# Informações sobre os tipos de dados
print("\nTIPOS DE DADOS:")
print(df.dtypes)

# Verificando valores ausentes
print("\nVALORES AUSENTES:")
print(df.isnull().sum())

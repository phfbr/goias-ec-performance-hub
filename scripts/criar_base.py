
import pandas as pd
from pathlib import Path

# Cinco partidas reais do Goiás na Série B de 2025
partidas = [
    ["2025-04-04", "Amazonas", "Casa", 1, 0],
    ["2025-04-12", "Operário-PR", "Fora", 2, 1],
    ["2025-04-17", "Vila Nova", "Casa", 2, 2],
    ["2025-04-20", "América-MG", "Fora", 0, 1],
    ["2025-04-28", "Botafogo-SP", "Fora", 1, 0]
]

colunas = [
    "data", "adversario", "mando",
    "gols_marcados", "gols_sofridos"
]

df = pd.DataFrame(partidas, columns=colunas)

# Adicionando a competição
df["competicao"] = "Brasileirão Série B 2025"

# Calculando os resultados
def calcular_resultado(linha):
    if linha["gols_marcados"] > linha["gols_sofridos"]:
        return "Vitoria"
    elif linha["gols_marcados"] < linha["gols_sofridos"]:
        return "Derrota"
    return "Empate"

df["resultado"] = df.apply(calcular_resultado, axis=1)

# Calculando os pontos
pontos = {"Vitoria": 3, "Empate": 1, "Derrota": 0}
df["pontos"] = df["resultado"].map(pontos)

# Calculando o saldo de gols
df["saldo_gols"] = (
    df["gols_marcados"] - df["gols_sofridos"]
)

# Convertendo as datas
df["data"] = pd.to_datetime(df["data"])

# Localizando a pasta do projeto
raiz = Path(__file__).resolve().parent.parent
destino = raiz / "dados" / "partidas_goias_2025.csv"

# Exportando para CSV
df.to_csv(destino, index=False, encoding="utf-8-sig")

print("Arquivo CSV criado com sucesso!")
print(df.to_string(index=False))
print("\nTotal de pontos:", df["pontos"].sum())
print("Arquivo salvo em:", destino)

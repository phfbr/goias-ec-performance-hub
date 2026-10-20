
import pandas as pd
from pathlib import Path

# 1. Localizar o arquivo original
raiz = Path(__file__).resolve().parent.parent

origem = raiz / "dados" / "brutos" / "goias_serie_b_2025.csv"
destino = raiz / "dados" / "fato_partida_clube.csv"

# 2. Importar os dados
df = pd.read_csv(origem, encoding="utf-8-sig")

# Identificar horários com valores entre parênteses
horarios_diferentes = df[
    df["Time"].astype(str).str.contains(
        r"\(", regex=True, na=False
    )
]

print("\nHORÁRIOS QUE PRECISAM DE VALIDAÇÃO:")
print(
    horarios_diferentes[
        ["Date", "Time", "Opponent"]
    ].to_string(index=False)
)

# 3. Traduzir os nomes das colunas
df = df.rename(columns={
    "Date": "data",
    "Time": "horario",
    "Round": "rodada",
    "Day": "dia_semana",
    "Venue": "mando",
    "Result": "resultado",
    "GF": "gols_marcados",
    "GA": "gols_sofridos",
    "Opponent": "adversario",
    "Poss": "posse_bola",
    "Attendance": "publico",
    "Captain": "capitao",
    "Formation": "formacao",
    "Opp Formation": "formacao_adversario",
    "Referee": "arbitro"
})

# 4. Remover colunas desnecessárias
df = df.drop(columns=["Match Report", "Notes"])

# 5. Converter a data
df["data"] = pd.to_datetime(df["data"])


# Preservar o horário original da fonte
df["horario_original"] = df["horario"]

# Corrigir os dois horários para Brasília
correcoes_horario = {
    "2025-08-02": "20:30",
    "2025-11-07": "21:30"
}

# Aplicar as correções pela data da partida
for data, horario in correcoes_horario.items():
    filtro = df["data"] == pd.Timestamp(data)
    assert filtro.sum() == 1, f"Partida não encontrada: {data}"
    df.loc[filtro, "horario"] = horario

# Garantir que todos os horários tenham formato HH:MM
assert df["horario"].str.fullmatch(
    r"\d{2}:\d{2}"
).all(), "Existem horários fora do padrão!"

print("\nHORÁRIOS CORRIGIDOS:")
print(
    df.loc[
        df["data"].isin(pd.to_datetime(
            list(correcoes_horario.keys())
        )),
        ["data", "adversario", "horario_original", "horario"]
    ].to_string(index=False)
)

# 6. Extrair o número da rodada
df["rodada"] = (
    df["rodada"]
    .str.extract(r"(\d+)")[0]
    .astype(int)
)

# 7. Traduzir os resultados
df["resultado"] = df["resultado"].map({
    "W": "Vitoria",
    "D": "Empate",
    "L": "Derrota"
})

# 8. Traduzir o mando
df["mando"] = df["mando"].map({
    "Home": "Casa",
    "Away": "Fora"
})

# 9. Calcular os pontos
df["pontos"] = df["resultado"].map({
    "Vitoria": 3,
    "Empate": 1,
    "Derrota": 0
})

# 10. Calcular saldo de gols
df["saldo_gols"] = (
    df["gols_marcados"] - df["gols_sofridos"]
)

# 11. Identificar clube e competição
df["clube"] = "Goiás"
df["competicao"] = "Brasileirão Série B"
df["temporada"] = 2025

# 12. Ordenar os dados
df = df.sort_values("rodada").reset_index(drop=True)

# 13. Validar a base
assert len(df) == 38, "Quantidade de partidas incorreta!"
assert df["rodada"].nunique() == 38, "Rodadas duplicadas!"
assert df["resultado"].notna().all(), "Resultado inválido!"
assert df["mando"].notna().all(), "Mando inválido!"

# 14. Exportar o CSV tratado
df.to_csv(destino, index=False, encoding="utf-8-sig")

print("\nBASE TRATADA COM SUCESSO!")
print("Partidas:", len(df))
print("Vitorias:", (df["resultado"] == "Vitoria").sum())
print("Empates:", (df["resultado"] == "Empate").sum())
print("Derrotas:", (df["resultado"] == "Derrota").sum())
print("Gols marcados:", df["gols_marcados"].sum())
print("Gols sofridos:", df["gols_sofridos"].sum())
print("Pontos:", df["pontos"].sum())
print("Saldo de gols:", df["saldo_gols"].sum())
print("\nArquivo salvo em:", destino)

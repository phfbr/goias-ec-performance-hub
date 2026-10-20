
import requests
import pandas as pd
from pathlib import Path

MATCH_ID = 4738803
GOIAS_ID = 9862

url = "https://www.fotmob.com/api/data/matchDetails"

resposta = requests.get(
    url,
    params={"matchId": MATCH_ID},
    timeout=30
)
resposta.raise_for_status()

dados = resposta.json()

shotmap = dados.get("content", {}).get("shotmap") or {}
finalizacoes = shotmap.get("shots", [])

registros = []

for chute in finalizacoes:
    if chute.get("teamId") != GOIAS_ID:
        continue

    registros.append({
        "id_partida": MATCH_ID,
        "id_finalizacao": chute.get("id"),
        "temporada": 2025,
        "competicao": "Série B",
        "jogador": chute.get("playerName"),
        "minuto": chute.get("min"),
        "x": chute.get("x"),
        "y": chute.get("y"),
        "tipo_evento": chute.get("eventType"),
        "tipo_chute": chute.get("shotType"),
        "situacao": chute.get("situation"),
        "xg": chute.get("expectedGoals"),
        "xgot": chute.get("expectedGoalsOnTarget"),
        "no_alvo": chute.get("isOnTarget"),
        "dentro_area": chute.get("isFromInsideBox"),
        "gol": chute.get("eventType") == "Goal"
    })

df = pd.DataFrame(registros)

pasta = Path(__file__).resolve().parent.parent / "dados"
pasta.mkdir(exist_ok=True)

arquivo = pasta / "fato_finalizacoes_teste.csv"

df.to_csv(
    arquivo,
    index=False,
    encoding="utf-8-sig"
)

print("Finalizações do Goiás:", len(df))
print("Gols:", int(df["gol"].sum()) if not df.empty else 0)
print("xG total:", round(df["xg"].sum(), 3) if not df.empty else 0)
print("Arquivo salvo em:", arquivo.resolve())
print(df.head())


print("\n===== VALIDAÇÃO DOS DADOS =====")

print("Total de finalizações:", len(df))
print("Gols:", int(df["gol"].sum()))
print("Finalizações no alvo:", int(df["no_alvo"].sum()))
print("xG total:", round(df["xg"].sum(), 3))

print("\nCoordenadas:")
print("X mínimo:", df["x"].min())
print("X máximo:", df["x"].max())
print("Y mínimo:", df["y"].min())
print("Y máximo:", df["y"].max())

print("\nRegistros duplicados:")
print(df["id_finalizacao"].duplicated().sum())

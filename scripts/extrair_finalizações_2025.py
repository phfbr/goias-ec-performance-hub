
import pandas as pd
import requests
import time
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
GOIAS_ID = 9862

ids = pd.read_csv(
    BASE / "dados" / "ids_partidas_2025.csv",
    encoding="utf-8-sig"
)

sessao = requests.Session()
finalizacoes = []
auditoria = []

for _, partida in ids.iterrows():
    if pd.isna(partida["match_id"]):
        print(f"Rodada {partida['rodada']}: partida sem match_id, ignorada.")
        continue
    match_id = int(partida["match_id"])
    rodada = int(partida["rodada"])

    print(f"Extraindo rodada {rodada} | ID {match_id}")

    try:
        resposta = sessao.get(
            "https://www.fotmob.com/api/data/matchDetails",
            params={"matchId": match_id},
            timeout=30
        )
        resposta.raise_for_status()

        dados = resposta.json()
        shotmap = dados.get("content", {}).get("shotmap", {})
        chutes = shotmap.get("shots", [])

        if not isinstance(chutes, list):
            raise ValueError("Lista de finalizações inválida.")

        quantidade = 0

        for chute in chutes:
            if str(chute.get("teamId")) != str(GOIAS_ID):
                continue

            finalizacoes.append({
                "match_id": match_id,
                "temporada": partida["temporada"],
                "competicao": partida["competicao"],
                "rodada": rodada,
                "adversario": partida["adversario"],
                "mando": partida["mando"],
                "id_finalizacao": chute.get("id"),
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

            quantidade += 1

        auditoria.append({
            "rodada": rodada,
            "match_id": match_id,
            "status": "extraido",
            "finalizacoes": quantidade
        })

    except (requests.RequestException, ValueError, TypeError) as erro:
        print(f"ERRO na rodada {rodada}: {erro}")

        auditoria.append({
            "rodada": rodada,
            "match_id": match_id,
            "status": "erro",
            "finalizacoes": 0
        })

    time.sleep(1)

df_finalizacoes = pd.DataFrame(finalizacoes)
df_auditoria = pd.DataFrame(auditoria)

# Evitar duplicação de eventos
if not df_finalizacoes.empty:
    duplicados = df_finalizacoes["id_finalizacao"].duplicated().sum()

    if duplicados:
        raise ValueError(
            f"Foram encontrados {duplicados} eventos duplicados."
        )

# Salvar os dados e o relatório de auditoria
df_finalizacoes.to_csv(
    BASE / "dados" / "fato_finalizacoes_2025.csv",
    index=False,
    encoding="utf-8-sig"
)

df_auditoria.to_csv(
    BASE / "dados" / "auditoria_finalizacoes_2025.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\n===== RESUMO DA EXTRAÇÃO =====")
print("Partidas consultadas:", len(df_auditoria))
print(
    "Partidas extraídas:",
    (df_auditoria["status"] == "extraido").sum()
)
print(
    "Erros:",
    (df_auditoria["status"] == "erro").sum()
)
print("Total de finalizações:", len(df_finalizacoes))

if not df_finalizacoes.empty:
    print(
        "Total de gols nos eventos:",
        int(df_finalizacoes["gol"].sum())
    )
    print(
        "xG total:",
        round(df_finalizacoes["xg"].sum(), 2)
    )
    print(
        "Eventos sem coordenadas:",
        int(
            df_finalizacoes[["x", "y"]]
            .isna()
            .any(axis=1)
            .sum()
        )
    )

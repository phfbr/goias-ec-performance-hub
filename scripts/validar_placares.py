
import pandas as pd
import requests
import time
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
GOIAS_ID = 9862

partidas = pd.read_csv(
    BASE / "dados" / "fato_partida_clube.csv",
    encoding="utf-8-sig"
)

ids = pd.read_csv(
    BASE / "dados" / "ids_partidas_2025.csv",
    encoding="utf-8-sig"
)

# Relacionar por temporada, competição e rodada
df = partidas.merge(
    ids[["temporada", "competicao", "rodada", "match_id"]],
    on=["temporada", "competicao", "rodada"],
    how="left",
    validate="one_to_one"
)

if df["match_id"].isna().any():
    raise ValueError("Existem partidas sem match_id.")

sessao = requests.Session()
resultados = []

for _, partida in df.iterrows():
    match_id = int(partida["match_id"])

    try:
        resposta = sessao.get(
            "https://www.fotmob.com/api/data/matchDetails",
            params={"matchId": match_id},
            timeout=30
        )
        resposta.raise_for_status()

        dados = resposta.json()
        geral = dados.get("general", {})

        casa = geral.get("homeTeam", {})
        fora = geral.get("awayTeam", {})

        # Conferir IDs das equipes
        if str(casa.get("id")) == str(GOIAS_ID):
            mando_api = "Casa"
        elif str(fora.get("id")) == str(GOIAS_ID):
            mando_api = "Fora"
        else:
            mando_api = "Desconhecido"

        # O placar pode estar em outra seção do JSON
        header = dados.get("header", {})
        status = header.get("status", {})
        score = status.get("scoreStr", "")

        gols_api = None

        if isinstance(score, str) and "-" in score:
            partes = score.split("-")
            try:
                gols_casa = int(partes[0].strip())
                gols_fora = int(partes[1].strip())

                gols_api = (
                    (gols_casa, gols_fora)
                    if mando_api == "Casa"
                    else (gols_fora, gols_casa)
                )
            except ValueError:
                pass

        gols_csv = (
            int(partida["gols_marcados"]),
            int(partida["gols_sofridos"])
        )

        if gols_api is None:
            validacao = "placar_indisponivel"
        elif gols_api == gols_csv:
            validacao = "placar_correto"
        else:
            validacao = "placar_divergente"

        resultados.append({
            "rodada": partida["rodada"],
            "adversario": partida["adversario"],
            "match_id": match_id,
            "placar_csv": str(gols_csv),
            "placar_api": str(gols_api),
            "validacao": validacao
        })

    except (requests.RequestException, ValueError, TypeError) as erro:
        resultados.append({
            "rodada": partida["rodada"],
            "adversario": partida["adversario"],
            "match_id": match_id,
            "placar_csv": "",
            "placar_api": "",
            "validacao": "erro"
        })
        print(f"Rodada {partida['rodada']}: {erro}")

    time.sleep(1)

resultado = pd.DataFrame(resultados)

print("\n===== VALIDAÇÃO DE PLACARES =====")
print(resultado["validacao"].value_counts())

print("\n===== PARTIDAS PARA REVISAR =====")
print(
    resultado[
        resultado["validacao"] != "placar_correto"
    ].to_string(index=False)
)

resultado.to_csv(
    BASE / "dados" / "validacao_placares_2025.csv",
    index=False,
    encoding="utf-8-sig"
)

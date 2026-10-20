
import pandas as pd
import requests
import time
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
GOIAS_ID = 9862

df = pd.read_csv(
    BASE / "dados" / "ids_partidas_2025.csv",
    encoding="utf-8-sig"
)

sessao = requests.Session()
resultados = []

for _, partida in df.iterrows():
    match_id = int(partida["match_id"])

    print(f"Validando rodada {partida['rodada']}...")

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

        id_casa = str(casa.get("id"))
        id_fora = str(fora.get("id"))

        mando_correto = (
            partida["mando"] == "Casa"
            and id_casa == str(GOIAS_ID)
        ) or (
            partida["mando"] == "Fora"
            and id_fora == str(GOIAS_ID)
        )

        status = (
            "validado" if mando_correto
            else "revisar"
        )

        resultados.append({
            "rodada": partida["rodada"],
            "match_id": match_id,
            "mando": partida["mando"],
            "status": status
        })

    except (requests.RequestException, ValueError) as erro:
        resultados.append({
            "rodada": partida["rodada"],
            "match_id": match_id,
            "mando": partida["mando"],
            "status": "erro"
        })
        print("Erro:", erro)

    time.sleep(1)

resultado = pd.DataFrame(resultados)

print("\n===== VALIDAÇÃO =====")
print("Total:", len(resultado))
print("Validados:", (resultado["status"] == "validado").sum())
print("Revisar:", (resultado["status"] == "revisar").sum())
print("Erros:", (resultado["status"] == "erro").sum())

resultado.to_csv(
    BASE / "dados" / "validacao_ids_2025.csv",
    index=False,
    encoding="utf-8-sig"
)

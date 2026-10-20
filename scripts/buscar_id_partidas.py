
import pandas as pd
import requests
import time
import unicodedata
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
GOIAS_ID = 9862

df = pd.read_csv(
    BASE / "dados" / "fato_partida_clube.csv",
    encoding="utf-8-sig"
)

def normalizar(texto):
    texto = str(texto or "").lower().strip()
    return "".join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )

sessao = requests.Session()
resultados = []

for _, partida in df.iterrows():
    data = str(partida["data"]).replace("-", "")
    rodada = partida["rodada"]
    adversario = normalizar(partida["adversario"])
    mando = partida["mando"]

    print(f"Buscando rodada {rodada} - {partida['data']}")

    match_id = None
    status = "nao_encontrado"

    try:
        resposta = sessao.get(
            "https://www.fotmob.com/api/data/matches",
            params={"date": data},
            timeout=30
        )
        resposta.raise_for_status()

        dados = resposta.json()

        for liga in dados.get("leagues", []):
            for jogo in liga.get("matches", []):
                casa = jogo.get("home", {})
                fora = jogo.get("away", {})

                id_casa = str(casa.get("id"))
                id_fora = str(fora.get("id"))

                if str(GOIAS_ID) not in (id_casa, id_fora):
                    continue

                # Validar mando
                if mando == "Casa" and id_casa != str(GOIAS_ID):
                    continue

                if mando == "Fora" and id_fora != str(GOIAS_ID):
                    continue

                outro_time = fora if mando == "Casa" else casa
                nome_adversario = normalizar(
                    outro_time.get("name", "")
                )


                # Validar placar do ponto de vista do Goiás
                gols_goias = int(partida["gols_marcados"])
                gols_adversario = int(partida["gols_sofridos"])

                gols_casa = (
                    gols_goias if mando == "Casa"
                    else gols_adversario
                )

                gols_fora = (
                    gols_adversario if mando == "Casa"
                    else gols_goias
                )

                placar_casa = casa.get("score")
                placar_fora = fora.get("score")

                if placar_casa is None or placar_fora is None:
                    continue

                if (
                    int(placar_casa) != gols_casa
                    or int(placar_fora) != gols_fora
                ):
                    continue

                match_id = jogo.get("id")
                status = "encontrado"
                break

            if match_id:
                break

    except requests.RequestException as erro:
        status = f"erro_http: {erro}"

    resultados.append({
        "data": partida["data"],
        "rodada": rodada,
        "adversario": partida["adversario"],
        "mando": mando,
        "temporada": partida["temporada"],
        "competicao": partida["competicao"],
        "match_id": match_id,
        "status": status
    })

    time.sleep(1)

resultado = pd.DataFrame(resultados)

saida = BASE / "dados" / "ids_partidas_2025.csv"
resultado.to_csv(
    saida,
    index=False,
    encoding="utf-8-sig"
)

print("\n===== RESUMO =====")
print("Total:", len(resultado))
print(
    "Encontradas:",
    (resultado["status"] == "encontrado").sum()
)
print(
    "Não encontradas:",
    (resultado["status"] != "encontrado").sum()
)

print("\nArquivo salvo em:", saida)

print("\n===== PARTIDAS NÃO ENCONTRADAS =====")

pendentes = resultado[
    resultado["status"] != "encontrado"
]

print(
    pendentes[
        [
            "rodada",
            "data",
            "adversario",
            "mando",
            "status"
        ]
    ].to_string(index=False)
)

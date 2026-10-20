
import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent

partidas = pd.read_csv(
    BASE / "dados" / "fato_partida_clube.csv",
    encoding="utf-8-sig"
)

finalizacoes = pd.read_csv(
    BASE / "dados" / "fato_finalizacoes_2025.csv",
    encoding="utf-8-sig"
)

# Contar gols identificados nos eventos
gols_eventos = (
    finalizacoes
    .groupby(["temporada", "competicao", "rodada"])["gol"]
    .sum()
    .reset_index(name="gols_eventos")
)

# Comparar com os gols oficiais da nossa base
comparacao = partidas.merge(
    gols_eventos,
    on=["temporada", "competicao", "rodada"],
    how="left",
    validate="one_to_one"
)

comparacao["gols_eventos"] = (
    comparacao["gols_eventos"]
    .fillna(0)
    .astype(int)
)

divergencias = comparacao[
    comparacao["gols_marcados"]
    != comparacao["gols_eventos"]
]

print("\n===== CONFERÊNCIA DE GOLS =====")
print("Gols na base:", partidas["gols_marcados"].sum())
print("Gols nos eventos:", finalizacoes["gol"].sum())
print("Partidas com divergência:", len(divergencias))

print("\n===== PARTIDAS PARA INVESTIGAR =====")

if divergencias.empty:
    print("Nenhuma divergência encontrada.")
else:
    print(
        divergencias[
            [
                "rodada",
                "data",
                "adversario",
                "gols_marcados",
                "gols_eventos"
            ]
        ].to_string(index=False)
    )

#!/usr/bin/env python3
"""
compute_diff.py - compara duas listas de eventos (Outlook e Google) e produz o
plano de merge: o que criar em cada lado, o que ja esta em sync, e o que ficou
ambiguo.

Entrada: dois arquivos JSON com a mesma estrutura:

    [
      {
        "source": "outlook" | "google",
        "title": "Reuniao 1:1 com Maria",
        "start": "2026-05-20T14:00:00-03:00",
        "end":   "2026-05-20T14:30:00-03:00",
        "location": "",
        "all_day": false,
        "is_synced_copy": false
      },
      ...
    ]

Saida: um JSON com 4 listas (criar_no_google, criar_no_outlook, ja_em_sync,
ambiguos). Vide SKILL.md para regras de matching.

Matching: titulo normalizado + start arredondado ao minuto, tolerancia 5min.
Eventos com is_synced_copy=true permanecem no matching para representar o
estado ja sincronizado (sao alvo de match contra os originais do outro lado).
Originais sem match -> entram em criar_no_X.
Copias sem match -> ambiguo (original do outro lado talvez apagado).
"""

import argparse
import json
import re
import sys
import unicodedata
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path


TOLERANCIA_MINUTOS = 5


def normalizar_titulo(s: str) -> str:
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = "".join(c for c in s if c.isascii())
    s = s.lower()
    # Remove prefixos de cancelamento ANTES de tudo, para matching cruzado
    s = re.sub(r"^\s*cancel(ado|ed|led)\s*:\s*", "", s)
    s = re.sub(r"^[\W_]+|[\W_]+$", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def parse_iso(s: str):
    if not s:
        return None
    s = s.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        try:
            return datetime.fromisoformat(s.split("+")[0].split("Z")[0])
        except Exception:
            return None


def diff_minutos(a, b):
    if a is None or b is None:
        return float("inf")
    if a.tzinfo and not b.tzinfo:
        a = a.replace(tzinfo=None)
    if b.tzinfo and not a.tzinfo:
        b = b.replace(tzinfo=None)
    return abs((a - b).total_seconds() / 60.0)


def titulos_similares(t1, t2):
    if not t1 or not t2:
        return 0.0
    if t1 == t2:
        return 1.0
    return SequenceMatcher(None, t1, t2).ratio()


def match_evento(evento, candidatos):
    titulo_n = normalizar_titulo(evento.get("title", ""))
    start = parse_iso(evento.get("start", ""))

    melhor = None
    melhor_score = 0.0
    melhor_diff_min = float("inf")

    for c in candidatos:
        c_titulo_n = normalizar_titulo(c.get("title", ""))
        c_start = parse_iso(c.get("start", ""))
        sim = titulos_similares(titulo_n, c_titulo_n)
        diff = diff_minutos(start, c_start)
        if sim >= 0.85 and diff <= TOLERANCIA_MINUTOS:
            if sim > melhor_score or (sim == melhor_score and diff < melhor_diff_min):
                melhor = c
                melhor_score = sim
                melhor_diff_min = diff

    if melhor and melhor_score >= 0.85 and melhor_diff_min <= TOLERANCIA_MINUTOS:
        return (melhor, "match")

    for c in candidatos:
        c_titulo_n = normalizar_titulo(c.get("title", ""))
        c_start = parse_iso(c.get("start", ""))
        sim = titulos_similares(titulo_n, c_titulo_n)
        diff = diff_minutos(start, c_start)
        if (0.5 <= sim < 0.85 and diff <= TOLERANCIA_MINUTOS) or (
            sim >= 0.85 and TOLERANCIA_MINUTOS < diff <= 30
        ):
            return (c, "ambiguo")

    return (None, None)


def is_cancelled(ev):
    """Detecta titulos 'Cancelado:', 'Canceled:', 'Cancelled:' (case-insensitive)."""
    t = (ev.get("title") or "").strip().lower()
    return t.startswith(("cancelado:", "canceled:", "cancelled:"))


def computar_diff(eventos_outlook, eventos_google):
    """
    Diff principal — produz 4 listas + 1 nova: deletar_no_google.

    A propagacao de cancelamento: copias da skill (is_synced_copy=true) no Google que
    matchem com eventos AGORA cancelados no Outlook viram candidatos a deletar.
    """
    outlook = eventos_outlook
    google = eventos_google

    criar_no_google = []
    criar_no_outlook = []
    deletar_no_google = []
    ja_em_sync = []
    ambiguos = []

    google_matchados = set()
    outlook_matchados = set()

    for i, ev in enumerate(outlook):
        candidatos = [g for j, g in enumerate(google) if j not in google_matchados]
        match, tipo = match_evento(ev, candidatos)
        if tipo == "match":
            # Caso especial: Outlook agora cancelado e a contraparte no Google e copia da skill
            if is_cancelled(ev) and match.get("is_synced_copy", False):
                deletar_no_google.append({
                    "google": match,
                    "outlook": ev,
                    "motivo": "cancelado no Outlook (era sync nosso)",
                })
            else:
                ja_em_sync.append({"outlook": ev, "google": match})
            for j, g in enumerate(google):
                if g is match:
                    google_matchados.add(j)
                    outlook_matchados.add(i)
                    break
        elif tipo == "ambiguo":
            ambiguos.append({
                "outlook": ev,
                "google": match,
                "motivo": "titulo parecido mas nao identico, ou horario um pouco diferente",
            })
            for j, g in enumerate(google):
                if g is match:
                    google_matchados.add(j)
                    outlook_matchados.add(i)
                    break
        else:
            if not ev.get("is_synced_copy", False):
                # Skip eventos cancelados — nao criar copias deles
                if not is_cancelled(ev):
                    criar_no_google.append(ev)
            else:
                ambiguos.append({
                    "outlook": ev,
                    "google": None,
                    "motivo": "copia da skill sem original correspondente no Google (apagado?)",
                })

    for j, ev in enumerate(google):
        if j in google_matchados:
            continue
        if not ev.get("is_synced_copy", False):
            criar_no_outlook.append(ev)
        else:
            # Copia da skill orfa: original sumiu do Outlook -> deletar
            deletar_no_google.append({
                "google": ev,
                "outlook": None,
                "motivo": "original removido do Outlook",
            })

    return {
        "criar_no_google": criar_no_google,
        "criar_no_outlook": criar_no_outlook,
        "deletar_no_google": deletar_no_google,
        "ja_em_sync": ja_em_sync,
        "ambiguos": ambiguos,
        "_meta": {
            "total_outlook_lidos": len(eventos_outlook),
            "total_google_lidos": len(eventos_google),
            "gerado_em": datetime.now().isoformat(),
        },
    }


def main():
    parser = argparse.ArgumentParser(
        description="Computa o plano de merge entre Outlook e Google Calendar"
    )
    parser.add_argument("--outlook", required=True)
    parser.add_argument("--google", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    try:
        eventos_outlook = json.loads(Path(args.outlook).read_text(encoding="utf-8"))
        eventos_google = json.loads(Path(args.google).read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Erro lendo arquivos de entrada: {e}", file=sys.stderr)
        sys.exit(1)

    plano = computar_diff(eventos_outlook, eventos_google)

    Path(args.output).write_text(
        json.dumps(plano, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print("PLANO DE MERGE")
    print(f"  Criar no Google   : {len(plano['criar_no_google'])}")
    print(f"  Deletar no Google : {len(plano.get('deletar_no_google', []))}")
    print(f"  Criar no Outlook  : {len(plano['criar_no_outlook'])}")
    print(f"  Ja em sync        : {len(plano['ja_em_sync'])}")
    print(f"  Ambiguos          : {len(plano['ambiguos'])}")
    print(f"\nDetalhes salvos em: {args.output}")


if __name__ == "__main__":
    main()
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
# Changelog

## v1.0.0 — 2026-05-19

Primeira release pública.

### `merge-agendas`

- Sincronização **unilateral Outlook → Google** por padrão (mais alinhado ao uso real: o trabalho enche a agenda corporativa e o usuário quer ver os blocos na pessoal). Bidirecional ainda suportado mediante pedido explícito.
- **Propagação de cancelamentos**: eventos que viraram "Cancelado: ..." no Outlook OU que sumiram, e cuja cópia ainda existe no Google (com tag `[merge-agendas]`), são marcados pra deletar.
- Extração via aria-labels no Outlook week view (formato `Título, HH:MM para HH:MM, DiaSemana, NN de Mes de AAAA, Por Organizador, Status, [Evento recorrente]`).
- Extração via `innerText` no Google week view (formato `Nam to Mpm, Title, Owner, location, Month DD, YYYY`).
- Filtro automático de eventos com prefixo `Cancelado:` / `Canceled:` / `Cancelled:`.
- Janela padrão: 6 semanas a partir de hoje.
- Limite de segurança: 50 criações + 10 deleções por direção. Acima disso, para e pede confirmação.
- Output do plano via `scripts/compute_diff.py` (matching por título normalizado + start ±5min, tolerância de pontuação/acento/emoji).
- Geração de `.ics` para upload manual no Google Calendar (handoff de ~10s, devido a restrição da extensão Claude in Chrome em uploads automatizados de arquivos locais).

### `criar-evento-duplo`

- Criação de evento único simultaneamente em Outlook + Google Calendar via deeplinks pré-preenchidos.
- Outlook usa `/calendar/0/deeplink/compose?subject=...&startdt=ISO_LOCAL&enddt=ISO_LOCAL&body=...`
- Google usa `/r/eventedit?text=...&dates=YYYYMMDDTHHMMSSZ/YYYYMMDDTHHMMSSZ&details=...`
- Parseamento de linguagem natural ("amanhã às 14h", "sexta 10h por 30min", etc).
- Opção de criar só em uma das duas via "só na pessoal" / "só no trabalho".

### Infraestrutura

- Repositório no GitHub com versionamento.
- Documentação: README, INSTALL, docs/connectors.md, docs/memory-template.md, docs/lessons-learned.md.

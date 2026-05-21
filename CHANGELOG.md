# Changelog

## v1.1.3 — 2026-05-20

### Lição importante incorporada

- **Não rodar `Start-Process msedge` se o usuário já tem Edge aberto.** Em uma sessão real, isso derrubou a sessão de login do usuário no Google e ele teve que relogar. A skill `merge-agendas` Fase 0.2 agora orienta a PEDIR pro usuário garantir Edge aberto + extensão pareada manualmente, em vez de lançar via processo. Lançamento programático só se o usuário pedir explicitamente "abre o Edge pra mim".
- `docs/lessons-learned.md` ganhou seção dedicada explicando o cenário e a regra.

## v1.1.2 — 2026-05-19

### Verificação de versão

- Adicionado arquivo `VERSION` na raiz com a versão atual (string `1.1.2`).
- Seção "antes de rodar, confira a versão" no README e no INSTALL.md, com snippet bash pra comparar `VERSION` local com a última tag no Git.
- Pré-requisitos das 3 skills agora referenciam essa verificação opcional como "Fase −1" (na `merge-agendas`).
- Cobre o cenário: usuário tem instância antiga numa máquina, foi pra outra, esqueceu de atualizar.

## v1.1.1 — 2026-05-19

### Docs

- Adicionado [`docs/usage.md`](docs/usage.md) — exemplos reais de conversa com cada skill, mostrando o que falar e o que esperar de retorno em cada cenário (merge, criar, apagar).
- Adicionado [`docs/triggers.md`](docs/triggers.md) — cheat sheet com todas as frases naturais que disparam cada skill.
- README e INSTALL.md atualizados com links pros novos docs.

Sem mudança de código. Patch só pra facilitar onboarding de novo computador.

## v1.1.0 — 2026-05-19

### Nova skill: `deletar-evento-duplo`

- Apaga um evento específico em Outlook, Google ou ambos.
- Identifica via título + data/hora; em caso de ambiguidade, pergunta.
- **Click via JS no `aria-label`** ao invés de coordenada — descoberto que coords falham com frequência (popups movem, layouts variam). JS click no `aria-label="Delete event"` (Google) ou `aria-label="Excluir"` (Outlook) é determinístico.
- Trata dialog de confirmação do Outlook automaticamente.
- Detecta evento com participantes e cancela sem notificar (não dispara email involuntário aos colegas).
- Limite de segurança: 1 evento por chamada direta; 10 por run em batch (vindo do `merge-agendas`).

### `merge-agendas` atualizado

- Fase de propagação de cancelamentos agora **delega pra `deletar-evento-duplo`** em vez de implementar a UI inline. Lógica de deleção fica centralizada.

### Docs

- README com bloco "como usar em outro computador (TL;DR)" visível no topo.

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

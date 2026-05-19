# Changelog

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
- Limite de segurança: 50 criações + 10 deleções por direção. Acima disso, para e p
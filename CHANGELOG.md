# Changelog

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
- Extração via 
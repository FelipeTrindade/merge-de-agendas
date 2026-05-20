# Changelog

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

## v1.0.0 — 2026-
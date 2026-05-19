# Merge de Agendas

Duas skills do Claude (Cowork / Claude Code) para integrar a agenda corporativa do Outlook Web com a agenda pessoal do Google Calendar, sem precisar de serviço pago de sincronização (OneCal, CalendarBridge, etc).

Funciona **diretamente no navegador Edge** via a extensão **Claude in Chrome** — não usa OAuth nem APIs corporativas, então não depende de aprovação do TI da empresa.

## As duas skills

### 1. `merge-agendas` — sincronização semanal em lote

Comando do usuário: **"Faça o merge das agendas"**

- Lê os compromissos das próximas 6 semanas no Outlook corporativo e Google Calendar pessoal
- Identifica eventos do Outlook que ainda não estão no Google
- **Propaga cancelamentos**: se um evento sincronizado no Google foi cancelado no Outlook (título virou `Cancelado:`) ou removido, marca pra deletar do Google
- Mostra preview completo no chat antes de criar ou deletar qualquer coisa
- Gera arquivo `.ics` com os eventos a criar para upload no Google Calendar (handoff manual de ~10s)
- **Idempotente**: cada cópia leva tag `[merge-agendas | source=outlook]` na descrição, runs seguintes não duplicam

Direção padrão: **unilateral Outlook → Google**. Bidirecional só se você pedir explicitamente.

### 2. `criar-evento-duplo` — criação avulsa em tempo real

Comandos do usuário: **"Cria evento X amanhã às 14h"**, **"Marca reunião com cliente sexta 10h"**, etc.

- Parseia o pedido em linguagem natural (título, data relativa, horário)
- Abre dois deeplinks pré-preenchidos: um no Google Calendar (`/r/eventedit`), outro no Outlook (`/calendar/0/deeplink/compose`)
- Clica Save em cada
- Verifica que ambos foram criados
- Tempo total: ~15-20s

Pode ser unilateral também ("só na pessoal", "só no trabalho").

## Instalação

Ver [`INSTALL.md`](INSTALL.md) para passo a passo. Resumo:

1. Cowork ou Claude Code instalado
2. Instalar dois plugins/conectores: **Claude in Chrome** + **Desktop Commander**
3. Instalar os dois `.skill` de `dist/`
4. Setup inicial: as duas contas (corporativa Outlook + pessoal Gmail) logadas no Edge
5. Memória inicial: copiar `docs/memory-template.md` pra sua memória de usuário do Claude

## Documentação

- [`INSTALL.md`](INSTALL.md) — instruções de instalação em uma máquina nova
- [`CHANGELOG.md`](CHANGELOG.md) — histórico de versões
- [`docs/connectors.md`](docs/connectors.md) — quais MCPs/plugins o Claude precisa
- [`docs/memory-template.md`](docs/memory-template.md) — memória de contexto pro Claude entender o setup
- [`docs/lessons-learned.md`](docs/lessons-learned.md) — descobertas sobre automação de Outlook/Google que valem a pena pré-saber
- `skill-source/` — código-fonte editável das duas skills
- `dist/` — pacotes `.skill` prontos pra instalar

## Versão

v1.0.0 — primeira release com merge unilateral e propagação de cancelamentos.

## Licença

Uso pessoal. Sem afiliação com Microsoft, Google, Anthropic.

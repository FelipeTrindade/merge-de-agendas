# Merge de Agendas

Três skills do Claude (Cowork / Claude Code) para integrar a agenda corporativa do Outlook Web com a agenda pessoal do Google Calendar, sem precisar de serviço pago de sincronização (OneCal, CalendarBridge, etc).

Funciona **diretamente no navegador Edge** via a extensão **Claude in Chrome** — não usa OAuth nem APIs corporativas, então não depende de aprovação do TI da empresa.

## Como usar em outro computador (TL;DR)

```bash
git clone https://github.com/FelipeTrindade/merge-de-agendas.git
cd merge-de-agendas
# Siga o INSTALL.md:
#   1. Instala Cowork ou Claude Code
#   2. Instala MCPs: Claude in Chrome + Desktop Commander
#   3. Instala os 3 .skill de dist/
#   4. Loga as 2 contas no Edge
#   5. Copia docs/memory-template.md pra memória do seu usuário do Claude
```

Detalhes completos em [`INSTALL.md`](INSTALL.md). Exemplos práticos de conversa em [`docs/usage.md`](docs/usage.md).

## As três skills

### 1. `merge-agendas` — sincronização semanal em lote

Comando: **"Faça o merge das agendas"**

- Lê os compromissos das próximas 6 semanas no Outlook corporativo e Google Calendar pessoal
- Identifica eventos do Outlook que ainda não estão no Google
- **Propaga cancelamentos**: se um evento sincronizado no Google foi cancelado no Outlook (título virou `Cancelado:`) ou removido, marca pra deletar do Google (delegando pra skill `deletar-evento-duplo`)
- Mostra preview completo no chat antes de criar ou deletar qualquer coisa
- Gera `.ics` com os eventos a criar para upload no Google Calendar (handoff manual de ~10s, devido a restrição de upload da extensão Claude in Chrome)
- **Idempotente**: cada cópia leva tag `[merge-agendas | source=outlook]` na descrição, runs seguintes não duplicam

Direção padrão: **unilateral Outlook → Google**. Bidirecional só sob pedido explícito.

### 2. `criar-evento-duplo` — criação avulsa em tempo real

Comandos: **"Cria evento X amanhã às 14h"**, **"Marca reunião com cliente sexta 10h"**, etc.

- Parseia o pedido em linguagem natural (título, data relativa, horário)
- Abre dois deeplinks pré-preenchidos: Google (`/r/eventedit`) e Outlook (`/calendar/0/deeplink/compose`)
- Clica Save em cada
- Verifica que ambos foram criados
- Tempo total: ~15-20s

Pode ser unilateral também ("só na pessoal", "só no trabalho").

### 3. `deletar-evento-duplo` — remoção de evento (novo em v1.1.0)

Comandos: **"Apaga evento X"**, **"Cancela aquela reunião de hoje"**, **"Tira do calendário"**

- Identifica o evento por título + data/hora
- Click via JS no aria-label (mais confiável que click por coordenada — descoberto na prática)
- Trata o dialog de confirmação do Outlook automaticamente
- Não notifica participantes em cancelamentos a não ser que pedido
- **Invocada internamente pela `merge-agendas`** quando precisa deletar cópias órfãs/canceladas

## Documentação

- [`INSTALL.md`](INSTALL.md) — instruções de instalação em uma máquina nova
- [`CHANGELOG.md`](CHANGELOG.md) — histórico de versões
- [`docs/usage.md`](docs/usage.md) — **exemplos reais de conversa** com cada skill (recomendado pra começar)
- [`docs/triggers.md`](docs/triggers.md) — cheat sheet de frases que disparam cada skill
- [`docs/connectors.md`](docs/connectors.md) — quais MCPs/plugins o Claude precisa
- [`docs/memory-template.md`](docs/memory-template.md) — memória de contexto pro Claude entender o setup
- [`docs/lessons-learned.md`](docs/lessons-learned.md) — descobertas sobre automação de Outlook/Google que valem a pena pré-saber
- `skill-source/` — código-fonte editável das três skills
- `dist/` — pacotes `.skill` prontos pra instalar

## Versão atual

**v1.1.1** — docs/usage.md e docs/triggers.md adicionados pra facilitar onboarding em máquina nova. Ver [CHANGELOG.md](CHANGELOG.md) para histórico.

## Licença

Uso pessoal. Sem afiliação com Microsoft, Google, Anthropic.

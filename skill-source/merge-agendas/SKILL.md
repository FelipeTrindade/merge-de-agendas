---
name: merge-agendas
description: >
  Merge bidirecional entre a agenda corporativa (Outlook Web) e a pessoal (Google Calendar),
  via Edge com Claude in Chrome. Lê as próximas 6 semanas dos dois lados, mostra um preview
  pro Felipe aprovar, e cria os eventos faltantes com uma tag `[merge-agendas|source=...]` na
  descrição pra evitar duplicação em runs seguintes. Idempotente — pode rodar toda semana.
  Não copia participantes (evita convites involuntários) nem links de Teams/Meet.
  USE ESTA SKILL SEMPRE que o usuário disser "faça o merge das agendas", "merge das agendas",
  "sincroniza/junta/mescla as agendas", "sincroniza Outlook com Gmail", "atualiza o merge",
  "rodar o merge", ou pedir pra "puxar compromissos do trabalho pra agenda pessoal" / vice-versa.
---

# Merge de Agendas — Outlook Corporativo ↔ Google Calendar Pessoal

## O que esta skill faz

Sincroniza as duas agendas do Felipe em uma única operação manual semanal:

- **Lê** os compromissos das próximas 6 semanas no Outlook Web e no Google Calendar (via Edge,
  com Claude in Chrome — as duas contas já estão logadas)
- **Calcula** quais eventos existem em uma agenda mas não na outra
- **Mostra um preview** completo antes de criar qualquer coisa, e espera confirmação
- **Cria** os eventos faltantes em cada direção, marcados com uma tag de sincronização que
  permite rodar a skill de novo sem duplicar nada

Não é um sync contínuo automático — é um merge único manual, rodado quando o Felipe escrever
"Faça o merge das agendas". A ideia é que rode uma vez por semana.

---

## Fase 0 — Garantir Edge aberto e Claude in Chrome conectado

Esta fase roda automaticamente no início. Não pedir confirmação aqui — só agir.

### 0.1 — Listar browsers conectados

Chamar `mcp__Claude_in_Chrome__list_connected_browsers`.

- **Se retornar 1+ browser**: ótimo, pular pra 0.3
- **Se retornar vazio**: ir pra 0.2

### 0.2 — Abrir o Edge se não estiver conectado

Tentar nesta ordem, parando assim que `list_connected_browsers` voltar a retornar algo:

1. **Desktop Commander start_process**:
   ```
   mcp__Desktop_Commander__start_process command:
     "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
   ```
   Caminho alternativo: `C:\Program Files\Microsoft\Edge\Application\msedge.exe`

2. **Bash via cmd.exe** (se Desktop Commander não estiver disponível):
   ```bash
   cmd.exe /c start msedge
   ```

3. **Pedir ao Felipe** (último recurso): "Não consegui abrir o Edge automaticamente. Abra
   manualmente e me peça o merge de novo."

Após disparar o open, aguardar 5 segundos e chamar `list_connected_browsers` de novo. Se ainda
vazio, repetir até 3 vezes com intervalo de 5s. Se em 15s não conectar, parar e avisar:
> "Abri o Edge mas o Claude in Chrome não detectou. A extensão pode estar desativada. Ative
> a extensão Claude no Edge e me peça o merge de novo."

### 0.3 — Selecionar o browser certo

Se `list_connected_browsers` retornou múltiplos:

1. Priorizar o que tiver "Edge" no nome
2. Em empate, priorizar o marcado como local (mesmo computador)
3. Em ambiguidade, perguntar ao Felipe

Chamar `mcp__Claude_in_Chrome__select_browser` com o `deviceId` escolhido.

### 0.4 — Garantir as duas abas abertas

Verificar abas abertas com `mcp__Claude_in_Chrome__read_page` (lista todas).

Para cada uma das duas URLs alvo, se nenhuma aba estiver naquele domínio, abrir:

```
mcp__Claude_in_Chrome__tabs_create_mcp url: "https://outlook.office.com/calendar/view/workweek"
mcp__Claude_in_Chrome__tabs_create_mcp url: "https://calendar.google.com/calendar/u/0/r/agenda"
```

Se já existir aba no domínio mas em URL diferente, usar `navigate` pra ajustar.

### 0.5 — Verificar login das duas contas

Em cada aba, chamar `get_page_text` e procurar por sinais de login (campos "Email" / "Senha" /
"Sign in"). Se detectar:

> "A conta [Outlook/Google] precisa de login. Faça login no Edge primeiro e me peça o merge
> de novo."

---

## Pré-requisitos contextuais (verificações que aplicam ao Felipe)

- **As duas contas já estão logadas no Edge.** Foi confirmado pelo Felipe na criação da skill.
  Se um dia migrar pra outro navegador, ajustar os caminhos.

---

## Configuração (constantes — não pedir pro usuário toda run)

```python
# Janela de tempo: hoje até hoje + N dias
JANELA_DIAS = 42  # 6 semanas

# Tag que marca eventos criados pela skill — usada pra detectar duplicatas
TAG_BASE = "[merge-agendas"   # qualquer evento com isso no description é cópia nossa

# Limite de segurança: se for criar mais que isso em uma direção, parar e perguntar
LIMITE_CRIACOES_POR_DIRECAO = 50

# Pasta onde a skill pode salvar relatórios e state file
PASTA_TRABALHO = r"C:\Users\FELIPE\Documents\Claude\Projects\Merge de agendas"
```

---

## Fluxo principal

São 6 fases. Avise o Felipe ao iniciar cada uma — esse merge demora ~3-8 minutos dependendo do
volume, e ele precisa saber que está rodando.

**Direção padrão**: unilateral Outlook → Google. Fases 2 e 5 só rodam pra esse sentido.
A Fase 4.5 (propagação de cancelamentos) checa eventos sincronizados no Google que ficaram
órfãos porque o original foi cancelado no Outlook — e os remove.

### Fase 1 — Extrair eventos do Outlook corporativo

#### 1.1 — Navegar pra agenda

Usar `mcp__Claude_in_Chrome__navigate` para abrir:
```
https://outlook.office.com/calendar/view/workweek
```

Se a página carregar mostrando tela de login do Microsoft, parar e avisar:
> "A agenda corporativa precisa de login. Faça login no Edge primeiro e me peça o merge de novo."

#### 1.2 — Mudar para a visão de Agenda/Lista

A view padrão do Outlook é grade semanal — ruim pra scraping. Mudar pra **list view** ajuda.
Tentar nesta ordem (a UI da Microsoft muda com frequência):

1. **Atalho de teclado**: usar `shortcuts_execute` com a sequência de teclas pra "Agenda view"
   (geralmente `Ctrl+Alt+5` na agenda do Outlook Web).
2. Se não funcionar, clicar manualmente no seletor de view (canto superior direito, perto do
   nome "Trabalho", "Dia", "Semana", "Mês"). Usar `find` pra localizar o botão de view.
3. Se mesmo assim não conseguir, manter a view padrão — `get_page_text` ainda pega os eventos
   visíveis.

#### 1.3 — Iterar semana a semana e extrair

Pra cobrir 6 semanas, navegar semana a semana usando o botão "próxima" (geralmente `→` no
teclado ou um chevron na UI):

```
Para cada uma das 6 semanas:
    1. Aguardar a página carregar (1-2s)
    2. Chamar `mcp__Claude_in_Chrome__get_page_text` na aba do Outlook
    3. Extrair eventos do texto retornado
    4. Avançar pra próxima semana (Ctrl+→ ou clicar no chevron de "próxima semana")
```

Ao final, voltar pra semana atual (importante pra não deixar a tela do Felipe deslocada).

#### 1.4 — Parsear os eventos do texto via aria-label (MELHOR jeito)

**Não use `get_page_text` no Outlook** — perde a relação data↔evento. Use JS via
`javascript_tool` pra ler os `aria-label` dos tiles de evento. Formato confiável (PT-BR):

```
"<TITULO>, HH:MM para HH:MM, <DiaSemana>, NN de <Mes> de AAAA, Por <Organizador>, <Status>, [Evento recorrente]"
```

Exemplo real:
> "Cancelado: Verificar Pesquisas de NPS, 17:00 para 17:00, Domingo, 17 de Mai de 2026, Por Thiago Picanco, Free, Evento recorrente"

Regex que funciona:
```js
const m = lbl.match(/^(.+?),\s*(\d{1,2}):(\d{2})\s+para\s+(\d{1,2}):(\d{2}),\s*[^,]+,\s*(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4}),(.*)$/i);
```

**Importante**: a view de **semana** usa nome do mês abreviado ("Mai", "Jun"), a view de
**mês** usa nome completo ("Maio", "Junho"). O mapa de meses precisa cobrir as duas formas:

```js
const meses = {janeiro:1,jan:1, fevereiro:2,fev:2, 'março':3,marco:3,mar:3,
  abril:4,abr:4, maio:5,mai:5, junho:6,jun:6, julho:7,jul:7, agosto:8,ago:8,
  setembro:9,set:9, outubro:10,out:10, novembro:11,nov:11, dezembro:12,dez:12};
```

**Use Week view, NÃO Month view** — o month view esconde eventos atrás de "+5", "+8" badges
e perde dados. Week view mostra todos. Iterar semana a semana clicando no botão
`aria-label="Ir para a semana seguinte ..."` (sleep 2s entre cliques pra UI carregar).

---

#### 1.4-LEGADO — Parsear via get_page_text (não recomendado)

O `get_page_text` retorna o texto da página inteira. Os eventos aparecem como blocos curtos com
horário e título. Use heurísticas:

- Linhas com padrão `HH:MM` ou `HH:MM - HH:MM` são fortes candidatos a horário
- A linha logo antes ou no mesmo bloco é o título
- Data: pegar do cabeçalho da página ou da seção atual

**Quando em dúvida, prefira ser conservador**: se não está claro se é um evento, NÃO incluir.
Melhor faltar um evento (Felipe percebe e cria manual) do que criar lixo na agenda pessoal.

Salvar como JSON estruturado:

```json
[
  {
    "source": "outlook",
    "title": "Reunião 1:1 com Maria",
    "start": "2026-05-20T14:00:00-03:00",
    "end": "2026-05-20T14:30:00-03:00",
    "location": "",
    "is_synced_copy": false
  }
]
```

#### 1.5 — Filtrar cópias e cancelados

Descartar (não incluir no JSON):

1. **Eventos cancelados** — título que começa com `Cancelado:`, `Canceled:`, `Cancelled:`
   (case-insensitive, com ou sem espaço após o `:`). Em python:
   ```python
   import re
   if re.match(r"^\s*cancel(ado|ed|led)\s*:", titulo, re.IGNORECASE):
       continue  # pula
   ```
2. **Cópias prévias da skill** — descrição contém `[merge-agendas`. Como `get_page_text` nem
   sempre mostra a descrição completa, também marcar como suspeito qualquer evento com título
   idêntico a um evento da outra agenda no mesmo horário (validação cruzada vem na Fase 3).

Salvar a lista filtrada em `[PASTA_TRABALHO]\eventos_outlook.json`.

---

### Fase 2 — Extrair eventos do Google Calendar pessoal

#### 2.1 — Navegar pra agenda

Abrir em nova aba (não fechar a aba do Outlook, vai ser usada na Fase 5):

```
https://calendar.google.com/calendar/u/0/r/agenda
```

A URL `/r/agenda` força a "visão de agenda" (lista cronológica) — exatamente o que queremos
para parsing.

Se aparecer tela de login do Google, parar e avisar — mesmo tratamento da 1.1.

#### 2.2 — Garantir a janela correta

A visão de agenda do Google mostra ~30 dias por padrão. Para cobrir 42 dias, rolar a página
até alcançar a data alvo (`hoje + 42 dias`):

```
data_alvo = hoje + timedelta(days=42)
Enquanto a última data visível no texto < data_alvo:
    rolar a página (PgDn ou scroll para baixo)
    aguardar 0.5s
    re-extrair texto
```

#### 2.3 — Extrair e parsear (Google Calendar)

**Google é diferente do Outlook**: os tiles têm `data-eventid` mas o `aria-label` deles
costuma vir vazio. O texto está no `innerText` do tile.

Formato de cada tile (em inglês mesmo quando UI tá em pt-BR):
```
"8am to 8:45pm, Presencial Suam Aniversário Janu , Felipe Trindade, No location, May 21, 2026
Presencial Suam Aniversário Janu
8am – 8:45pm"
```

Regex:
```js
const m = text.match(/^(\d{1,2})(?::(\d{2}))?(am|pm)\s+to\s+(\d{1,2})(?::(\d{2}))?(am|pm),\s*(.+?)\s*,\s*[^,]+,\s*[^,]+,\s*(\w+)\s+(\d{1,2}),\s*(\d{4})/i);
```

Iterar semanas clicando botão `aria-label="Next week"` (em inglês). A URL muda pra
`/r/week/AAAA/M/DD` o que confirma a navegação.

---

#### 2.3-LEGADO — Extrair via get_page_text

Similar à 1.4. A view de agenda do Google é mais limpa que a do Outlook:

```
quinta-feira, 21 de maio
  09:00 - 10:00   Treino na academia
  14:30 - 15:30   Almoço com Pai
sexta-feira, 22 de maio
  ...
```

Cada linha de evento é parseável com regex tipo:
```
^\s*(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})\s+(.+)$
```

Eventos de dia inteiro aparecem sem horário, geralmente com um marcador "Dia inteiro" — incluir
no JSON com `"all_day": true`.

#### 2.4 — Filtrar cópias, cancelados e salvar

Mesma filtragem da 1.5 (descartar cancelados e cópias prévias da skill).
Salvar em `[PASTA_TRABALHO]\eventos_google.json`.

---

### Fase 3 — Computar o diff

Usar o script bundled em `scripts/compute_diff.py`:

```bash
python "[caminho-da-skill]/scripts/compute_diff.py" \
  --outlook "[PASTA_TRABALHO]/eventos_outlook.json" \
  --google  "[PASTA_TRABALHO]/eventos_google.json" \
  --output  "[PASTA_TRABALHO]/plano_merge.json"
```

O script aplica esta regra de matching:

- **Chave de comparação**: `(título_normalizado, data_inicio_arredondada_pro_minuto_mais_proximo)`
- **Normalização do título**: lowercase, sem acentos, sem espaços duplos, sem emojis
- **Tolerância de horário**: se diferença < 5 minutos, considera o mesmo evento

Categorias do output:

```json
{
  "criar_no_google": [...],    // estão no Outlook, faltam no Google
  "criar_no_outlook": [...],   // estão no Google, faltam no Outlook
  "ja_em_sync": [...],         // matchados — nada a fazer
  "ambiguos": [...]            // dois eventos parecidos mas não certos — pedir review
}
```

---

### Fase 4.5 — Detectar cancelamentos a propagar (NOVO em v1.0.0)

Antes do preview, fazer mais um passo: identificar cópias órfãs no Google que devem ser
deletadas porque o evento original no Outlook foi cancelado ou removido.

#### Lógica

Para cada evento no Google que tem a tag `[merge-agendas` na descrição (= foi criado por
nós em algum run anterior):

1. Extrair o título "limpo" (sem a tag) e o horário.
2. Procurar nos eventos brutos do Outlook (incluindo CANCELADOS — não filtrar nessa hora):
   - Match exato: mesmo título normalizado + start dentro de ±5min → ainda existe, MAS:
     - Se o título do Outlook AGORA começa com `Cancelado:`, `Canceled:` ou `Cancelled:`
       → o evento foi cancelado depois do sync inicial → **marcar pra deletar no Google**
     - Se não tem prefixo de cancelado → tudo ok, manter
   - Nenhum match em nenhum lugar → o evento foi removido por completo do Outlook →
     **marcar pra deletar no Google**

#### Por que checar contra eventos cancelados (não filtrados)

O filtro de cancelados acontece na Fase 1.5/2.4. Pra essa lógica funcionar, precisamos do
estado bruto antes do filtro. Salvar separadamente:

```python
eventos_outlook_brutos = [...]  # tudo, sem filtrar
eventos_outlook = [e for e in eventos_outlook_brutos if not is_cancelled(e)]
```

#### Output dessa fase

Adicionar nova categoria ao plano:

```json
{
  "deletar_no_google": [
    {
      "google_event_id": "...",
      "title": "Reunião XYZ",
      "start": "2026-05-22T14:00:00-03:00",
      "motivo": "cancelado no Outlook"  // ou "removido do Outlook"
    },
    ...
  ]
}
```

#### Como deletar — delegar pra skill `deletar-evento-duplo`

A skill `deletar-evento-duplo` tem toda a lógica testada de click via JS (mais confiável que
coord), tratamento do dialog do Outlook, etc. Em vez de duplicar essa lógica aqui, **invocar**
ela passando a lista de eventos a deletar (com `agenda: "google"` em cada um — esta skill
nunca deleta no Outlook automaticamente, é unilateral por padrão).

Resumo do que aquela skill faz pra Google:
1. Click no tile → mini popup
2. JS click no `aria-label="Delete event"` (em inglês mesmo) → deleta direto, sem confirmação
3. Verifica que o tile sumiu

**Limite de segurança herdado**: 10 deleções por run. Se exceder, parar e mostrar lista pro
Felipe confirmar antes de prosseguir. Deletar de massa por acidente é o pior cenário que
essa skill pode causar.

---

### Fase 4 — Preview e confirmação (OBRIGATÓRIO)

Antes de criar qualquer coisa, mostrar no chat uma tabela como esta:

```
PLANO DE MERGE — semana de 19/05/2026
==========================================================

Vou CRIAR 7 eventos no Google (vindos do Outlook):
  • 20/05 14:00  Reunião 1:1 com Maria
  • 21/05 09:30  Sprint planning
  • 22/05 11:00  Café com cliente XPTO
  ...

Vou DELETAR 2 eventos no Google (cancelados no Outlook):
  • 20/05 10:00  Daily Standup — cancelado no Outlook
  • 23/05 15:00  Reunião com Banco — removido do Outlook

Já em sync (nada a fazer): 12 eventos
Casos ambíguos para revisar manualmente: 2
  ? "Daily" às 09:00 no Outlook vs "Stand-up" às 09:00 no Google — mesmo evento?

==========================================================
TOTAL: 7 criações + 2 deleções. Confirma que posso prosseguir? (sim/não)
```

**Hardstops antes de pedir confirmação:**

- Se `criar_no_google` > LIMITE_CRIACOES_POR_DIRECAO (50) → parar e perguntar:
  "Caí em 73 criações no Google. Suspeito de problema na extração. Quer que eu mostre os
  primeiros 10 pra você sanity-
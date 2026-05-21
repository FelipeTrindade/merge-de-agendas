# Lições aprendidas

Descobertas técnicas durante a construção dessas skills. Salvar isso aqui evita o Claude de queimar tokens redescobrindo o que já sabemos.

## Identidade dos navegadores

A extensão **Claude in Chrome** se identifica como `name: "Chrome"` no `list_connected_browsers` quando roda em qualquer Chromium. No Edge, ela aparece como **`name: "Edge"`** (descobrimos só depois de testar).

Sempre listar todos os navegadores conectados e usar `name` pra distinguir — não confiar em assumptions.

## NÃO lançar Edge via Start-Process se o usuário já tem Edge aberto

Em uma sessão (2026-05-20), rodar `Start-Process msedge` quando o usuário tinha Edge aberto pelo taskbar **derrubou a sessão de login dele no Google**. A janela nova abriu sem cookies, e algo no processo de inicialização também afetou a janela existente — o usuário precisou relogar manualmente.

**Regra**: se `list_connected_browsers` vier vazio, pedir pro usuário garantir manualmente que:
1. O Edge dele está aberto
2. A extensão Claude in Chrome está habilitada
3. A extensão está pareada (clicou no ícone e aprovou)

Só lançar via processo se o usuário pedir explicitamente "abre o Edge pra mim".

## Outlook Web — extração de eventos

### Use Week view, NÃO Month view

O Month view do Outlook esconde eventos atrás de "+5", "+8" badges quando o dia tem muitos compromissos. Perde dados.

Week view (`outlook.office.com/calendar/view/week`) mostra todos os eventos.

### Aria-labels têm tudo

Os tiles de evento têm aria-labels riquíssimos no formato (PT-BR):

```
"<TITULO>, HH:MM para HH:MM, <DiaSemana>, NN de <Mes> de AAAA, Por <Organizador>, <Status>, [Evento recorrente]"
```

Exemplo:
```
"Cancelado: Verificar Pesquisas de NPS, 17:00 para 17:00, Domingo, 17 de Mai de 2026, Por Thiago Picanco, Free, Evento recorrente"
```

Regex que captura tudo:
```js
/^(.+?),\s*(\d{1,2}):(\d{2})\s+para\s+(\d{1,2}):(\d{2}),\s*[^,]+,\s*(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4}),(.*)$/i
```

### Meses abreviados (Mai, Jun) ≠ Meses completos (Maio, Junho)

A **week view** abrevia: "Mai", "Jun", "Jul".
A **month view** usa nome completo: "Maio", "Junho".

O mapa de meses precisa cobrir as duas formas:

```js
const meses = {
  janeiro:1,jan:1, fevereiro:2,fev:2, 'março':3,marco:3,mar:3,
  abril:4,abr:4, maio:5,mai:5, junho:6,jun:6, julho:7,jul:7,
  agosto:8,ago:8, setembro:9,set:9, outubro:10,out:10,
  novembro:11,nov:11, dezembro:12,dez:12
};
```

### Navegação entre semanas

O botão "Ir para a semana seguinte" tem aria-label distintivo: `aria-label*="Ir para a semana seguinte"`. Selecionar e clicar via JS. Esperar 2s entre cliques (UI carregar).

### Deeplink de criação de evento

URL pattern testado e funcional:

```
https://outlook.office.com/calendar/0/deeplink/compose
  ?path=/calendar/action/compose
  &rru=addevent
  &subject=<urlencoded>
  &startdt=<ISO_LOCAL_SEM_TZ>     # ex: 2026-05-19T21:00:00
  &enddt=<ISO_LOCAL_SEM_TZ>
  &body=<urlencoded>
  &location=<urlencoded>
```

**ISO sem timezone** — Outlook interpreta no TZ do navegador. Tentar com `Z` (UTC) NÃO funciona corretamente.

Depois de navegar, aguardar **≥5 segundos** pro form carregar, depois clicar "Salvar" (~coord 68, 75 numa janela 1258×952).

## Google Calendar — extração de eventos

### Aria-labels nos tiles vêm vazios

`data-eventid` existe e é estável, mas `aria-label` no tile costuma ser string vazia. Em vez disso, ler `innerText` do tile:

```
"8am to 8:45pm, Title , Owner, location, Month DD, YYYY
Title
8am – 8:45pm"
```

Regex:
```js
/^(\d{1,2})(?::(\d{2}))?(am|pm)\s+to\s+(\d{1,2})(?::(\d{2}))?(am|pm),\s*(.+?)\s*,\s*[^,]+,\s*[^,]+,\s*(\w+)\s+(\d{1,2}),\s*(\d{4})/i
```

Note: meses em INGLÊS mesmo quando UI está em pt-BR.

### Navegação

Botão "Next week" (em inglês mesmo na UI pt-BR). URL atualiza pra `/r/week/AAAA/M/DD`.

### Deeplink de criação de evento

URL pattern testado e funcional:

```
https://calendar.google.com/calendar/u/0/r/eventedit
  ?text=<urlencoded>
  &dates=<INICIO_UTC_Z>/<FIM_UTC_Z>     # ex: 20260520T000000Z/20260520T010000Z
  &details=<urlencoded>
  &location=<urlencoded>
```

**UTC com Z** — diferente do Outlook. Conversão:
```js
function toGcalUTC(localISO) {
  const d = new Date(localISO);
  const pad = (n) => String(n).padStart(2, '0');
  return `${d.getUTCFullYear()}${pad(d.getUTCMonth()+1)}${pad(d.getUTCDate())}T${pad(d.getUTCHours())}${pad(d.getUTCMinutes())}00Z`;
}
```

Depois de navegar, **2-3 segundos** já é suficiente, depois clicar "Save" (~coord 737, 40).

### Settings/Import URL não é deep-linkable

`https://calendar.google.com/calendar/u/0/r/settings/import` frequentemente redireciona pra view normal sem montar a página de settings.

Caminho confiável é UI:
1. Click gear icon (canto sup direito, ~907, 32)
2. Click "Settings" no menu que aparece (~925, 80)
3. Click "Import & export" no menu lateral esquerdo

### file_upload bloqueado

`mcp__Claude_in_Chrome__file_upload` retorna `{"code":-32000,"message":"Not allowed"}` pra qualquer caminho local — é política de segurança da extensão pra evitar upload não-autorizado de arquivos do sistema.

Workaround: gerar o `.ics`, baixar via Blob (cai em Downloads), e pedir handoff manual de ~10s pro usuário fazer o upload no Google Calendar Import.

## Geração de ICS

Pra criar muitos eventos no Google de uma vez, ICS importado é **muito** melhor que criar evento-por-evento via URL (52 eventos via URL = ~150+ tool calls). Um ICS é um único upload manual.

Skeleton mínimo:

```
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//merge-agendas//run YYYY-MM-DD//PT
CALSCALE:GREGORIAN
BEGIN:VEVENT
UID:merge-agendas-<timestamp>-<i>@local
DTSTAMP:<utc_z>
DTSTART:<utc_z>
DTEND:<utc_z>
SUMMARY:<escaped>
DESCRIPTION:<escaped>
END:VEVENT
...
END:VCALENDAR
```

Escape ICS (RFC 5545): `\` → `\\`, `;` → `\;`, `,` → `\,`, `\n` → `\\n`.

## Idempotência

A tag `[merge-agendas | source=outlook | run=YYYY-MM-DD]` no campo `description` é o marcador. Quando extrair eventos no Google e ver essa tag, marcar `is_synced_copy=true` e tratar separadamente nas regras de match.

Se o usuário apagar acidentalmente a tag, o próximo merge pode duplicar — a validação cruzada por título+horário ainda protege parcialmente, mas não 100%.

## Limites de segurança

Encoded nas skills, pra não causar estrago em caso de bug:

- Máximo **50 criações** por direção sem confirmação extra.
- Máximo **10 deleções** por run sem confirmação extra.
- Se exceder, parar e mostrar a lista pro usuário.

## Volume típico (referência)

Para calibrar expectativas (do Felipe, mas serve de baseline):

- Outlook corporativo: ~90 eventos em 6 semanas (~15/semana), 60% deles "Cancelado:"
- Google pessoal: ~3 eventos em 6 semanas (eventos não-trabalho são poucos)

Logo, runs típicas: 30-50 criações no Google, 0-2 deleções.

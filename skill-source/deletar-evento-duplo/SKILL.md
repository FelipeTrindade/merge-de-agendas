---
name: deletar-evento-duplo
description: >
  Apaga um evento da agenda corporativa (Outlook Web) e/ou da agenda pessoal (Google Calendar)
  via Edge com Claude in Chrome. Identifica o evento por título + data/hora, abre o tile na UI,
  e clica no botão Excluir/Delete via JS (mais confiável que click por coordenada). Trata o
  diálogo de confirmação do Outlook automaticamente. Por padrão, apaga das DUAS agendas se o
  evento existir nas duas; pode ser unilateral mediante pedido.
  USE ESTA SKILL SEMPRE que o usuário pedir pra "apagar evento", "deletar evento", "cancelar
  reunião", "remover compromisso", "tira X do calendário", "cancela aquela call de Y",
  "apaga o evento de hoje às 19h", ou qualquer pedido pra remover um evento de calendário.
  Também é INVOCADA pela skill `merge-agendas` na fase de propagação de cancelamentos —
  quando um evento foi cancelado/removido no Outlook e a cópia sincronizada precisa sair do
  Google.
---

# Deletar Evento Duplo — Outlook + Google Calendar

## O que esta skill faz

Apaga um evento específico em uma ou nas duas agendas do Felipe. Pode ser chamada:

- **Diretamente pelo usuário** ("apaga o evento das 14h amanhã")
- **Internamente pela skill `merge-agendas`** quando detecta cópias órfãs/canceladas a remover

Fluxo:
1. Identifica o evento alvo por título + data/hora
2. Abre o tile no calendário
3. Aciona "Delete event" (Google) / "Excluir" (Outlook)
4. Trata confirmação se aparecer
5. Verifica que o tile sumiu

Tempo: ~5-10s por evento por agenda.

---

## Pré-requisitos

Mesmos da skill `merge-agendas` e `criar-evento-duplo`:

1. Edge aberto com as duas contas logadas
2. Claude in Chrome conectado ao Edge
3. Abas do Outlook e Google Calendar abertas na semana relevante

Se faltar algo, parar e pedir setup.

---

## Fase 1 — Parsear o pedido

Extrair do input do usuário:

| Campo | Obrigatório | Exemplo |
|-------|-------------|---------|
| **Título** ou **descritor** | Sim | "evento teste", "reunião com Maria", "aquela call das 14h" |
| **Data** | Sim | "hoje", "amanhã", "20/05" |
| **Hora** | Recomendado | "19h", "às 14h" — desambigua se houver múltiplos eventos no mesmo dia |
| **Agendas alvo** | Não — default ambas | "só do Google", "só do trabalho", "das duas" |

Se houver ambiguidade (múltiplos eventos batem com o descritor), perguntar via
`AskUserQuestion` qual deletar — **NUNCA chutar e deletar errado**. Deleção é irreversível.

---

## Fase 2 — Encontrar o evento

### Google Calendar (tabId da aba do Google)

```js
const all = document.querySelectorAll('[data-eventid]');
const matches = [];
for (const el of all) {
  const text = (el.innerText || '');
  const r = el.getBoundingClientRect();
  if (/<TITULO_REGEX>/i.test(text) && r.width > 0 && r.height > 0) {
    matches.push({
      eventid: el.getAttribute('data-eventid'),
      text: text.substring(0, 100),
      x: Math.round(r.x + r.width/2),
      y: Math.round(r.y + r.height/2)
    });
  }
}
```

Filtrar `matches` pela hora se houver mais de um.

### Outlook (tabId da aba do Outlook)

```js
const elems = document.querySelectorAll('[role="button"][aria-label]');
const matches = [];
for (const el of elems) {
  const lbl = el.getAttribute('aria-label') || '';
  if (/<TITULO_REGEX>/i.test(lbl) && /<HH:MM>/.test(lbl)) {
    const r = el.getBoundingClientRect();
    matches.push({
      lbl: lbl,
      x: Math.round(r.x + r.width/2),
      y: Math.round(r.y + r.height/2)
    });
  }
}
```

---

## Fase 3 — Deletar no Google

**Fluxo testado e funcional**:

### 3.1 — Abrir o popup do evento

Click na coordenada central do tile (a coord retornada pelo JS da Fase 2).

```
computer left_click (x, y) na tab do Google
sleep 2s
```

O mini popup com botões aparece (pencil, trash, email, 3-dots, X).

### 3.2 — Click no botão Delete via JS

**Não use coordenada** pra clicar no trash — a posição do popup varia conforme o tile (esquerda
do tile ou direita, dependendo de espaço). Em vez disso:

```js
const btns = document.querySelectorAll('[role="button"][aria-label], button[aria-label]');
let clicked = null;
for (const b of btns) {
  const lbl = b.getAttribute('aria-label') || '';
  if (/^delete event$/i.test(lbl)) {  // Em inglês MESMO na UI pt-BR
    const r = b.getBoundingClientRect();
    if (r.width > 0 && r.height > 0) {
      b.click();
      clicked = lbl;
      break;
    }
  }
}
```

### 3.3 — Verificar

```
sleep 2s
JS: contar [data-eventid] com width > 0 que batem com o título → deve ser 0
```

**Não há confirmação modal no Google** — deleta direto e mostra um banner "Event deleted"
no rodapé (some sozinho).

---

## Fase 4 — Deletar no Outlook

Mais passos que no Google porque tem confirmação obrigatória.

### 4.1 — Abrir o editor completo (NÃO o mini popup)

Click simples no Outlook abre um popup mini que **não tem botão Excluir**. Você precisa do
editor completo. Duas opções:

**Opção A — Duplo-click direto no tile**:
```
computer double_click (x, y) na tab do Outlook
sleep 4s
```

**Opção B — Click simples, depois click no ícone "Abrir em modo de exibição completo"** (canto
superior direito do popup mini):
```
computer left_click (x, y)  // abre popup mini
sleep 2s
computer left_click (popup.x + popup.width - 30, popup.y + 20)  // canto sup direito
sleep 3s
```

A opção A é mais simples — usar essa por padrão.

### 4.2 — Click "Excluir" via JS

```js
const btns = document.querySelectorAll('button[aria-label]');
let clicked = false;
for (const b of btns) {
  if ((b.getAttribute('aria-label') || '').toLowerCase() === 'excluir') {
    const r = b.getBoundingClientRect();
    if (r.width > 0 && r.height > 0) {
      b.click();
      clicked = true;
      break;
    }
  }
}
```

### 4.3 — Confirmar no dialog

Aparece dialog "Excluir evento — Tem certeza de que deseja excluir este evento?" com botões
"Excluir" (primário) e "Cancelar".

```js
const dialogs = document.querySelectorAll('[role="dialog"]');
let clicked = false;
for (const dlg of dialogs) {
  for (const b of dlg.querySelectorAll('button')) {
    if ((b.textContent || '').trim().toLowerCase() === 'excluir') {
      b.click();
      clicked = true;
      break;
    }
  }
  if (clicked) break;
}
```

### 4.4 — Voltar pra view de semana e verificar

```
navigate https://outlook.office.com/calendar/view/week (na tab do Outlook)
sleep 4s
JS: procurar aria-label com título e hora → deve ser 0
```

Importante: depois de excluir no editor, o Outlook deixa a URL em `/calendar/item/...`. Re-navegar
pra `/calendar/view/week` pra ver o estado atualizado e verificar.

---

## Eventos com participantes — cuidado

Se o evento tiver participantes (campo "Convidar participantes" não-vazio), o Outlook pode
mostrar dialog adicional: "Notificar os participantes do cancelamento?" — opções "Cancelar
reunião" (notifica), "Cancelar sem enviar" (não notifica), "Não cancelar".

**Default seguro**: cancelar sem enviar. NÃO mandar email de cancelamento involuntariamente
pros colegas — Felipe pode estar testando ou querer comunicar manualmente. Mas avisar no
chat:
> "Esse evento tem participantes (X, Y, Z). Cancelei sem mandar email — se quiser notificar,
> faz manualmente."

Detectar via JS: depois do click em "Excluir", se aparecer dialog com texto "participantes" ou
"convidados", clicar "Cancelar sem enviar".

Para eventos da skill `merge-agendas` (cópias com tag `[merge-agendas`), nunca há participantes —
o cuidado é apenas para casos diretos do usuário.

---

## Limites de segurança

- **Máximo 1 evento por chamada** quando invocada diretamente pelo usuário.
- Para chamadas em lote (vindas da `merge-agendas`), respeitar o limite de **10 deleções
  por run** já encoded lá. Esta skill aceita um array de targets nesse caso.
- **Confirmação extra no chat** se o evento detectado for um recorrente: "Esse evento é
  recorrente (toda terça às 9h). Quer deletar só essa ocorrência ou toda a série?" — deixar
  o Felipe decidir antes de prosseguir.

---

## Reportar resultado

Mensagem final:

```
✓ Evento deletado:
  • [Título] — [Data] [Hora]
  • Google: removido
  • Outlook: removido
```

Se falhou em uma:

```
Deleção parcial:
  ✓ Google: removido
  ✗ Outlook: não consegui clicar Excluir. Pode estar fora da view atual ou ter participantes
    bloqueando? Quer tentar de novo ou faz manual?
```

---

## Erros comuns

| Sintoma | Causa | Solução |
|---------|-------|---------|
| `[data-eventid]` retorna popup container, não o tile | O JS pegou o popup que abriu antes — filtrar por rect com `width > 0` e por estrutura (tile tem texto curto) | Já tratado no exemplo da Fase 2 |
| No Outlook, click no tile não abre nada | Tile foi só "selecionado", não aberto | Usar double_click ao invés de left_click |
| No Google, click no trash icon (coord) não deleta | A posição do popup mudou desde o screenshot | Sempre usar JS click no aria-label, não coordenada |
| Outlook fica em `/calendar/item/...` depois de excluir | É normal — re-navegar pra `/calendar/view/week` antes de verificar |
| Dialog "participantes" aparece | Evento tinha attendees | Clicar "Cancelar sem enviar" pra não notificar |

---

## Notas finais

- **Deleção é irreversível** no Google. O Outlook tem lixeira (Itens excluídos), então em
  caso de erro lá dá pra restaurar. Ainda assim, sempre verificar duas vezes o que vai
  deletar.
- Esta skill **não deleta séries recorrentes inteiras** — só ocorrências individuais. Se
  Felipe pedir explicitamente "deleta a série toda" / "tira essa reunião recorrente do
  calendário", pular o tile da ocorrência e ir direto no menu de série (Outlook tem "Série"
  ao lado de "Evento" no editor; Google tem opção no dialog que aparece ao deletar
  recorrente).

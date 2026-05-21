---
name: criar-evento-duplo
description: >
  Cria UM evento avulso simultaneamente na agenda corporativa (Outlook Web — outlook.office.com)
  E na agenda pessoal (Google Calendar — calendar.google.com), via Edge com Claude in Chrome.
  Usa deeplinks pré-preenchidos pra abrir o editor de cada agenda já com título/data/hora/descrição,
  e clica Salvar/Save em cada. Ideal para compromissos novos que o Felipe quer ver em ambos os
  lados imediatamente (ex: reunião, compromisso pessoal que afeta agenda do trabalho).
  USE ESTA SKILL SEMPRE que o usuário pedir pra "criar evento", "adicionar evento", "marca um
  compromisso", "agenda uma reunião", "põe no calendário", "marca uma call", "marcar reunião nas
  duas agendas", "criar evento nas duas", ou qualquer pedido pra colocar um único evento na
  agenda quando o contexto é dual (corporativa + pessoal). Se o usuário não especificar agenda,
  o padrão é criar nas DUAS. Se pedir explicitamente "só na pessoal" ou "só no trabalho", criar
  apenas naquela.
---

# Criar Evento Duplo — Outlook + Google Calendar

## O que esta skill faz

Cria um único evento simultaneamente nas duas agendas do Felipe (Outlook corporativo +
Google pessoal), usando os deeplinks que cada uma expõe. NÃO é uma sincronização em lote
(pra isso, use a skill `merge-agendas`). É uma criação one-shot rápida.

Fluxo típico:
- Felipe diz "criar evento reunião com cliente amanhã às 14h"
- A skill parseia, abre os dois deeplinks (Google + Outlook) em paralelo
- Clica Save/Salvar em cada um
- Verifica que ambos foram criados
- Reporta sucesso

Tempo total: ~15-20 segundos.

---

## Pré-requisitos

0. **Versão do repo atualizada** (opcional mas recomendado na primeira run da sessão). Se o
   Felipe perguntar pela versão, ou se for a primeira interação com o conjunto de skills nesta
   máquina, comparar `VERSION` local com a última tag no Git. Detalhes em
   `merge-agendas/SKILL.md` Fase −1.
1. **Edge aberto** com as duas contas logadas (corporativa + pessoal).
   - Se não estiver, usar `Start-Process msedge` via Desktop Commander e aguardar 5s.
   - Conferir `list_connected_browsers` — selecionar o que tem `name: "Edge"`.
2. **Claude in Chrome conectado** ao Edge.

Se algo falhar, parar e pedir pro Felipe abrir/logar manualmente.

---

## Fase 1 — Parsear o pedido

O Felipe vai falar em linguagem natural. Extrair:

| Campo | Obrigatório | Exemplos |
|-------|-------------|----------|
| **Título** | Sim | "reunião com cliente XPTO", "dentista", "almoço pai" |
| **Data** | Sim | "amanhã" → calcular; "sexta" → próxima sexta; "20/05" → literal |
| **Hora início** | Sim | "14h", "9:30", "às 15" |
| **Hora fim** | Não — default +1h | "até 16h", "1h de duração" |
| **Descrição** | Não | "discutir proposta de Q3" |
| **Local** | Não | "sala 3", "Av Faria Lima 1234" |
| **Agendas alvo** | Não — default ambas | "só na pessoal", "só no trabalho" |

**Sempre converter relativos pra absolutos** usando a data corrente (`env.Today`). Ex:
"amanhã às 14h" em 19/05/2026 → 2026-05-20T14:00:00-03:00.

**Se algo crítico estiver ambíguo, perguntar via `AskUserQuestion` antes de criar.** Critérios:

- Data não definida (ex: "marca reunião com cliente" sem dia) → perguntar
- Hora não definida (ex: "marca dentista amanhã" sem horário) → perguntar  
- Título genérico tipo só "reunião" (sem com quem) → confirmar
- Duração indefinida E o evento parece longo (ex: "treinamento", "workshop") → perguntar

Para casos rotineiros (título claro + data + hora), criar direto sem perguntar nada.

---

## Fase 2 — Garantir setup do Edge e abas

```
1. list_connected_browsers — selecionar o "Edge"
2. tabs_context_mcp createIfEmpty:true — pegar/criar aba inicial
3. Se só tem 1 tab, criar outra via tabs_create_mcp
4. tabIdGoogle = primeira aba; tabIdOutlook = segunda
```

A ordem importa pouco; ambas tabs vão pra deeplinks específicos a seguir.

---

## Fase 3 — Construir os deeplinks

### 3.1 — Google Calendar

```
https://calendar.google.com/calendar/u/0/r/eventedit
  ?text=<TITULO_URLENCODED>
  &dates=<INICIO>/<FIM>
  &details=<DESCRICAO_URLENCODED>
  &location=<LOCAL_URLENCODED>
```

Datas em formato `YYYYMMDDTHHMMSSZ` (UTC com Z no final). Conversão:

```js
function toGcalUTC(localIsoStr) {
  const d = new Date(localIsoStr);  // assume timezone -03:00
  const pad = (n) => String(n).padStart(2, '0');
  return `${d.getUTCFullYear()}${pad(d.getUTCMonth()+1)}${pad(d.getUTCDate())}T${pad(d.getUTCHours())}${pad(d.getUTCMinutes())}00Z`;
}
// Exemplo: '2026-05-19T21:00:00-03:00' → '20260520T000000Z'
```

### 3.2 — Outlook Web

```
https://outlook.office.com/calendar/0/deeplink/compose
  ?path=/calendar/action/compose
  &rru=addevent
  &subject=<TITULO_URLENCODED>
  &startdt=<ISO_LOCAL>
  &enddt=<ISO_LOCAL>
  &body=<DESCRICAO_URLENCODED>
  &location=<LOCAL_URLENCODED>
```

Datas no formato ISO local SEM timezone: `2026-05-19T21:00:00`. O Outlook interpreta
como horário local do usuário (timezone do navegador).

**Importante**: Outlook aceita `+` como espaço em URL params (mais comum) ou `%20`.
Google prefere `%20`. Pra simplicidade, usar `encodeURIComponent` nos dois e depois trocar
apenas no Outlook params se necessário.

---

## Fase 4 — Navegar e salvar

Sequência:

```
1. navigate (Google deeplink, tabIdGoogle) E navigate (Outlook deeplink, tabIdOutlook)
   — em browser_batch, paralelo
2. sleep 5s  — Outlook é mais lento; menos que 5s arrisca clicar antes do form carregar
3. screenshot da aba do Google pra confirmar form preenchido
4. Click Save no Google (Save button, geralmente x≈737, y≈40 na resolução 1258x952)
5. screenshot da aba do Outlook pra confirmar form preenchido  
6. Click Salvar no Outlook (Salvar button, geralmente x≈68, y≈75)
7. sleep 4s — espera os saves processarem
8. navigate de cada tab pra view do calendário pra verificação
```

**Atenção sobre paralelizar os cliques de Save**: NÃO bater Save dos dois ao mesmo tempo
sem aguardar o form de cada um carregar individualmente. Aprendizado: o Outlook às vezes
ainda não tem o form pronto quando o Google já tá — o click em (68, 75) cai em área vazia
e nada acontece. Melhor sequencial: salva Google, depois Outlook. Custa ~3s a mais e é
muito mais confiável.

---

## Fase 5 — Verificar criação

Após salvar e voltar pras views de semana, conferir via JS que cada evento aparece:

### Google
```js
const elems = document.querySelectorAll('[data-eventid]');
const found = [...elems].some(el => /<TITULO>/i.test(el.innerText || ''));
```

### Outlook  
```js
const elems = document.querySelectorAll('[role="button"][aria-label]');
const found = [...elems].some(el => {
  const lbl = el.getAttribute('aria-label') || '';
  return /<TITULO>/i.test(lbl) && /<HH:MM_INICIO>/.test(lbl);
});
```

Se uma das duas falhou: avisar o Felipe especificamente qual, e perguntar se ele quer
retry só dessa.

---

## Fase 6 — Reportar

Mensagem final curta no chat:

```
✓ Evento criado nas duas agendas:
  • [Título] — [Data] [Hora início]–[Hora fim]
  • Google Calendar: confirmado
  • Outlook (felipe.trindade@investsmart.com.br): confirmado
```

Se só uma deu certo:

```
Evento criado parcialmente:
  ✓ Google: criado
  ✗ Outlook: não consegui salvar (motivo: ...). Quer que eu tente de novo?
```

---

## Direções unilaterais

Se o Felipe pedir "só no Google" / "só na pessoal" / "só no trabalho" / "só no Outlook",
pular o deeplink da outra agenda e não verificar lá. Reportar só o que foi feito.

---

## O que NÃO fazer

- **Não adicionar participantes** automaticamente. Se o Felipe não pediu, não copiar.
- **Não copiar o evento criado em uma agenda pro merge da outra** — esta skill faz duas
  criações independentes, não usa o mecanismo de merge (tag `[merge-agendas]`).
- **Não criar série recorrente** a não ser que explicitamente pedido. Default é evento
  único.
- **Não criar com 'busy/free/tentative'** custom. Default do Outlook é "Busy", Google é
  "Busy" — manter padrão.
- **Não pedir confirmação pra cada evento** se o Felipe já passou todos os dados claros.
  Só perguntar quando faltar algo crítico.

---

## Coordenadas dos botões — referência pra clicks

Resolução padrão observada do Felipe: ~1258×952. Se mudar, usar `find` em vez de
coordenadas fixas.

| Botão | Localização | Coord (x, y) |
|-------|-------------|--------------|
| Google "Save" | Topo, centro-direita | (737, 40) |
| Outlook "Salvar" | Topo-esquerda | (68, 75) |

Se as coordenadas falharem (click em área vazia), usar `find` com query "Save button" /
"Salvar button" e clicar pelo `ref`.

---

## Erros comuns

| Sintoma | Causa provável | Tratamento |
|---------|----------------|------------|
| Outlook click no Salvar não fez nada | Form não carregou (paralelizou cedo) | Refazer só o Outlook — navigate, sleep 6s, click Salvar |
| Google manda pra landing page em vez do editor | Sessão Google deslogou | Pedir login |
| Aria-label de Outlook não acha o evento criado | Verificação rodou cedo demais | sleep 4s a mais, re-query |
| Título do evento ficou cortado | Caracter especial não escapou direito | Usar `encodeURIComponent` consistentemente |
| Evento criado em horário errado | Confusão timezone | Garantir que a entrada é ISO com -03:00 e a conversão pro Google usa UTC com Z |

---

## Notas

- **Outlook deeplink aceita ISO local sem TZ** (ex: `2026-05-19T21:00:00`) — interpreta
  no timezone do navegador. Não tentar UTC, dá errado.
- **Google deeplink exige UTC com Z** no formato `YYYYMMDDTHHMMSSZ` — sem `:` nem `-`.
- **Os dois aceitam o calendar default do usuário** sem precisar especificar. No Felipe,
  Google manda pra "Felipe Trindade", Outlook pra calendário corporativo.
- **Esta skill não tem deduplicação** — se rodada duas vezes seguidas com mesmo título e
  hora, vai criar dois eventos iguais. Comportamento esperado (Felipe quer poder marcar
  bloqueios idênticos quando precisar).

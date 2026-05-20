# Como usar — exemplos reais de conversa

Depois de instalar (ver `INSTALL.md`), as 3 skills disparam automaticamente quando você escrever frases naturais. Você não precisa decorar comandos.

Os exemplos abaixo mostram o que falar e o que esperar.

## Exemplo 1 — merge semanal completo

**Você**:
> Faça o merge das agendas

**Claude** (passa pela skill `merge-agendas` — leva ~3-8 min):
> Confirmando o setup...
> ✓ Edge conectado
> ✓ Outlook carregado (felipe.trindade@investsmart.com.br)
> ✓ Google Calendar carregado (felipenst11@gmail.com)
>
> Extraindo eventos das próximas 6 semanas...
> ✓ Outlook: 232 tiles brutos, 91 após filtrar cancelados
> ✓ Google: 5 eventos
>
> Computando o diff...
>
> ```
> PLANO DE MERGE — semana de DD/MM/AAAA
> ==========================================================
>
> Vou CRIAR 18 eventos no Google (vindos do Outlook):
>   • DD/MM 09:00  Reunião X
>   • DD/MM 14:00  Call com Y
>   • ...
>
> Vou DELETAR 2 eventos no Google (cancelados no Outlook):
>   • DD/MM 10:00  Daily — cancelado no Outlook
>   • DD/MM 15:00  Reunião Banco — removido do Outlook
>
> Já em sync (nada a fazer): 30 eventos
> Casos ambíguos para revisar: 1
>   ? "Daily" às 09:00 no Outlook vs "Stand-up" 09:00 no Google?
>
> ==========================================================
> TOTAL: 18 criações + 2 deleções. Confirma? (sim/não)
> ```

**Você**:
> sim

**Claude**:
> Gerando .ics com os 18 eventos...
> ✓ Arquivo salvo em `C:\Users\FELIPE\Downloads\merge-agendas-2026-MM-DD.ics`
>
> Pra finalizar (10s manual):
> 1. Google Calendar → ⚙️ → Configurações
> 2. Menu esquerdo → Importar e exportar
> 3. Selecionar arquivo → escolha o `.ics`
> 4. Confirma Import
>
> Enquanto isso, vou deletar os 2 cancelados...
> ✓ "Daily" às 10:00 — deletado do Google
> ✓ "Reunião Banco" às 15:00 — deletado do Google
>
> Merge concluído.

---

## Exemplo 2 — criar um evento avulso

**Você**:
> Cria evento "Almoço com cliente XPTO" amanhã 12:30 por 1h30

**Claude** (skill `criar-evento-duplo` — leva ~15-20s):
> Criando evento "Almoço com cliente XPTO" para amanhã (DD/MM) 12:30-14:00, nas duas agendas.
>
> ✓ Google: aberto, salvo
> ✓ Outlook: aberto, salvo
>
> Confirmado nas duas. Tá lá.

### Variação: só uma agenda

**Você**:
> Marca dentista quinta 14h, só na pessoal

**Claude**:
> Criando "dentista" quinta-feira (DD/MM) 14:00-15:00, **só no Google Calendar pessoal**.
>
> ✓ Google: aberto, salvo.

### Variação: faltou info

**Você**:
> Marca uma reunião amanhã

**Claude** (faz pergunta via `AskUserQuestion`):
> Antes de criar, preciso saber:
> - Com quem é a reunião? (título do evento)
> - Que horas?
> - Duração? (default 1h)

---

## Exemplo 3 — apagar evento

**Você**:
> Apaga aquele evento "Almoço com cliente" de amanhã

**Claude** (skill `deletar-evento-duplo`):
> Achei "Almoço com cliente XPTO" amanhã (DD/MM) 12:30-14:00, presente nas duas agendas. Vou apagar das duas.
>
> ✓ Google: deletado.
> ✓ Outlook: deletado (sem notificar participantes — não havia nenhum).

### Variação: ambiguidade

**Você**:
> Cancela aquela reunião de quinta

**Claude**:
> Encontrei 3 reuniões em quinta-feira (DD/MM):
> 1. 09:00 — Sprint planning
> 2. 14:00 — 1:1 com Maria
> 3. 16:30 — Café com investidor
>
> Qual quer cancelar?

---

## Dicas de uso

- **Datas relativas** (`amanhã`, `sexta`, `daqui 2 semanas`) funcionam — o Claude usa a data corrente
- **"As duas agendas"** ou **"só na pessoal"** / **"só no trabalho"** controlam direção
- **Confirmação obrigatória**: a skill `merge-agendas` sempre pede "sim/não" antes de criar/deletar em lote. As outras criam direto se a info estiver clara
- **Idempotente**: rodar "Faça o merge das agendas" duas vezes em sequência não duplica nada
- **Frequência recomendada**: 1x por semana pra `merge-agendas` (mantém a janela de 6 semanas sempre coberta)

## Quando algo dá errado

A skill **para e te avisa** em vez de continuar errando. Cenários típicos:

| Sintoma | O que dizer pra resolver |
|---------|--------------------------|
| "Edge não está conectado" | Abre o Edge e clica no ícone da extensão Claude pra parear |
| "Outlook não está logado" | Faz login manual em outlook.office.com no Edge |
| "Mais de 50 eventos pra criar — suspeito de bug" | Confirma "ok, pode criar" se achar ok, ou "deixa só os primeiros 10 pra testar" |
| "Achei 3 eventos com esse título, qual?" | Responde com hora ou número |

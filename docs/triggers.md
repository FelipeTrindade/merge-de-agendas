# Cheat sheet de triggers

Frases que disparam cada skill automaticamente. Você não precisa decorar — qualquer variação semântica próxima funciona, porque o Claude usa a descrição da skill pra decidir quando invocar.

## `merge-agendas`

Skill de sincronização semanal em lote (Outlook → Google).

- Faça o merge das agendas
- merge das agendas
- sincroniza minhas agendas
- junta as agendas / mescla as agendas
- sincronizar Outlook com Gmail
- atualiza o merge
- rodar o merge
- puxa os compromissos do trabalho pra agenda pessoal

## `criar-evento-duplo`

Skill de criação avulsa em ambas as agendas.

- Cria evento <título> <quando>
- Marca <evento> <quando>
- Agenda <reunião> <quando>
- Põe no calendário <evento>
- Marca uma reunião <quando>
- Adiciona evento <título>
- Marca call com <pessoa> <quando>

Variantes de direção:

- "só na pessoal" / "só no Google" → apenas Google
- "só no trabalho" / "só no Outlook" → apenas Outlook

## `deletar-evento-duplo`

Skill de remoção de eventos.

- Apaga evento <título>
- Deleta <evento>
- Cancela <reunião>
- Remove <compromisso> do calendário
- Tira <evento> da agenda
- Cancela aquela call de <quando>

Variantes:

- "das duas agendas" (default)
- "só do Google" / "só do Outlook"

## O que NÃO dispara as skills

Pra evitar gatilhos falsos (uma das maiores dores de skills sensíveis demais):

- Perguntas factuais sobre agenda ("o que tenho amanhã?") → o Claude responde direto, não dispara skill
- Pedidos pra criar evento em **outra** ferramenta ("agenda no Notion", "marca no Trello") → não dispara
- Discussão sobre evento sem ação ("qual o status daquela reunião?") → não dispara

## Combos típicos

| O que quero | O que falo |
|-------------|------------|
| Sincronizar tudo agora | "Faça o merge das agendas" |
| Bloqueio rápido nas duas agendas | "Marca [evento] [quando]" |
| Cancelar evento que eu marquei | "Apaga [evento]" |
| Remarcar | "Apaga [evento antigo]" + "Marca [evento] [novo horário]" |
| Conferir o que rodaria sem executar | "Faz o merge das agendas mas só me mostra o plano, não cria" |

# Template de memória pro Claude

Copia isso pra um arquivo no diretório de memória do seu usuário Claude (ver `INSTALL.md` passo 5). Edita os campos `<...>` com os teus dados.

Esse arquivo dá contexto pro Claude entender seu setup sem você precisar repetir toda hora. Tipo de memória: `project` + `feedback`.

---

```markdown
---
name: merge-agendas-setup
description: Setup de navegadores e contas pro merge de agendas. Importante porque pode ter mais de um Chromium logado com contas diferentes — fácil de confundir.
metadata:
  type: project
---

Setup das skills `merge-agendas` e `criar-evento-duplo`:

- **Navegador alvo**: <Edge | Chrome>
- **Conta corporativa (Outlook)**: <seu.email@empresa.com> — logada em outlook.office.com
- **Conta pessoal (Gmail)**: <seu.email@gmail.com> — logada em calendar.google.com
- **Outros navegadores Chromium presentes** (e o que rodam): <Chrome com conta pessoal X | nenhum>

A extensão Claude in Chrome se identifica como "Chrome" no `list_connected_browsers` mesmo quando está rodando no Edge. Pra diferenciar entre múltiplas instâncias conectadas, usar o campo `name` (que pode ser "Edge" ou "Chrome" dependendo da extensão).

**Why**: na primeira vez que essas skills rodaram, o Claude assumiu que "Chrome" = Edge com extensão e errou — abriu a conta errada e levou tempo pra perceber. Confirmar SEMPRE qual navegador antes de agir.

**How to apply**: antes de qualquer ação de calendário, chamar `list_connected_browsers`, achar o que tem `name == "<navegador_alvo>"`, e chamar `select_browser` com aquele deviceId.

## Preferências de uso

- **Direção do merge**: unilateral Outlook → Google por padrão. Não duplicar eventos pessoais pro Outlook a não ser quando pedido explicitamente.
- **Cancelamentos**: se um evento ficou "Cancelado:" no Outlook e a cópia ainda está no Google, deletar do Google.
- **Recorrentes**: copiar cada ocorrência individualmente, não tentar replicar a regra.
- **Janela**: 6 semanas a partir de hoje.
- **Sem participantes**: NUNCA copiar lista de attendees. Isso disparariam convites involuntários a colegas.
- **Sem links Teams/Meet**: não funcionam autenticados fora da agenda de origem.

## Padrões de gatilho

- "Faça o merge das agendas" / "sincronizar agendas" → skill `merge-agendas`
- "Cria evento X às Y" / "marca reunião" / "agenda compromisso" → skill `criar-evento-duplo`
```

---

Sugestão: salve também um arquivo `MEMORY.md` (índice) na mesma pasta:

```markdown
- [merge-agendas setup](merge_agendas_setup.md) — qual navegador alvo, contas logadas, preferências de merge.
```

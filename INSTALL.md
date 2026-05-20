# Instalação em uma máquina nova

Passo a passo pra rodar essas skills num computador novo.

## Pré-requisitos

- **Windows** (testado em Windows 10/11). Linux/macOS provavelmente funciona com ajustes nos caminhos.
- **Microsoft Edge** instalado (não Chrome — embora a extensão se chame "Claude in Chrome", precisamos do Edge porque é onde estão logadas as duas contas no setup do Felipe; se você prefere usar Chrome, basta inverter).
- **Claude Cowork** (desktop app) OU **Claude Code** (CLI).
- Conta GitHub (opcional, só se for clonar este repo).

## 1. Clonar o repo

```bash
git clone https://github.com/FelipeTrindade/merge-de-agendas.git
cd merge-de-agendas
```

Ou baixe direto pelo "Code → Download ZIP" no GitHub.

## 2. Instalar os MCPs/plugins necessários

Esses dois conectores precisam estar disponíveis na sua instância do Claude:

### a) Claude in Chrome

Extensão para navegador Chromium (funciona em Edge também). Instala na Chrome/Edge Web Store. Habilita a extensão dentro do Cowork via UI.

**Importante**: depois de instalar, abra o Edge e clique no ícone da extensão pra "parear" o navegador com o Claude. Isso faz `mcp__Claude_in_Chrome__list_connected_browsers` retornar o seu Edge.

### b) Desktop Commander

MCP que dá acesso de leitura/escrita ao sistema de arquivos do Windows e execução de processos. Usado pra:
- Abrir o Edge automaticamente quando não estiver aberto (`Start-Process msedge`)
- Mover arquivos entre pastas (ex: Downloads → projeto)

Instalação típica no Cowork: na busca de conectores, procura "Desktop Commander" e instala.

Detalhes sobre quais ferramentas específicas de cada MCP a skill usa em [`docs/connectors.md`](docs/connectors.md).

## 3. Instalar as skills

Cada `.skill` em `dist/` é um pacote zipado. Pra instalar:

1. No Cowork, abra Settings → Skills (ou similar)
2. "Import skill" / "Install from file"
3. Escolhe `dist/merge-agendas.skill` — instala
4. Repete com `dist/criar-evento-duplo.skill`

Ou clique no arquivo `.skill` direto no Explorador de Arquivos — o Cowork pode interceptar o duplo-clique se estiver configurado pra isso.

## 4. Setup das contas no Edge

A skill assume que **as duas contas estão logadas no Edge**:

- Conta Microsoft corporativa em `outlook.office.com`
- Conta Google pessoal em `calendar.google.com`

Verificar isso antes do primeiro run abrindo as duas URLs no Edge e confirmando que cada uma carrega a agenda direto sem pedir login.

## 5. Memória do Claude (opcional mas recomendado)

Pra que o Claude lembre do seu setup entre conversas (qual navegador, qual conta, etc), copie o conteúdo de [`docs/memory-template.md`](docs/memory-template.md) pra um arquivo de memória do seu usuário. O caminho varia:

- **Cowork** (Windows): `C:\Users\<seu-usuário>\AppData\Roaming\Claude\local-agent-mode-sessions\<sessão>\spaces\<space>\memory\merge_agendas_setup.md`
- **Claude Code**: `~/.claude/memory/` ou onde sua instância estiver configurada

Edite o arquivo trocando os emails de exemplo pelos seus.

## 6. Primeiro teste

Numa nova conversa do Claude, escreve:

> "Faça o merge das agendas"

(Tem [`docs/usage.md`](docs/usage.md) com exemplos passo-a-passo do que aparece no chat em cada cenário, e [`docs/triggers.md`](docs/triggers.md) com a lista completa de frases que disparam cada skill.)

A skill deve:
1. Conferir que o Edge está aberto e conectado
2. Abrir o Outlook e Google Calendar em abas separadas
3. Extrair eventos das próximas 6 semanas dos dois
4. Calcular diff (criar + deletar)
5. Te mostrar preview no chat
6. Esperar você responder "sim" pra prosseguir
7. Gerar `.ics` em Downloads e te guiar no upload manual no Google Calendar

Se der errado em qualquer ponto, a skill **para** e te avisa onde, sem criar/deletar nada.

## Troubleshooting

| Sintoma | Causa | Solução |
|---------|-------|---------|
| `list_connected_browsers` vazio | Extensão não pareada | Clique no ícone da extensão Claude no Edge e autorize |
| Outlook abre marketing page | Conta corporativa não logada | Logue manualmente em outlook.office.com no Edge |
| Google abre `/workspace.google.com/products/calendar` | Conta Google não logada | Logue em calendar.google.com |
| `file_upload` retorna "Not allowed" | Restrição da extensão | É política de segurança da Claude in Chrome — fazer upload do .ics manualmente é o caminho normal |
| Outlook deeplink dá erro | URL mal-formada | Conferir que `startdt`/`enddt` estão em ISO local SEM Z |
| Google Calendar mostra evento em ho
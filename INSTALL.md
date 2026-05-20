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

## 6. Confira a versão antes de rodar

Antes de QUALQUER run (primeira ou subsequente), garanta que o que você tem instalado bate com a versão mais nova no Git. As skills evoluem rápido — bug fix ou nova funcionalidade pode mudar a forma de uso.

```bash
cd <pasta-do-clone>/merge-de-agendas
git fetch --tags
INSTALADA=$(cat VERSION 2>/dev/null || echo "?")
ULTIMA=$(git tag --sort=-v:refname | head -n1 | sed 's/^v//')
echo "Instalada: v$INSTALADA  |  Última no Git: v$ULTIMA"
```

**Se a do Git for mais nova:**

1. `git pull` — puxa o código novo
2. Reinstala os 3 arquivos de `dist/` no Claude (a versão instalada **não auto-atualiza** quando o repo muda; precisa reinstalar manualmente)
3. Se `docs/memory-template.md` mudou, atualize sua memória também

**Se baterem**, pode rodar tranquilo.

Dica: dentro do chat com o Claude você pode pedir *"confere se o merge-de-agendas tá na versão mais nova"* — o Claude pode rodar esse mesmo check pra você.

## 7. Primeiro teste

Numa nova conversa do Claude, escreve:

> "Faça o merge das agendas"

(Tem [`docs/usage.md`](docs/usage.md) com exemplos passo-a-passo do que aparece no chat em cada cenário, e [`docs/triggers.md`](docs/triggers.md) com a lista completa de frases que disparam cada skill.)

A skill deve:
1. Conferir que o Edge está aberto e conectado
2. Abrir o Outlook e Google Calendar em abas separadas
3. Extrair eventos das próximas 6 semanas dos dois
4. Calcular diff (criar + deletar)
5. Te mostrar previ
# Conectores (MCPs) necessários

Quais ferramentas/plugins seu Claude precisa ter disponíveis pra rodar essas skills.

## Obrigatórios

### Claude in Chrome

Extensão de navegador + MCP server. Dá ao Claude acesso de leitura e automação ao seu navegador Chromium (Chrome ou Edge).

**Onde instalar**: Chrome Web Store (também funciona em Edge porque é Chromium).
**Site**: https://www.claude.com/product/claude-for-chrome

**Tools usadas pelas skills**:

| Tool | Skill que usa | Pra quê |
|------|---------------|---------|
| `list_connected_browsers` | ambas | Detectar Edge vs Chrome, escolher o correto |
| `select_browser` | ambas | Conectar ao Edge específico |
| `tabs_context_mcp` | ambas | Listar abas abertas, criar nova |
| `tabs_create_mcp` | ambas | Abrir aba nova quando necessário |
| `navigate` | ambas | Ir pra URLs de calendário e deeplinks |
| `get_page_text` | merge-agendas | Fallback de extração quando JS não funciona |
| `javascript_tool` | ambas | Extração via DOM (aria-labels), parse, gerar .ics |
| `find` | ambas | Achar botões pelo aria-label (Save, Salvar, file input) |
| `computer` (left_click, screenshot) | ambas | Clicar botões e verificar visualmente |
| `browser_batch` | ambas | Executar várias ações em uma chamada (mais rápido) |
| `file_upload` | merge-agendas | Tentativa de upload do .ics — note: **bloqueado** pela política de segurança da extensão; sempre cai pro handoff manual |

### Desktop Commander

MCP que dá acesso ao sistema de arquivos e processos Windows/macOS/Linux.

**Onde instalar**: catálogo de MCPs do Cowork ou via `claude mcp add`.

**Tools usadas pelas skills**:

| Tool | Pra quê |
|------|---------|
| `start_process` | Abrir Edge automaticamente (`Start-Process msedge`) quando não está aberto |
| `move_file` | Mover .ics gerado de Downloads pra pasta do projeto (pra upload via file_upload) |
| `get_file_info` | Confirmar que .ics chegou em Downloads antes de mover |
| `list_directory` | Inspecionar pasta de Downloads / projeto |

## Opcionais

### Scheduled Tasks

MCP de agendamento. **Não usado** pelas skills atualmente. Se você quiser rodar `merge-agendas` automaticamente toda semana, esse é o conector — peça ao Claude: "agenda 'Faça o merge das agendas' toda segunda às 9h".

## Permissões dentro do Cowork

Quando instalar as skills, o Claude vai pedir confirmação pra usar cada conector. Aceitar pra:

- `mcp__Claude_in_Chrome__*` — acesso ao navegador
- `mcp__Desktop_Commander__*` — acesso ao sistema de arquivos

Restringe se desconfortável; o pior caso é a skill parar e pedir intervenção manual.

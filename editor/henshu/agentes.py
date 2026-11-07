"""Ponte entre o chat do Henshū e os agentes de linha de comando (Claude Code e Codex).

Cada mensagem do chat vira uma execução não interativa do agente escolhido, **dentro da pasta do vídeo**:
- Claude: `claude -p … --output-format stream-json`; edições de arquivo liberadas, Bash só para ffprobe/tiktok/ls;
  o resto é negado automaticamente. A conversa continua com --resume <sessão>.
- Codex: `codex exec --json` com sandbox workspace-write (só escreve na pasta, sem rede); continua com `exec resume`.
As linhas JSON de saída viram eventos simples {"tipo": sessao|texto|acao|fim|erro, "texto": …}.
"""
import json, os, shutil

AGENTES = {"claude": "Claude", "codex": "Codex"}
FERRAMENTAS_CLAUDE = ",".join(["Read", "Edit", "Write", "Glob", "Grep",
                               "Bash(ffprobe:*)", "Bash(tiktok silencios:*)", "Bash(henshu-transcrever:*)", "Bash(ls:*)"])

INSTRUCOES = """# Henshū 編集 — você está editando um vídeo

Você foi chamado pelo chat do editor Henshū. A pasta atual é a pasta deste vídeo. Responda em **português do Brasil**,
curto e direto (o usuário assiste à edição acontecendo).

## Como editar
- O vídeo é descrito em **`projeto.json`**. Editar esse arquivo É editar o vídeo: o Henshū percebe a mudança e
  refaz a prévia sozinho em poucos segundos. Não renderize nada você mesmo.
- Formato:
```json
{
  "versao": 2,
  "formato": {"preset": "vertical", "largura": 1080, "altura": 1920, "fps": 30},
  "clipes": [ {"arquivo": "brutos/fala.mp4", "inicio": 2.0, "fim": 7.5, "volume": 1.0, "velocidade": 1.0,
               "enquadrar": "ajustar", "foco_x": 0.5, "foco_y": 0.5,
               "transicao": {"tipo": "corte", "duracao": 0.5}} ],
  "textos": [ {"texto": "3 dicas rápidas", "inicio": 0.0, "fim": 2.5, "posicao": "topo",
               "tamanho": 84, "cor": "#ffffff", "fonte": "padrao"} ],
  "legendas": {"ativo": true, "estilo": "frases", "posicao": "base", "tamanho": 0},
  "capitulos": [ {"inicio": 0.0, "titulo": "Introdução"} ],
  "musica": {"arquivo": "audio/fundo.mp3", "volume": 0.15},
  "observacoes": ""
}
```
  - **formato.preset**: `vertical` (1080×1920, TikTok/Reels/Shorts) ou `horizontal` (1920×1080, YouTube). Ao trocar,
    ajuste também largura/altura (vertical 1080×1920, horizontal 1920×1080).
  - **clipes** tocam em sequência; `inicio`/`fim` são segundos DENTRO do arquivo (`fim: null` = até o fim).
    `velocidade` 0.25–4 (2 = duas vezes mais rápido). `enquadrar`: `ajustar` (imagem inteira, com faixas) ou
    `preencher` (corta para ocupar a tela; `foco_x`/`foco_y` 0–1 escolhem o centro do corte — ex.: rosto à esquerda
    = foco_x 0.3). `transicao` vale para a passagem ao PRÓXIMO clipe: `corte`, `fade` (passa pelo preto) ou
    `dissolver` (mistura; encurta a linha do tempo pela duração).
  - **textos** usam o tempo da linha do tempo final; `posicao`: topo | centro | base; `fonte`: padrao | pixel;
    `tamanho` em pixels do vídeo final.
  - **legendas**: `estilo` frases | karaoke (palavra falada destacada) | pixel (identidade); `tamanho` 0 = automático.
  - **capitulos**: para vídeos horizontais/YouTube; o primeiro começa em 0. Use títulos curtos.
- Para conhecer os arquivos: `ls brutos audio` e `ffprobe -v error -show_entries format=duration -of csv=p=0 <arquivo>`.
- Para tirar pausas de uma fala: `tiktok silencios brutos/<arquivo>` (gera `brutos/<nome>_sem-pausas.mp4`).

## Falas, legendas e capítulos
- `henshu-transcrever` transcreve as falas (local) e gera **`legendas/legendas.json`**: frases com `inicio`, `fim`,
  `texto` e palavras com tempo, já no tempo da linha do tempo. Depois de mudar cortes/velocidade, rode
  `henshu-transcrever --so-legendas` para realinhar (rápido, usa o cache). Atenção: isso refaz o arquivo
  (a versão anterior fica em `legendas.json.anterior`).
- Para corrigir uma legenda, edite só o campo `texto` do segmento em `legendas/legendas.json`.
- Leia `legendas/legendas.json` para saber o que é dito e quando (ex.: cortar trechos, achar o gancho, criar capítulos
  pelos assuntos, escrever títulos e hashtags em `notas.md`).
- `notas.md` tem o roteiro/gancho do usuário — leia quando ajudar.

## Regras
- **Nunca apague, mova ou altere nada em `brutos/`**. Trabalhe só nesta pasta.
- Mantenha o `projeto.json` sempre válido (JSON correto). Faça a mudança pedida, nada além.
- Ao terminar, diga em uma ou duas frases o que mudou (ex.: "Cortei de 0:02 a 0:05 e pus o título no topo").
"""


def preparar_pasta(pasta):
    """Instruções para os agentes dentro da pasta do vídeo (AGENTS.md para o Codex, CLAUDE.md para o Claude)."""
    with open(os.path.join(pasta, "AGENTS.md"), "w", encoding="utf-8") as f: f.write(INSTRUCOES)
    with open(os.path.join(pasta, "CLAUDE.md"), "w", encoding="utf-8") as f: f.write("@AGENTS.md\n")


def disponivel(agente):
    return shutil.which(agente) is not None


def comando(agente, mensagem, sessao=None):
    if agente == "claude":
        cmd = ["claude", "-p", mensagem, "--output-format", "stream-json", "--verbose",
               "--permission-mode", "acceptEdits", "--allowedTools", FERRAMENTAS_CLAUDE]
        return cmd + (["--resume", sessao] if sessao else [])
    if agente == "codex":
        base = ["--json", "--skip-git-repo-check", "-c", 'sandbox_mode="workspace-write"']
        if sessao:
            return ["codex", "exec", "resume", *base, sessao, mensagem]
        return ["codex", "exec", *base, mensagem]
    raise ValueError(agente)


def _resumo_ferramenta(nome, ent):
    ent = ent or {}
    alvo = ent.get("file_path") or ent.get("path") or ent.get("pattern") or ent.get("command") or ""
    alvo = os.path.basename(alvo) if ent.get("file_path") else alvo
    rot = {"Read": "lendo", "Edit": "editando", "Write": "escrevendo", "Glob": "procurando", "Grep": "procurando",
           "Bash": "rodando"}.get(nome, nome)
    return f"{rot} {alvo}".strip()


def eventos(agente, linha):
    """Converte uma linha JSON do agente em zero ou mais eventos do chat."""
    try:
        d = json.loads(linha)
    except ValueError:
        return []
    t = d.get("type", "")
    if agente == "claude":
        if t == "system" and d.get("subtype") == "init":
            return [{"tipo": "sessao", "texto": d.get("session_id", "")}]
        if t == "assistant":
            out = []
            for c in (d.get("message") or {}).get("content") or []:
                if c.get("type") == "text" and c.get("text", "").strip():
                    out.append({"tipo": "texto", "texto": c["text"].strip()})
                elif c.get("type") == "tool_use":
                    out.append({"tipo": "acao", "texto": _resumo_ferramenta(c.get("name"), c.get("input"))})
            return out
        if t == "result":
            if d.get("is_error"):
                return [{"tipo": "erro", "texto": str(d.get("result") or d.get("subtype"))}]
            return [{"tipo": "fim", "texto": ""}]
        return []
    # codex
    if t == "thread.started":
        return [{"tipo": "sessao", "texto": d.get("thread_id", "")}]
    if t in ("item.started", "item.completed"):
        it = d.get("item") or {}; k = it.get("type") or it.get("item_type")
        if k == "agent_message" and t == "item.completed":
            return [{"tipo": "texto", "texto": (it.get("text") or "").strip()}]
        if k == "command_execution" and t == "item.started":
            c = it.get("command", "")
            for pre in ("/bin/bash -lc ", "bash -lc ", "/bin/sh -c "):
                if c.startswith(pre): c = c[len(pre):].strip("'\"")
            linhas = c.strip().splitlines() or [""]
            c = linhas[0][:90] + ("…" if len(linhas) > 1 or len(linhas[0]) > 90 else "")
            return [{"tipo": "acao", "texto": f"rodando {c}"}]
        if k == "file_change" and t == "item.completed":
            arqs = ", ".join(os.path.basename(c.get("path", "")) for c in it.get("changes") or [])
            return [{"tipo": "acao", "texto": f"editou {arqs}"}]
        return []
    if t == "turn.completed":
        return [{"tipo": "fim", "texto": ""}]
    if t in ("turn.failed", "error"):
        msg = (d.get("error") or {}).get("message") if isinstance(d.get("error"), dict) else d.get("message")
        return [{"tipo": "erro", "texto": str(msg or "falhou")}]
    return []

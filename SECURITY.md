# Segurança

O Ukiyo mexe em configurações do desktop e, em dois casos, do sistema (tela de login SDDM e repositório do Spotify).
Por isso o projeto segue estas regras:

- **Sem segredos no repositório:** nenhuma senha, token, chave de API ou dado de rede. O `.gitignore` bloqueia
  backups, capturas pessoais, retratos de configuração e saídas de vídeo.
- **Sem `sudo` automático:** os scripts que precisam de root (`themes/washi/scripts/aplicar-v5-login.sh` e
  `scripts/instalar-spotify.sh`) recusam rodar sem `sudo` e são executados por você.
- **Backup e reversão:** toda etapa faz backup antes de alterar algo e tem um script ou uma instrução para desfazer.
- **Agentes de IA confinados:** no editor Henshū, o Claude só edita arquivos da pasta do vídeo e só roda comandos
  de inspeção e da esteira; o Codex roda na sandbox `workspace-write` (escreve só na pasta, sem rede).
- **Repositório de terceiros com chave verificada:** o Spotify é instalado pelo repositório oficial, com a impressão
  digital da chave conferida e `Signed-By` restrito.

## Como relatar um problema

Abra uma *issue* sem colar dados pessoais (caminhos com o seu usuário, nomes de rede, tokens). Para algo sensível,
use o recurso de *Private vulnerability reporting* do GitHub neste repositório.

## Música
* [X] Queue para tocar músicas em sequência 
* [X] Remover uma música da queue 
* [X] Skip para pular a música atual
* [X] Skip para pular para uma música da fila de reprodução `-goto` ou `-skipto`
* [X] Shuffle para embaralhar as músicas na queue
* [ ] Loop para a música no momento ou para a fila inteira
* [X] Now Playing para ver informações da música atual 
* [X] Um evento para remover o bot automaticamente se estiver sozinho em uma Voice Call
* [X] Implementar `-configmusic` para o bot saber aonde enviar as logs de música
* [X] Implementar playlists do Youtube
* [ ] Adicionar autoplay
* [X] Adicionar `-playnext` para adicionar uma música na fila na próxima posição
* [X] Bot sempre estar ensurdecido quando no canal de voz por questões de privacidade
* [X] Implementar playlists do Spotify
  * [X] Playlists com arquivos locais (Podem não funcionar dependendo da metadata do arquivo local, precisa de mais testes)
* [X] Implementar albuns do Spotify
* [X] `-lyrics` para mostrar a letra da música atual (EXTREMAMENTE BUGADO)

## Moderação
* [X] Limpar mensagens de um canal de texto 

## Bugs
* [X] Evento para quando o bot for desconectado forçado, restaurar estado inicial (evitar bugs de fila)
* [X] Resolver quando a fila de reprodução é muito grande e o embed não pode ser enviado
* [X] Bug quando usados links no formato https://youtu.be/
* [X] Bug quando certos links eram colocados (Não sei a causa pois não acionada absolutamente nenhum erro, mas resolver o bug acima também o resolveu)
* [X] O bot para de funcionar sem motivo aparente, e só é resolvido com um reinicio

## GERAL
* Modificar o bot para funcionar com diversos servidores
  * [X] Criar db para armazenar valores a respeito de servidores
  * [X] Adicionar o servidor na db assim que o bot entrar
  * [X] Remover o servidor na db assim que o bot sair ou o servidor for deletado
  * [X] Adicionar o canal de música selecionado com o comando `-configmusic` pelo usuário
* [X] Transição para modularização cogs
* [ ] Converter comandos prefixados para comandos hibridos
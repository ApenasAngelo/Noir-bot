## Música
* [X] Queue para tocar músicas em sequência 
* [X] Remover uma música da queue 
* [X] Skip para pular a música atual 
* [ ] Shuffle para embaralhar as músicas na queue
* [ ] Loop para a música no momento ou para a fila inteira
* [X] Now Playing para ver informações da música atual 
* [ ] Um evento para remover o bot automaticamente se estiver sozinho em uma Voice Call
* [ ] Implementar `-configmusic` para o bot saber aonde enviar as logs de música

## Moderação
* [X] Limpar mensagens de um canal de texto 

## Bugs
* [ ] Evento para quando o bot for desconectado forçado, sair do canal (evitar bugs de fila)

## GERAL
* Modificar o bot para funcionar com diversos servidores
  * [X] Criar db para armazenar valores a respeito de servidores
  * [X] Adicionar o servidor na db assim que o bot entrar
  * [X] Remover o servidor na db assim que o bot sair ou o servidor for deletado
  * [X] Adicionar o canal de música selecionado com o comando `-configmusic` pelo usuário
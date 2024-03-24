# Noir Discord Bot

Esse repositório é para o meu bot pessoal para discord.
Esse projeto não tem a intenção de ser feito para uso por diversas pessoas, então está inicialmente configurado para uso em um servidor por vez. Caso você planeje utilizar esse bot para uso e hospedagem própria, tenha noção que ele possa não funcionar tão bem dependendo das suas necessidades, já que ele foi feito pensado especialmente no meu uso diário.

## Funcionalidades

O Noir será um bot multi-propósito, com diversas funções:
* Player de música para reprodução de spotify, YouTube, soundcloud e outros
* Comandos de gerenciamentos do servidor, assim como comandos de QoF
* Comandos de entretenimento
* Qualquer utilidade extra que eu achar necessário


## Documentação

O bot é muito experimental no momento, já que eu estou usando-o como um projeto de autoaprendizado, então tudo é muito volátil e não existe garantia de se manter na versão final. A documentação será feita quando o bot tiver uma base mais concreta.

## Suporte

Apesar de ser um projeto bem básico, é necessário que se tenha um conhecimento mínimo de python e das bibliotecas utilizadas. Não tente usar e modificar o código sem entender como elas funcionam, e pedidos de suporte sem o conhecimento das mesmas serão ignorados. Você pode começar estudando um pouco sobre as bibliotecas mais importantes, como a [discord.py](https://github.com/Rapptz/discord.py) e [Wavelink](https://github.com/PythonistaGuild/Wavelink).

## Como configurar

Ler o tutorial no repositório do [Wavelink](https://github.com/PythonistaGuild/Wavelink) para criar o node do Lavalink pode ser útil e bem autoexplicativo e fácil de se seguir, mas o repositório já vem com uma pasta pré-pronta para facilitar.

Para facilitar algumas configurações e esconder informações importantes, eu utilizei .env para algumas variáveis. Por questão de segurança, ela não é enviada para o repositório, então é necessário que o usuário crie. Para isso você pode usar como referência:
```
prefix =                            # O prefixo para usar os comandos

dc.TOKEN =                          # O Token do bot do seu Discord
MyUserID =                          # O ID do seu usuário. É utilizado para poder desligar o bot dentro do servidor, para debug
wl.PASSWORD =                       # Senha escolhida para Wavelink
wl.URI = http://localhost:2333      # A URI, recomendo a padrão do Wavelink
spotify.ClientID =                  # ClientID do seu app do Spotify Developer
spotify.ClientSecret =              # ClientSecret do seu app do Spotify Developer
genius.ClientID=                    # ClientID do seu app do Genius
genius.ClientSecret=                # ClientSecret do seu app do Genius
genius.TOKEN=                       # O Token do seu app do Genius
```

# Como iniciar

Iniciar o bot é como iniciar qualquer outro programa em python do seu terminal. Não esqueça que é necessário rodar o servidor do Wavelink.  
Primeiramente é necessário instalar todos os requisitos. Para isso, instale todos eles com o comando:

```
python -m pip install -r requirements.txt
```

Depois inicialize o servidor do Lavalink. Para isso, vá até o diretório aonde se encontra `Lavalink.jar` e abra o terminal. Digite o comando:

```
java -jar Lavalink.jar
```

Agora só falta iniciar o bot. Para isso, vá até o diretório aonde se encontra `main.py` e abra o terminal. Digite o comando:

```
python main.py
```

> Pode ser necessário substituir `python` por `py`, `python3`, `python3.11`, etc. dependendo das versões de python instaladas na sua máquina.


## Bugs ou pedidos

Caso você decida usar o código e encontre algum bug, envie ele na aba de [Issues](https://github.com/ApenasAngelo/Noir-bot/issues). Assim, eu posso tentar resolver e você também pode usar o bot corrigido.  
Por favor, não abra pedidos sobre coisas que estão no arquivo [TODO_LIST.md](https://github.com/ApenasAngelo/Noir-bot/blob/master/TODO_LIST.md), já que eles já estão sendo pensados e trabalhados para futura implementação.
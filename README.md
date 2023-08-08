# Noir Discord Bot

Esse repositório é para o meu bot pessoal para discord.
Esse projeto não tem a intenção de ser feito para uso por diversas pessoas, então está inicialmente configurado para uso em um servidor por vez. Caso você planeje utilizar esse bot para uso e hospedagem própria, tenha noção que ele possa não funcionar tão bem dependendo das suas necessidades, já que ele foi feito pensado especialmente no meu uso diário.

## Funcionalidades

O Noir será um bot multi-propósito, com diversas funções:
- Player de música para reprodução de spotify, youtube, soundcloud e outros
- Comandos de gerenciamentos do servidor, assim como comandos de QoF
- Comandos de entretenimento
- Qualquer utilidade extra que eu achar necessário


## Documentação

O bot é muito experimental no momento, já que eu estou usando-o como um projeto de auto aprendizado, então tudo é muito volátil e não existe garantia de se manter na versão final. A documentação será feita quando o bot tiver uma base mais concreta.

## Suporte

Apesar de ser um projeto bem básico, é necessário que se tenha um conhecimento mínimo de python e das bibliotecas utilizadas. Não tente usar e modificar o código sem entender como elas funcionam, e pedidos de suporte sem o conhecimento das mesmas serão ignorados. Você pode começar estudando um pouco sobre as bibliotecas mais importantes, como a [discord.py](https://github.com/Rapptz/discord.py) e [Wavelink](https://github.com/PythonistaGuild/Wavelink).

## Como baixar

Siga os seguintes passos:
* Baixe/clone o repositório
    *Você pode usar `git clone` ou Download zip no botão Code no topo da página
* Crie uma aplicação no [Developer Portal do Discord](https://discord.com/developers/applications)
* Siga os passos padrão para convidar o seu bot para o servidor

## Como configurar

Primeiro é necessário que se siga o tutorional no repositório do [Wavelink](https://github.com/PythonistaGuild/Wavelink) para criar o node do Lavalink. É bem auto-explicativo e fácil de se seguir

Para facilitar algumas configurações e esconder informações importantes, é utilizado .env para algumas variáveis. Por questão de segurança, ela não é enviada para o repositório, então é necessário que o usuário crie. Para isso criei um arquivo [example.env](https://github.com/ApenasAngelo/Noir-bot/blob/master/example.env) que deve ser renomeado para apenas .env e ter seus valores alterados para que o bot funcione de maneira correta. As explicações de cada uma das variáveis está dentro do próprio [example.env](https://github.com/ApenasAngelo/Noir-bot/blob/master/example.env) e é fácil de configurar.

# Como iniciar

Iniciar o bot é como iniciar qualquer outro programa em python do seu terminal. Não esqueça que é necessário rodar o servidor do Wavelink.  
Primeiramente é necessário instalar todos requisitos. Para isso, instale todos eles com o comando:

```
python -m pip install -r requirements.txt
```

Depois de instalar e inicializar o servidor do Wavelink, basta iniciar com o comando:

```
python main.py
```

> Pode ser necessário substituir `python` por `py`, `python3`, `python3.11`, etc. dependendo das versões de python instaladas na sua máquina.


## Bugs ou pedidos

Caso você decida usar o código e encontre algum bug, envie ele na aba de [Issues](https://github.com/ApenasAngelo/Noir-bot/issues). Assim, eu posso tentar resolver e você também pode usar o bot corrigido.  
Por favor não abra pedidos sobre coisas que estão no arquivo [TODO_LIST.md](https://github.com/ApenasAngelo/Noir-bot/blob/master/TODO_LIST.md), já que eles já estão sendo pensados e trabalhados para futura implementação.
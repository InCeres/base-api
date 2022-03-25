# Base API

Um modelo básico de API Python Flask usado na Plataforma InCeres.

Esse projeto tem o mínimo necessário para criar uma API de verdade (nós já temos 8 e contando) e ainda tem algumas coisas a mais como um service Pusher para usar o <a href="https://github.com/pusher/pusher-http-python" target="_blank">Pusher</a> que, basicamente, faz push de notificações do back para o front usando websocket. Coisa linda de Deus!

Tem também um módulo fabfile que usa o <a href="http://www.fabfile.org/" target="_blank">`Fabric`</a> para executar comandos de deploy em um servidor via `SSH`. Ele faz deploy de API e App em ambiente de PROD e STAG. 

Finalmente, para você rodar o projeto em um ambiente STAG ou PROD, você precisará do <a href="https://gunicorn.org/" target="_blank">`gunicorn`</a>, um WSGI muito bom e fácil de usar para Python. O módulo `gunicorn_conf.py` tem as configurações necessárias para isso. 

## Instalação

**Não se esqueça de trocar `base` pelo nome do seu projeto!**

### VirtualEnv

Recomendo usar um virtualenv para qualquer projeto Python. Isso vai te permitir isolar o contexto de uma API e trabalhar com diversas APIs na mesma máquina.

Se você ainda não usou um virtualenv no Python, bom começar com o <a href="https://virtualenvwrapper.readthedocs.io/en/latest/" target="_blank">virtualenvwrapper</a> que é um... ahn.. wrapper para o virtualenv... Na verdade, ele adiciona diversos comandos que facilitam a gestão dos virtualenvs.

    $ sudo pip install virtualenvwrapper

Após rodar o comando acima, você terá o virtualenv e o virtualenvwrapper instalado. Note que você precisa ser um SU para esse pip, pois o virtualenv vai ficar instalado no Python do SO.

Adicione as seguintes linhas no final do seu bash profile:

    $ export WORKON_HOME=$HOME/.virtualenvs
    $ source /usr/local/bin/virtualenvwrapper.sh

Reinicie seu terminal ou execute:

    $ source /usr/local/bin/virtualenvwrapper.sh

### Criando a API

Crie o virtualenv:

    $ mkvirtualenv base-api

Adicione as variáveis de ambiente para que sejam carregadas sempre que ativar o virtualenv. Para isso, crie o arquivo no caminho abaixo (no exemplo, usamos o vim para criar o arquivo):

    $ vim ~/.virtualenvs/fbi-api/bin/postactivate
    
Adicione as variáveis de ambiente em um arquivo chamado `.env` na raiz do seu projeto. Existe um arquivo `.env.sample` no projeto que é a base pára esse `.env`
  
Instale os pacotes pip necessários, lembre-se de estar dentro do virtualenv criado. Use o seguinte comando (do virtualenvwrapper) para ativar o virtualenv se ele ainda não estiver ativo:

    $ workon base-api

E depois, para instalar os pacotes:

    $ pip install -r requirements.txt

Esse comando, não é mais necessário ser um SU, pois você estará instalando os pacotes dentro do Python do virtualenv apenas.

### Criando o  banco

    $ sudo su postgres
    $ psql
    $ CREATE ROLE base SUPERUSER LOGIN PASSWORD 'base';
    $ CREATE DATABASE base;
    $ ALTER DATABASE base OWNER TO base;

**Não se esqueça de trocar `base` pelo nome do seu projeto dentro do .env no DATABASE_URL**

Esse projeto base vem configurado com o Alembic, um pacote Python para permitir transformar models feitos no SQLAlchemy em scripts Python para criar as tabelas no banco.

Se você está instalando um projeto já existente, vai precisar rodar as migrations para atualizar o banco recém criado com as tabelas do projeto:

    $ python manage.py db upgrade

Se você está iniciando um projeto novo, vai precisar iniciar o Alembic para poder criar migrations:

    $ flask db init

Toda vez que você criar um Model novo ou atualizar um Model existente, crie a migration:

    $ flask db migrate

E atualize o banco de novo com:

    $ flask db upgrade

## Desenvolvendo

Nesse momento, você está pronto para começar a desenvolver. Para rodar um WebServer de desenvolvimento do Flask execute:

    $ flask run

Nesse modo, toda vez que você editar qualquer módulo Python dentro do projeto, o Flask reinicia o WebServer para garantir que o código novo seja usado.

Para testar, abra a url abaixo no seu navegador:

http://0.0.0.0:33366/api/healthcheck

Provavelmente, eu esqueci alguma coisa, mas se não, você está pronto! Se eu esqueci, você vai perceber porque vai dar erro e aí você não estará pronto!

Lembre-se, Python é uma viagem sem volta. Antes de iniciar, tenha certeza de que não está deixando nada para trás! Mas se for o NodeJS _(credo)_ siga em frente e mesmo que ele chore de joelhos implorando, não olhe pra trás. Você vai ser mais feliz sem ele!

#!/usr/bin/env bash

export AMBIENTE=production
export BRANCH=master
export PROJECT_NAME=base
export HAS_CELERY=0

start() {
    COMMAND=start
    ACTION=STARTING
    _doit
}

stop() {
    COMMAND=stop
    ACTION=STOPING
    _doit
}

restart() {
    COMMAND=restart
    ACTION=RESTARTING
    _doit
}

status() {
    COMMAND=status
    ACTION=STATUS
    _doit
}

_doit() {
    echo ${ACTION} API
    sudo systemctl ${COMMAND} $PROJECT_NAME-api.service
    echo DONE API
    if [ $HAS_CELERY -eq 1 ]
    then
        echo ${ACTION} CELERY
        sudo systemctl ${COMMAND} $PROJECT_NAME-celery.service
        echo 'CELERY RESTARTED'
    fi
}

melogs() {
    tail -$1f ~/logs/*.log
}

deploy() {
    API_FOLDER=$HOME/projects/$PROJECT_NAME-api
    APP_FOLDER=$HOME/projects/$PROJECT_NAME-app

    echo 'GIT PUL NA API'
    cd $API_FOLDER && git checkout $BRANCH && git pull origin $BRANCH
    echo 'API ATUALIZADA PELO GIT'

    echo 'INSTALANDO DEPENDENCIAS PYTHON'
    $HOME/.virtualenvs/$PROJECT_NAME-api/bin/pip install -r $API_FOLDER/requirements.txt
    echo 'DEPENDENCIAS INSTALADAS'

    echo 'ATUALIZANDO BANCO'
    cd $API_FOLDER && $HOME/.virtualenvs/$PROJECT_NAME-api/bin/python manage.py db upgrade
    echo 'BANCO ATUALIZADO'

    echo 'GIT PULL NA APP'
    cd $APP_FOLDER && git checkout $BRANCH && git pull origin $BRANCH
    echo 'APP ATUALIZADA PELO GIT'

    echo 'GRUNT APP $AMBIENTE'
    cd $APP_FOLDER && bower install
    cd $APP_FOLDER && grunt $AMBIENTE
    echo 'BUILD DA APP PRONTO'
    restart
    echo 'DEPLOY PRONTO'
}

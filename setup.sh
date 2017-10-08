#!/bin/sh

setup_venv () {
	echo Configurando ambiente virtual
	if [ ! -d ~/.venv/bluebird/ ]; then
		mkdir ~/.venv/bluebird
		echo Installing virtualenv quietly
		python3 -m pip install --quiet virtualenv
		echo creating virtualenv
		virtualenv ~/.venv/bluebird/
	fi
	echo Ativando ambiente virtual em ~/.venv/bluebird
	source "/home/$USER/.venv/bluebird/bin/activate"
	which_python=$(which python)
	if [[ $which_python ==  *"bluebird/bin/python"* ]]; then
		pip install --quiet -r requirements.txt
	else
		echo "Unable to activate python virtual environment"
	fi
}


setup_venv
echo Invocando pássaro azul
python bluebird.py
echo Desativando ambiente virtual
deactivate

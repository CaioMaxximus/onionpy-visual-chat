PYTHON = python3
LOCAL_PYTHON = venv/bin/python3.9
INSTALL_SCRIPT = prepare-env.py
PIP = venv/bin/pip3

run :

	export APPLICATION_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
	PYTHONPATH=src $(LOCAL_PYTHON) -m root
 
install :
	${PYTHON} -m venv venv
	${PIP} install -r requirements.txt
	${LOCAL_PYTHON} ${INSTALL_SCRIPT}
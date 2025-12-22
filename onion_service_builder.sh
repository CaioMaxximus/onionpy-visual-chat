if [ ! -d "tor_service/files" ]; then
    mkdir -p tor_service/files
    cd tor_service
    apt download tor #downloads only the daemon files
    cd ..
    dpkg -x ./tor_service/tor*.deb ./tor_service/files #unpack everything
    mkdir -p ./tor_service/tor_instances
fi

export APPLICATION_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "APPLICATION_ROOT set to $APPLICATION_ROOT"

source venv/bin/activate


python3 root/root.py 
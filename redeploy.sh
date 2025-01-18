#/bin/bash
#git pull
helm dependency update
helm uninstall oai-xapp
sleep 2
helm install oai-xapp .

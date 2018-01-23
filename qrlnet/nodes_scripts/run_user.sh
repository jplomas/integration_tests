#!/bin/bash -u

#RUN pip install -i https://testpypi.python.org/pypi --extra-index-url https://pypi.python.org/simple/  --upgrade qrl

##########################################
# Get source code
rm -rf ${HOME}/QRL
if [ -z ${INTEGRATION_TESTINPLACE:-} ]; then
    echo "Cloning source from github"
    git clone -b ${REPO_BRANCH} https://github.com/${REPO_SLUG}.git ${HOME}/QRL
    cd ${HOME}/QRL
    GITHASH=$(git -C ${HOME}/QRL/ rev-parse HEAD)
    echo "Repo hash: $GITHASH"
else
    echo "Copying source from local deployment"
    ls /volumes/source
    rsync -qiar --progress /volumes/source/QRL/ ${HOME}/QRL --exclude tests_integration --exclude .git
    ls ${HOME}/QRL
fi

#########################################
# Install dependencies
sudo -H pip3 install -r ${HOME}/QRL/requirements.txt | grep -v 'Requirement already satisfied' | cat

#########################################
# Patch source code genesis
mkdir -p /home/${USERNAME}/.qrl/wallet/
sudo python3 /home/${USERNAME}/scripts/prepare_node.py

#########################################
# Execute phase
# TODO: We can probably remove this soon
echo "Boot phase: ${BOOT_PHASE}"
case "${BOOT_PHASE}" in
    freeze)
        # TODO: We can probably remove this soon
        tail -f /dev/null
        ;;
    start)
        python3 ${HOME}/QRL/start_qrl.py -l DEBUG
        ;;

    *)
        echo $"Usage: $0 {bootstrap|start}"
        exit 1
esac

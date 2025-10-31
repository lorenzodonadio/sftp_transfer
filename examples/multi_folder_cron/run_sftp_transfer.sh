#!/bin/bash

ENV_NAME="sftp"
PYTHON_SCRIPT="main.py"
# Set working directory
cd /home/lorenzo/Desktop/feuphd/sftp_routines


conda run -n "$ENV_NAME" python "$PYTHON_SCRIPT" ./examples/multi_folder_cron/configA.yaml
conda run -n "$ENV_NAME" python "$PYTHON_SCRIPT" ./examples/multi_folder_cron/configT.yaml
conda run -n "$ENV_NAME" python "$PYTHON_SCRIPT" ./examples/multi_folder_cron/configE.yaml


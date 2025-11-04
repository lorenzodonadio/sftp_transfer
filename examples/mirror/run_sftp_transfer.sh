#!/bin/bash

PYTHON_PATH="/home/user/miniconda3/envs/sftp/bin/python"
PYTHON_SCRIPT="main.py"

cd /home/lorenzo/Desktop/feuphd/sftp_routines

$PYTHON_PATH "$PYTHON_SCRIPT" ./examples/mirror/mirrorA.yaml
$PYTHON_PATH "$PYTHON_SCRIPT" ./examples/mirror/mirrorA.yaml
$PYTHON_PATH "$PYTHON_SCRIPT" ./examples/mirror/mirrorA.yaml


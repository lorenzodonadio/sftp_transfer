import paramiko
import os
import fnmatch
from sftputils import plain_transfer_files
from time import time as now
from mylogger import setup_logging
import yaml
import sys
import os
import argparse


def main():
    parser = argparse.ArgumentParser(description="SFTP File Transfer")
    parser.add_argument("config", help="Path to config YAML file")
    try:
        # Load configuration
        args = parser.parse_args()
        with open(args.config, "r") as f:
            conf = yaml.safe_load(f)

        remote_path = conf["paths"]["remote_dir"]
        local_path = conf["paths"]["local_dir"]

    except Exception as e:
        print(f"Startup Error: {e}")
        sys.exit(1)

import paramiko
import os
import fnmatch
from sftputils import plain_transfer_files
from time import time as now
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
        pattern = conf["paths"]["pattern"]

        print(f"START {now()} MIRROR: {remote_path} -> {local_path}  {pattern}")

        transport = paramiko.Transport((conf["sftp"]["host"], conf["sftp"]["port"]))
        transport.connect(username=conf["sftp"]["username"], password=conf["sftp"]["password"])
        sftp = paramiko.SFTPClient.from_transport(transport)
        if sftp is None:
            raise ValueError("ERROR: Unable to create SFTPClient")
    except Exception as e:
        print(f"Startup Error: {e}")
        sys.exit(1)

    try:
        sftp.chdir(remote_path)
        local_files = os.listdir(local_path)
        local_file_set = set(fnmatch.filter(local_files, pattern))
        rmt_files = sftp.listdir(".")
        rmt_files = [f for f in fnmatch.filter(rmt_files, pattern) if f not in local_file_set]

        plain_transfer_files(transport, remote_path, rmt_files, local_path)
        print(f"Transfered: {len(rmt_files)} files to {local_path}")
    except Exception as e:
        print(f"Unexpected ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

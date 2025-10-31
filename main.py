import paramiko
import os
import fnmatch
from sftputils import tar_and_transfer_files
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

        logger = setup_logging(conf["log"]["file"], conf["log"]["interval_days"])

        remote_path = conf["paths"]["remote_dir"]
        local_path = conf["paths"]["local_dir"]
        offset_s = conf["files"]["offset"]
        pattern = conf["files"]["pattern"]
        retires = conf["files"]["retries"]

        logger.info(f"START: {remote_path} -> {local_path}  {pattern} : older than {offset_s}s")

        transport = paramiko.Transport((conf["sftp"]["host"], conf["sftp"]["port"]))
        transport.connect(username=conf["sftp"]["username"], password=conf["sftp"]["password"])
        sftp = paramiko.SFTPClient.from_transport(transport)
        if sftp is None:
            logger.error("ERROR: Unable to create SFTPClient")
            return

        try:
            sesh = transport.open_session()
            sesh.exec_command("date +%s")
            remote_date = int(sesh.recv(30))  # secoonds since last epoch
            sesh.close()
            if abs(remote_date - now()) > 3600:
                err = f"Local vs remote time differente too big (1h): local: {now()} remote: {remote_date}"
                return logger.error(err)
        except:
            return logger.error(f"cant read remote date (date +%s), stopping the program")

    except Exception as e:
        print(f"Startup Error: {e}")
        sys.exit(1)
    try:
        sftp.chdir(remote_path)
        local_files = os.listdir(local_path)
        local_file_set = set([f.split(".")[0] for f in local_files])

        # remote_files = sftp.listdir(".")
        fattr = sftp.listdir_attr(".")
        # remote file filtering
        rmt_files = [f.filename for f in fattr if (f.st_mtime or now()) < now() - offset_s]
        rmt_files = sorted(fnmatch.filter(rmt_files, pattern))
        rmt_files = [f for f in rmt_files if f.split(".")[0] not in local_file_set]

        ok_files = []
        for i in range(retires):
            ok_files = tar_and_transfer_files(transport, remote_path, rmt_files, local_path)
            rmt_files = [f for f in rmt_files if f not in ok_files]
            logger.info(f"files: {len(ok_files)} OK {len(rmt_files)} remaining - {i+1} attempt")
            if len(rmt_files) == 0:
                break

        transport.close()
        logger.info("END OK")

    except Exception as e:
        try:
            transport.close()
        except:
            pass
        logger.error(f"Unexpected : {e}")


if __name__ == "__main__":
    main()

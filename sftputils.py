import paramiko
import os
import time
import logging

# Setup module-level logger
logger = logging.getLogger(__name__)


def wait_for_exit_status(channel: paramiko.Channel, timeout=10, check_interval=0.05):
    """
    Block until command completes or timeout is reached.
    """
    start_time = time.time()
    logger.debug(f"Waiting for command completion, timeout: {timeout}s")

    while (time.time() - start_time) < timeout:
        if channel.exit_status_ready():
            exit_status = channel.recv_exit_status()
            if exit_status != 0:
                error_msg = channel.recv_stderr(512).decode().strip()
                logger.error(f"Command failed with exit code {exit_status}: {error_msg}")
                return False, exit_status, error_msg

            logger.debug("Command completed successfully")
            return True, exit_status, ""

        time.sleep(check_interval)

    logger.warning(f"Command timed out after {timeout} seconds")
    return False, None, f"Timeout after {timeout} seconds"


def exec_with_timeout(channel: paramiko.Channel, cmd: str, timeout=5):
    """Execute command with timeout."""
    logger.debug(f"Executing command: {cmd}")
    channel.exec_command(cmd)
    return wait_for_exit_status(channel, timeout)


def plain_transfer_files(
    transport: paramiko.Transport, remote_path: str, remote_files: list[str] | str, local_path: str
):
    """
    Transfer files without compression.
    """
    if type(remote_files) == str:
        remote_files = [remote_files]

    logger.info(f"Transfer of {len(remote_files)} files from {remote_path} to {local_path}")

    sftp = paramiko.SFTPClient.from_transport(transport)
    if sftp is None:
        logger.error("Unable to create SFTPClient")
        return []

    successful_files = []
    sftp.chdir(remote_path)

    for rf in remote_files:
        try:
            local_file_path = os.path.join(local_path, os.path.basename(rf))
            logger.debug(f"Transferring {rf} to {local_file_path}")
            sftp.get(rf, local_file_path)
            successful_files.append(rf)
            logger.info(f"Successfully transferred: {rf}")
        except Exception as e:
            logger.error(f"Failed to transfer {rf}: {e}")

    logger.info(f"Success transfer: {len(successful_files)}/{len(remote_files)} files ")
    return successful_files


def tar_and_transfer_files(
    transport: paramiko.Transport, remote_path: str, remote_files: list[str] | str, local_path: str
):
    """
    Tar and transfer files with compression.
    """
    if type(remote_files) == str:
        remote_files = [remote_files]

    logger.info(f"Transferring {len(remote_files)} files from {remote_path} to {local_path}")

    sftp = paramiko.SFTPClient.from_transport(transport)
    if sftp is None:
        logger.error("Unable to create SFTPClient")
        return []

    successful_files = []
    sftp.chdir(remote_path)

    for rf in remote_files:
        logger.debug(f"Processing file: {rf}")
        remote_tar = tar_remote_file(transport, remote_path, rf)

        if remote_tar is None:
            logger.error(f"Failed to tar remote file: {rf}")
            continue

        try:
            local_tar_path = os.path.join(local_path, os.path.basename(remote_tar))
            logger.debug(f"Downloading tar file {remote_tar} to {local_tar_path}")
            sftp.get(remote_tar, local_tar_path)
            successful_files.append(rf)
            logger.debug(f"Successfully transferred: {rf} (as {remote_tar})")
        except Exception as e:
            logger.error(f"Failed to download tar file {remote_tar}: {e}")
            continue

        try:
            sftp.remove(remote_tar)
            logger.debug(f"Cleaned up remote tar file: {remote_tar}")
        except Exception as e:
            logger.warning(f"Failed to remove remote tar file {remote_tar}: {e}")

    logger.debug(f"Tar transfer completed: {len(successful_files)}/{len(remote_files)} files")
    return successful_files


def tar_remote_file(transport: paramiko.Transport, cwd: str, filename: str):
    """
    Create tar archive of remote file.
    """
    try:
        tarname = f"{filename.split('.')[0]}.tar.gz"
        tarcmd = f"cd {cwd} && tar -czf {tarname} {filename}"

        logger.debug(f"Creating tar archive: {tarname} for file: {filename}")

        sesh = transport.open_session()
        success, exit_code, error_msg = exec_with_timeout(sesh, tarcmd)
        sesh.close()

        if not success:
            raise ValueError(f"Tar command failed with exit code {exit_code}: {error_msg}")

        logger.debug(f"Successfully created tar archive: {tarname}")
        return tarname

    except Exception as e:
        logger.error(f"Error creating tar for {filename}: {e}")
        return None

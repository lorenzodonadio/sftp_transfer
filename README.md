### Example usage to transfer files from server to server using sftp

A config.yaml file must be supplied as first positional argument to `main.py`

**workflow**

1. read config
2. list both remote and local files
3. filter remote files to ensure:
   - pattern match
   - last modified before offset (seconds)
   - not present in local dir
4. tar gzip remote file
5. transfer tar.gz to local dir
6. remove tar.gz in remote dir
7. check if all files were transfered
8. retry `retries` times

**Key aspects:**

- dont forget to create a venv for this routine to work
- This routines copy files from one remote_dir to a local_dir, no multi directory support
- both remote and local dir MUST exist
- We can specify the pattern of the files to read from the remote_dir but not the ones to compare from the local dir
- Comparison of file names happen before the last period ( . ), so `file1.tar.gz` equals `file1.tsv`
- paths can be local or global but working with global paths is recomended, at least for remote dir
- logging is provided with a time rolling setup, with backup count of 4

  **CONFIG YAML:**

```
sftp:
  host: "host"
  port: 888
  username: "user"
  password: "password"

paths:
  remote_dir: "/home/ldonadio/sdrei_scripts"
  local_dir: "./localdata"

files:
  offset: 7200
  pattern: "E*.tsv"
  retries: 5

log:
  file: "sftp_transfer.log"
  interval_days: 7

```

**Crontab automation**

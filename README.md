*Telefeed (WIP)*

Note: `dcp = docker-compose`

### Migration:

Create migration
```shell script
dcp run --rm app db migrate -m "Add new column"
sudo chmod -R 777 migrations  # only for linux
```
Run migration
```shell script
dcp run --rm app db upgrade heads
```

#### Starting
Run application and worker
```shell script
dcp up app worker
```

### Other

Promote user as admin
```shell script
dcp run --rm app roles add hyzyla@gmail.com superuser
```

Update requirements.txt
```shell script
# install pip-tools
python3 -m pip install --user pip-tools
# add new requirement to requirements.in
echo 'django==2.0'>> filename
# Update requirements.txt via pip-compile
pip-compile
```
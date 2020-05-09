*Telefeed (WIP)*

Note: `dcp = docker-compose`
1) Migration:
```shell script
dcp run --rm app db migrate -m "Add new column"
sudo chmod -R 777 migrations  # only for linux
```
2) Run migration
```shell script
dcp run --rm app db upgrade heads
```
3) Run application and worker
```shell script
dcp up app worker
```
4) Promote user as admin
```shell script
dcp run --rm app roles add hyzyla@gmail.com superuser
```
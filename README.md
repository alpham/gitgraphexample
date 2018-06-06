##Installation
No need to any special requirements, just `python 3.6+` would be enough.
### Docker 
If you want to you may install `docker`.
### Docker Compose
If you want to you may install `docker-compose`.
##Initialization

#### As a python module:
```bash
python3.6 -m gitgraph_server
```
#### As docker container:
First you need to build the image:
```bash
docker build -t gitgraph:1.0
```
Second run the container:
```bash
docker run -d -p8000:8000 --name gitgraph_server gitgraph:1.0
```
#### As docker service:
Just use `docker-compose` for this.
```bash
docker-compose up -d
```
## Usage

Navigate to ```http://localhost:8000```

By default this will show you the first 100 commits of branch `master` of `odoo/odoo` repo.

#### Options
The server accepts the following optional url parameters:

`owner` \<string\>: The repo owner

`repo` \<string\> : The repo name 

`page` \<int\> : Page number 


####Example

```http://localhost:8000/?page=2&owner=odoo&repo=odoo```

```http://localhost:8000/?owner=apche&repo=hadoop```

```http://localhost:8000/?owner=apche&repo=spark&page=10```
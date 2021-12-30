* If it is required to replace development key pairs for JWT, run **_./gen_key.sh_**
* Docker containers will be launched with following CLI command: **_docker-compose up --build -d_**, in this assignment, the following services will run: **postgres, django, nginx and websocket**
* **ssl.csr and ssl.key** are self-signed certificate and private key, it's used for development only
* Access swagger webpage by **https://localhost/swagger**, please reference for retrieving users API doc
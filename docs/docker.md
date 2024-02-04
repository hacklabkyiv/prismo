Docker tips and tricks
================================================

## Running in `Docker`

Running PRISMO in a separate Docker container offers several advantages. It 
isolates data and ensures a well-defined environment for smooth operation. 
You can verify everything is ready for Docker deployment by running the
following command:
```commandline
$ docker build --no-cache -t prismo-app .
```
This command build a container and sets all environment variables from dockerfile.
```commandline
$ docker run --name=prismo-app -p 80:5000 --restart always --detach -v "$(pwd)/data/:/app/external/" prismo-app
```
This command runs the newly built container and starts the server on port 80. Note that on some systems, port 80 might be 
unavailable for non-privileged users. For development purposes, you can use 
the alternative mapping \`5000\:5000\` instead\.
As shown in the command, the `-v "</span>(pwd)/data/:/app/external/"` 
option mounts an external volume where you should store your `database.db` 
and `config_docker.json` files. This volume persists data and configuration 
outside the container, ensuring they are not lost even if the container is 
deleted.

**Additional Notes:**

- Remember to replace the placeholder values for environment variables like `DATABASE_URL` and `SECRET_KEY` with your actual settings in the example commands.

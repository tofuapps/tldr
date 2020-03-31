# cs5131-project

## Installing
You will need the following on your system:

* Python3
* Pip3
* Pipenv

To install the dependencies, enter the following in the root directory
```
pipenv sync
```

## Running

You will need to start both the ui and api server. A script `tmux.sh` is available to start both servers in split view in a detached tmux session.

### UI Server
Start a new shell in the current directory and enter
```
cd ui && npm start
```

### API Server
Now, in a separate shell in the current directory enter
```
pipenv run python3 api_server.py
```

### Command-line Interface
If you only want to test the AI component of this project, run
```
pipenv run python3 main.py
```
An empty output is expected. Pass the option `--help` or `-h` to view the complete list of available options.

# Major Tom Scripting API Examples in Python

> Note: a shared library is Coming Soon™.

## Setup

This setup is only needed if you do **not** have docker.

1. Setup a virtualenv (first time only)
    ```bash
    pip3 install virtualenv
    virtualenv virtualenv -p `which python3`
    # or: python3 -m venv virtualenv
    ```
1. `source virtualenv/bin/activate`
1. `pip3 install --upgrade -r requirements.txt`

## Usage

View, edit, and run the example scripts. You'll need to replace `YOUR_SCRIPT_TOKEN` with your Script's token.

### With Docker

```
./run-docker.sh 
```


### Without Docker

For example:

```bash
python execute_command.py
```

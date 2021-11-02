# Example Major Tom Scripts

These example scripts use Major Tom's Scripting API to automate operations.

# Usage

### Quick start (requires Docker)

This provides an interactive menu to select your script. You will need access to a Major Tom instance and a token from the UI.

```
./run-docker.sh
```

### Manually

#### Setup

1. Setup a virtualenv (first time only)
    ```bash
    pip3 install virtualenv
    virtualenv virtualenv -p `which python3`
    # or: python3 -m venv virtualenv
    ```
1. `source virtualenv/bin/activate`
1. `pip3 install --upgrade -r requirements.txt`

#### Executing Scripts

The structure of most scripts is:

```bash
python ./python/script_name.py {CLOUD_URL} {SCRIPT_TOKEN}
```

Examples:
```bash
python ./python/execute_command.py app.majortom.cloud 12345656780abcefghijkl12345656780
```


### Development

You can develop against a branch of the scripting API by adding something like the following to requirements.txt:
```
git+https://github.com/kubos/majortom_scripting_package@BRANCH_NAME#egg=majortom-scripting
```
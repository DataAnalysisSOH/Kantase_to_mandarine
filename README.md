# Mandarin Cantonese Translator

This is an application that translates some of the Mandarine wording into the HK Cantonese wording so that the audience should understand the content better and more comfortable.


## Development

1. Create a virtual environment for this project

    ```bash
    python -m venv .venv
    ```

2. Install dev and runtime dependencies

    ```bash
    pip install -r requirements-dev.txt
    ```

## Deploy

Run the following command from the project root to deploy.

```zsh
# Define function name to which code is deployed
export LAMBDA_NAME="mandarin-cantonese-translator"

# Define target environment for loading different config
export TARGET_ENV="dev"

# Deploy to AWS account
./scripts/deploy.sh
```

The above command assumes that a Lambda is already created manually in the AWS account.




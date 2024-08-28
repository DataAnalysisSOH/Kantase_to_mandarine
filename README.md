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
./scripts/deploy.sh
```

The above command assumes that a Lambda is already created manually in the AWS account.




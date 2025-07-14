#!/bin/zsh

# The set -e option instructs the shell to exit immediately 
# if any command or pipeline returns a non-zero exit status,
# which usually indicates an error or failure. 
set -e

# The set -x option instructs the shell to print each command 
# or pipeline before executing it, preceded by a special prompt 
# (usually +). This can be useful for debugging scripts, but it 
# can also be too verbose and cluttered, especially for long or 
# complex scripts.
set -x


if [[ -z "${LAMBDA_NAME}" ]]; then
  echo "Environment variable LAMBDA_NAME is not set. Please use 'export LAMBDA_NAME=<Your Lambda's Function Name>' to define"
  echo "Default value 'mandarin-cantonese-translator' is used as the Lambda name"
  FUNCTION_NAME="mandarin-cantonese-translator"
else
  echo "Lambda's function name is '${LAMBDA_NAME}'"
  FUNCTION_NAME="${LAMBDA_NAME}"
fi

if [[ -z "${TARGET_ENV}" ]]; then
  echo "Environment variable TARGET_ENV is not set. Please use 'export TARGET_ENV=<dev or prod>' to define"
  echo "Default value 'dev' is used as the deployment target environment"
  DPLY_TARGET_ENV="dev"
else
  echo "Deployment target environment is '${TARGET_ENV}'"
  DPLY_TARGET_ENV="${TARGET_ENV}"
fi


# Start with a clean distribution folder
rm -rf ./.dist/
mkdir -p ./.dist/

# Copy Lambda Function Hanlder
cp ./src/lambda_function.py ./.dist/lambda_function.py

# Install requirements.txt in ./.dist folder
pip install -r requirements.txt -t .dist

cd .dist
zip -r translator_lambda.zip .

# Update Lambda with the latest ZIP file
read "confirm?Do you want to continue deploying function '${FUNCTION_NAME}'? (Y/N): "
if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
  echo "Deployment cancelled."
  exit 0
fi
aws lambda update-function-code \
    --function-name "${FUNCTION_NAME}" \
    --zip-file fileb://translator_lambda.zip

# Update Lambda with the latest configuration
read "confirm?Do you want to continue deploying configuration changes for function '${FUNCTION_NAME}'? (Y/N): "
if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
  echo "Deployment cancelled."
  exit 0
fi
aws lambda update-function-configuration \
    --function-name "${FUNCTION_NAME}" \
    --environment "{\"Variables\":`cat ../config/${FUNCTION_NAME}.${DPLY_TARGET_ENV}.json`}"
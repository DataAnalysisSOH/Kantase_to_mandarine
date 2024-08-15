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
aws lambda update-function-code \
    --function-name mandarin-cantonese-translator \
    --zip-file fileb://translator_lambda.zip

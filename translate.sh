#!/bin/sh

# Usage: ./translate.sh ./lwn dev-tools llama3
python main.py --path "$1" --target "$2" --model "$3"
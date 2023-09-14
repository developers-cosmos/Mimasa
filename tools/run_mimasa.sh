#!/bin/bash

run_setup=false
run_download=false

while getopts "sd" opt; do
  case $opt in
    s) # Set the run_setup flag when -s option is provided
      run_setup=true
      ;;
    d) # Set the run_download flag when -d option is provided
      run_download=true
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      ;;
  esac
done

if $run_setup; then
  python setup.py install
fi

if $run_download; then
  python src/common/download_data.py
fi

python src/main.py

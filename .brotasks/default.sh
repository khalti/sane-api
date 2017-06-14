#!/bin/sh

project=$(basename `pwd`)

init () {
  source .env/bin/activate
  echo "Happy hacking !!!"
}

$@

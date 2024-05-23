#!/bin/bash

for zipfile in corpus/*/*.zip
do
	kr_number="$(basename $(dirname $zipfile))"
	filename="$(basename $zipfile)"
	if [ ! -d "corpus/$kr_number/$kr_number-${filename%.zip}" ]; then
		unzip -n -d "$(dirname $zipfile)" $zipfile
	fi
done

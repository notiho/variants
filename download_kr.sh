#!/bin/bash

mkdir -p corpus

cat dual_kr_ids.txt | while read line || [[ -n $line ]];
do
	echo mkdir -p corpus/$line
	if [ ! -e corpus/$line/WYG.zip ]
	then
		wget -P corpus/$line "https://github.com/kanripo/$line/archive/refs/heads/WYG.zip"
		sleep 3s
	fi
	if [ ! -e corpus/$line/SBCK.zip ]
	then
		wget -P corpus/$line "https://github.com/kanripo/$line/archive/refs/heads/SBCK.zip"
		sleep 2s
	fi
done

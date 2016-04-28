#!/usr/bin/env bash

valid_test=(colouring)
param=`echo $1`

DIR=""
arr=$(echo $PWD| tr "/" "")
for i in $arr; do
	DIR=$DIR$i"/"
	if [ $i == "examination-scheduling"]; then
		break
	fi
done

test_file=$DIR"tests/test_"$param".py"
if [ -f $test_file ]; then
	echo "Test "$param
	echo `python $test_file`;
fi

if [ $param == "all" ]; then
	for name in $valid_test; do
		echo "Test "$name
		echo `python $DIR"tests/test_"$name".py"`
	done
fi

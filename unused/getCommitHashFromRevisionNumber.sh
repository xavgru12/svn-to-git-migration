#!/bin/bash

while read line; do
    if [[ $line == *"r508730 |"* ]]; then
        echo $line | awk -F '|' '{print $2}'
    fi
done < <(git svn log --show-commit --oneline)
#!/bin/bash

SOURCE_DIR=$1
DESTINATION_DIR=$2

if [ "${SOURCE_DIR}" == "" ]; then
  echo "SOURCE_DIR is not specivied"
  exit 1
fi
if [ ! -d "${SOURCE_DIR}" ]; then
  echo "SOURCE_DIR does not exists"
fi
if [ "${DESTINATION_DIR}" == "" ]; then
  echo "DESTINATION_DIR is not specivied"
  exit 1
fi
if [ ! -d "${DESTINATION_DIR}" ]; then
  echo "DESTINATION_DIR does not exists"
fi

echo "Using SOURCE_DIR=${SOURCE_DIR}"
echo "Using DESTINATION_DIR=${DESTINATION_DIR}"

find "${SOURCE_DIR}" -type f | while read line; do
  OUTPUT=$(exiftool -s -s  -ImageWidth -ImageHeight "${line}")
  WIDTH=$(echo $OUTPUT | sed 's/[^0-9]*\([0-9]*\)[^0-9]*\([0-9]*\)/\1/')
  HEIGHT=$(echo $OUTPUT | sed 's/[^0-9]*\([0-9]*\)[^0-9]*\([0-9]*\)/\2/')
  if [ "${WIDTH}" -gt "${HEIGHT}" ]; then
    FILENAME=$(basename "${line}")
    if [ -f "${DESTINATION_DIR}/${FILENAME}" ]; then
      echo "FILE \"${line}\" ALREADY PRESENT IN DESTINATION_DIR"
    else
      cp -a "${line}" "${DESTINATION_DIR}"
    fi
  fi
done

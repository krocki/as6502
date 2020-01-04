#!/bin/bash
set -eu
md5_x=`md5sum $1.bin | cut -d " " -f 1`
md5_y=`md5sum $1.ref | cut -d " " -f 1`

diff $1.bin $1.ref
if [ $? == 0 ]
  then
  echo "$1 TEST PASSED"
  else
  echo "$1 TEST FAILED"
fi
#echo "$md5_x"
#echo "$md5_y"

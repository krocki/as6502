#!/bin/bash
TESTS=(sierp0 sierp1)

for t in ${TESTS[@]}; do
  rm -rf $t.bin
  python3 as6502.py -c $t.a65 -o $t.bin
  ./verify.sh $t
done

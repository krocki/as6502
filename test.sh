#!/bin/bash
TESTS=(prog1 prog2 prog3 prog4 prog5 prog6 prog7 prog8)

for t in ${TESTS[@]}; do
  rm -rf $t.bin
  python3 as6502.py -c $t.a65 -o $t.bin
  ./verify.sh $t
done

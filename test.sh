#!/bin/bash
TESTS=(prog1 prog2 prog3)

for t in ${TESTS[@]}; do
  python3 as6502.py -c $t.a65 -o $t.bin
  ./verify.sh $t
done

# -*- coding: utf-8 -*-
# author: krocki

import argparse
import re
from defs import opcodes

def assemble(lines, opt, pc=0x600):

  if opt.verbose:
    print('Scanning for labels...')

  if opt.verbose:
    print('Assembling...')

  pattern = '^(([A-Za-z].*?)(\s+((#?)(\$)?([0-9a-fA-F]*)))?)?(\s*(\;.*)?)?$'
  #pattern = '^([A-Za-z].*?)(\s+((#?)(\$)?([0-9a-fA-F]*)))?$'

  data = {}
  instr = {}

  pos = 0

  for i,l in enumerate(lines):
    m = re.search(pattern, l)
    if opt.verbose:
      print('line {}=[{}]'.format(i,l))
      print('regex groups={}'.format(m.groups()))

    # syntax: expression = op (space arg)?
    expr=m.group(1)             # entire expression
    op=m.group(2)               # op

    if op==None: # empty or comments
      continue

    is_unary=True if m.group(4)==None else len(m.group(4))==0 # no args
    if is_unary: # no arguments
      encoding=opcodes[op][10] # sngl
      argbytes=0
    else: # 1 or more arguments
      argraw=m.group(4)           # arg string
      is_imm=len(m.group(5))==1
      is_hex=len(m.group(6))==1
      argval=int(m.group(7), 16) if is_hex else int(m.group(5), 10)
      arglen=len(m.group(7))
      if is_imm:
        encoding=opcodes[op][0] #imm
        argbytes=1
      else:
        if arglen<3:
          encoding=opcodes[op][1] #zp
          argbytes=1
        else:
          encoding=opcodes[op][4] #abs
          argbytes=2

    if opt.strip:
      print('{}'.format(expr))

    if opt.verbose:
      xs=opcodes[op]
      x_str = [hex(x) if x!=None else '' for x in xs]
      print('{:} {}'.format(op, x_str))
      print('argval={}, arglen={}\n'
            'encoding={:x}, argbytes={}'.format(
            argval, arglen, encoding, argbytes))

    if encoding==None:
      print('uh-oh')
    else:
      data[pos] = encoding
      addr=pos
      s='0x{:04x}: {:02x}'.format(pos, encoding)
      pos+=1
      for b in range(argbytes):
        data[pos] = (argval >> (8*b)) & 0xff
        s+=' {:02x}'.format(data[pos])
        pos+=1

      instr[addr] = s
      if opt.verbose: print(s + '\n')

  prog_len=max(data)+1
  mem = [0x00] * prog_len
  for k in data:
    mem[k] = data[k]

  if opt.verbose:
    print('Assembled, {} Bytes'.format(prog_len))

  return mem, instr

if __name__ == "__main__":

  # parse args
  parser = argparse.ArgumentParser(description='')
  parser.add_argument('-c',
    '--input', type=str, required=True, help='source file')
  parser.add_argument('-o',
    '--output', type=str, help='output file')
  parser.add_argument('-v',
     '--verbose', action="store_true", help='verbose')
  parser.add_argument('-strip',
     '--strip', action="store_true", help='remove whitespace and comments')

  opt = parser.parse_args()
  if opt.verbose: print(opt)

  ifile=opt.input
  ofile=opt.output

  with open(ifile, 'r') as fp:
    lines = fp.readlines()

  lines = [line.rstrip('\n') for line in lines]

  if opt.verbose:
    print('{:} read, {:} lines'.format(ifile, len(lines)))
    [print('line {:}: [{:}]'.format(i, l))
       for i,l in enumerate(lines)]

  mem, instr = assemble(lines, opt, pc=0x600)

  if ofile:
    with open(ofile, 'wb') as fp:
      fp.write(bytearray(mem))
  else:
    for k,i in enumerate(instr):
      print('[{:02d}] {:}'.format(k, instr[i]))
    print('')
    print(''.join('{:02x}'.format(m) for m in mem))

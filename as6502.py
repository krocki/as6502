# -*- coding: utf-8 -*-
# author: krocki

import argparse
import re
from defs import opcodes

def assemble(lines, opt, pc=0x600):

  if opt.verbose:
    print('Assembling...')

  pattern = '^\s*((?P<label>[A-za-z0-9_]+):)|(?P<expr>(?P<op>[A-Za-z]{3}?)\s*(?P<argraw>(?P<imm>#?)(?P<hex>\$?)(?P<argval>[0-9a-fA-F]{1,4})|(?P<arglab>[A-za-z0-9_]*?)))?\s*(\;.*)?$'

  data = {}
  instr = {}

  pos = 0

  labels = {}

  for i,l in enumerate(lines):
    m = re.search(pattern, l)
    if opt.verbose:
      print('line {}=[{}]'.format(i,l))
      print('regex groups={}'.format(m.groups()))

    # syntax: expression = op (space arg)?
    expr=m.group('expr')        # entire expression
    op=m.group('op')            # op
    label=m.group('label')      # label

    if opt.verbose:
      print('label={}, expr={}, op={}'.format(label, expr, op))

    if label:
      if opt.verbose:
        print('inserting label [{}]'.format(label))
      labels[label] = pos

    if op==None: # empty or comments
      continue

    is_bra=op in ['BPL','BMI','BVC',
                  'BCC','BCS','BNE',
                  'BEQ']

    if opt.verbose:
      print('is_bra={}'.format(is_bra))

    argraw=m.group('argraw')
    if opt.verbose:
      print('argraw={}'.format(argraw))

    is_unary=True if argraw==None else len(argraw)==0 # no args

    if opt.verbose:
      print('is_unary={}'.format(is_unary))

    if is_unary: # no arguments
      encoding=opcodes[op][10] # sngl
      argbytes=0

    else: # 1 or more arguments
      is_imm=m.group('imm')=="#"
      is_hex=m.group('hex')=="$"
      arglab_str = m.group('arglab')
      argval_str = m.group('argval')
      if opt.verbose:
        print('is_imm={}, is_hex={}, '
        'arglab_str={}, argval_str={}'.format(
        is_imm, is_hex, arglab_str, argval_str))

      argval=int(argval_str, 16) if is_hex \
        else int(argval_str, 10) if is_imm \
        else labels[arglab_str]

      arglen=len(argval_str) if argval_str else 1
      if is_bra:
        encoding=opcodes[op][11]
        argbytes=1
        argval=(argval-pos-2)
      elif is_imm:
        encoding=opcodes[op][0] #imm
        argbytes=1
      else:
        if arglen<=2:
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

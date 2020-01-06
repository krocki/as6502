# -*- coding: utf-8 -*-
# author: krocki

import argparse
import re
from defs import *

def assemble(lines, opt):

  pattern = '^\s*(?P<expr>(?P<label>[a-z]*):|(?P<op>[a-zA-z]{3})(?P<args>.*?))?(?P<comment>;.*)?$'

  instr = {}
  labels = {}
  data = {}
  pc = opt.pc

  for i,l in enumerate(lines):
    m = re.search(pattern, l)
    if opt.verbose:
      print('\nline {}=[{}]'.format(i,l))

    if opt.verbose:
      print('labels={}'.format(labels))

    # syntax: expression = op (space arg)?
    expr=m.group('expr')        # entire expression
    op=m.group('op')            # op
    label=m.group('label')      # label
    args=m.group('args')        # args
    comment=m.group('comment')  # comment

    if opt.verbose:
      print(' label=[{}], expr=[{}], op=[{}], args=[{}], comm=[{}]'.format(
        label, expr, op, args, comment))

    if label:
      if opt.verbose:
        print('  * lab [{}] pc={:x}'.format(label, pc))
      labels[label] = ' $'+str(hex(pc))

    # is arg a label ?
    if args:
      args_str = args.strip()
      if args_str in labels:
        args = labels[args_str]
        if opt.verbose:
          print('  * args found as a label [{}] -> [{}]'.format(args_str, args))

    if op==None: # empty or comments
      continue

    else:
      encodings=list(filter(lambda y: y[1]!=None, [(i,e) for i,e in enumerate(opcodes[op.lower()])]))

      mode=None
      for m, e in encodings:
        p=re.search(modes[m][2], args)
        if p!=None:
          mode = modes[m]
          if mode[0] != 10:
            is_hex = p.group(1)
            rawval = p.group(2)

      if None==mode:
        print('uh-oh: could not find addressing mode')
        return None

      val=int(rawval, 16) if is_hex \
      else int(rawval, 10)

      argbytes=mode[3]
      encoding=opcodes[op][mode[0]]

      if opt.verbose:
        print('  * mode [{}], opcode [0x{:02x}], argbytes [{}] '.format(mode[1], encoding, argbytes))
        print('  * rawval [{}], ishex [{}], val [0x{:04x}] '.format(rawval, is_hex, val))

      if mode[1]=='rel':
         val=(val-pc-2)
      addr=pc
      s=[encoding]
      pc+=1
      for b in range(argbytes):
        data[pc] = (val >> (8*b)) & 0xff
        s.append(data[pc])
        pc+=1

      instr[addr] = {}
      instr[addr]['src'] = '{:20} {:3} {:10}'.format(expr, op, args)
      instr[addr]['obj'] = s
      if opt.verbose: print('  * assembled [{}]'.format(s))

  return instr, pc - opt.pc, labels

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
  parser.add_argument('-p',
     '--pc', type=hex, default=0x600, help='default entry point')

  opt = parser.parse_args()
  if opt.verbose: print(opt)

  ifile=opt.input
  ofile=opt.output

  with open(ifile, 'r') as fp:
    lines = fp.readlines()

  lines = [line.rstrip('\n') for line in lines]

  if opt.verbose:
    print('{:} read, {:} lines, assembling...'.format(ifile, len(lines)))

  instr, n_bytes, labels = assemble(lines, opt)

  if None==instr:
    print('Assembly failed!')
  else:
    if ofile:
      mem = [0] * n_bytes
      for k,i in enumerate(instr):
        for n in range(len(instr[i]['obj'])):
          mem[i - opt.pc + n] = instr[i]['obj'][n]
      with open(ofile, 'wb') as fp:
        fp.write(bytearray(mem))
    else:
      print('Assembled, {} Bytes'.format(n_bytes))
      print('labels', labels)
      for k,i in enumerate(instr):
        print('[{}] -> [0x{:04x}] {:}'.format(instr[i]['src'], i, ['0x{:02x}'.format(x) for x in instr[i]['obj']]))

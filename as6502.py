# -*- coding: utf-8 -*-
# author: krocki

import time
import argparse
import re
from defs import *

def encode(op, mode, rawval, is_hex, opt, pc):
  # a helper function which fills the instruction structure
  instr = {}
  val=None
  if rawval:
    val=int(rawval, 16) if is_hex \
    else int(rawval, 10)

  argbytes=mode[3]
  encoding=opcodes[op.lower()][mode[0]]

  if opt.verbose:
    print('  * mode [{}], opcode [0x{:02x}], argbytes [{}] '.format(
      mode[1], encoding, argbytes))
    print('  * rawval [{}], ishex [{}], val [{}] '.format(
      rawval, is_hex, val))

  if mode[1]=='rel':
     val=(val-pc-2)

  s=[encoding]
  for b in range(argbytes):
    s.append((val >> (8*b)) & 0xff)

  instr['src'] = '{} {}'.format(op, rawval)
  instr['obj'] = s

  return instr

def find_mode(op, args):
  # given an expression=(op, args)
  # determine an addressing mode or return None
  # if invalid syntax

  encodings=list(filter(lambda y: y[1]!=None,
  [(i,e) for i,e in enumerate(opcodes[op.lower()])]))

  mode=None
  is_hex=None
  rawval=None
  if args==None: args = ""

  for m, e in encodings:
    p=re.search(modes[m][2], args)
    if p!=None:
      found_mode = modes[m]
      if None==mode or found_mode[3] < mode[3]:
        mode = found_mode
      if mode[0] != 10:
        is_hex = p.group(1)
        rawval = p.group(2)

  return mode, is_hex, rawval

def assemble(lines, opt):

  # a regex which accepts lines
  # line = [label] [expr] [comment]
  # expr = OPC [args] - see defs.py for syntax
  # label = alphanum + ':'
  # comment = ';' + anything

  pattern = '^\s*(((?P<label>[A-Za-z0-9]+):)?' \
            '\s*(?P<expr>(?P<op>[a-zA-z]{3})' \
            '(\s+(?P<args>.*?))?)?)?' \
            '(?P<comment>;.*)?$'

  instr, labels, unresolved, data = {}, {}, {}, {}
  pc = opt.pc

  for i,l in enumerate(lines):
    m = re.search(pattern, l)
    if opt.verbose:
      print('\nline {}=[{}]'.format(i,l))

    if opt.verbose:
      print('labels={}'.format(labels))
      print('unresolved={}'.format(unresolved))

    # extract tokens
    expr=m.group('expr')        # entire expression
    op=m.group('op')            # op
    label=m.group('label')      # label
    args=m.group('args')        # args
    comment=m.group('comment')  # comment

    if opt.verbose:
      print(' label=[{}], expr=[{}], ' \
            'op=[{}], args=[{}], comm=[{}]'.format(
            label, expr, op, args, comment))

    # do we have a label?
    if label:
      # insert into our dictionary
      labels[label] = '${:04x}'.format(pc)
      if opt.verbose:
        print('  * lab [{}] pc={:x}'.format(label, pc))
      # have we tried to look it up before?
      if label in unresolved:
        f=unresolved[label]
        # patch the unresolved symbol
        pc0=f[0]
        op0=f[1]
        arg0=labels[label]
        mode0, is_hex0, rawval0 = find_mode(op0, arg0)
        instr[pc0] = encode(op0, mode0, rawval0, is_hex0, opt, pc0)
        # clear
        unresolved[label] = {}

    # is arg a label ?
    if args:
      args_str = args.strip()
      if args_str in labels:
        args = labels[args_str]
        if opt.verbose:
          print('  * args found as a label [{}] -> [{}]'.format(args_str, args))

    if op==None: # empty or comments
      continue

    # op present
    else:
      # determine the mode
      mode, is_hex, rawval = find_mode(op, args)
      if None==mode:
        # something went wrong, maybe it's a label
        # try passing 0 as arg
        mode, is_hex, rawval = find_mode(op, "$0")
        if None==mode:
          # still not working: FATAL
          print('uh-oh: could not find addressing mode')
          return None, None, None
        else:
          # 0 as arg worked, we need to patch it later
          unresolved[args.strip()] = [pc, op]

      instr[pc] = encode(op, mode, rawval, is_hex, opt, pc)
      pc+=len(instr[pc]['obj'])

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

  t0 = time.clock()
  instr, n_bytes, labels = assemble(lines, opt)
  t1 = time.clock()

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
      print('Assembled in {} s, {} Bytes'.format(t1-t0, n_bytes))
      print('labels', labels)
      for k,i in enumerate(instr):
        print('[{}] -> [0x{:04x}] {:}'.format(
          instr[i]['src'], i, ['0x{:02x}'.format(x) for x in instr[i]['obj']]))

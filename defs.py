modes = [
  [ 0, 'imm',  '^\s*#(\$?)([0-9a-f]{1,2})\s*$', 1 ],
  [ 1, 'zp',   '^\s*(\$?)0?0?([0-9a-f]{1,2})\s*$', 1 ],
  [ 2, 'zpx',  '^\s*(\$?)([0-9a-f]{1,2})\s*,\s*[xX]\s*$', 1 ],
  [ 3, 'zpy',  '^\s*(\$?)([0-9a-f]{1,2})\s*,\s*[yY]\s*$', 1 ],
  [ 4, 'abs',  '^\s*(\$?)(([1-9a-f][0-9a-f]|[0-9a-f][1-9a-f])[0-9a-f]{2})\s*$', 2 ],
  [ 5, 'absx', '^\s*(\$?)([0-9a-f]{3,4})\s*,\s*[xX]\s*$', 2 ],
  [ 6, 'absy', '^\s*(\$?)([0-9a-f]{3,4})\s*,\s*[yY]\s*$', 2 ],
  [ 7, 'ind',  '^\s*\((\$?)([0-9a-f]*)\)\s*$', 2 ],
  [ 8, 'indx', '^\s*\((\$?)([0-9a-f]{1,2}),\s*[xX]\)\s*$', 1 ],
  [ 9, 'indy', '^\s*\((\$?)([0-9a-f]{1,2})\s*\),\s*[yY]\s*$', 1 ],
  [10, 'impl', '^\s*$', 0 ],
  [11, 'rel',  '^\s*(\$?)([a-z0-9]*)\s*$', 1 ],
]

opcodes = {
  #Name,   IMM,   ZP,  ZPX,  ZPY,  ABS, ABSX, ABSY,  IND, INDX, INDY, IMPL, REL
  'adc': [0x69, 0x65, 0x75, None, 0x6d, 0x7d, 0x79, None, 0x61, 0x71, None, None],
  'and': [0x29, 0x25, 0x35, None, 0x2d, 0x3d, 0x39, None, 0x21, 0x31, None, None],
  'asl': [None, 0x06, 0x16, None, 0x0e, 0x1e, None, None, None, None, 0x0a, None],
  'bit': [None, 0x24, None, None, 0x2c, None, None, None, None, None, None, None],
  'bpl': [None, None, None, None, None, None, None, None, None, None, None, 0x10],
  'bmi': [None, None, None, None, None, None, None, None, None, None, None, 0x30],
  'bvc': [None, None, None, None, None, None, None, None, None, None, None, 0x50],
  'bvs': [None, None, None, None, None, None, None, None, None, None, None, 0x70],
  'bcc': [None, None, None, None, None, None, None, None, None, None, None, 0x90],
  'bcs': [None, None, None, None, None, None, None, None, None, None, None, 0xb0],
  'bne': [None, None, None, None, None, None, None, None, None, None, None, 0xd0],
  'beq': [None, None, None, None, None, None, None, None, None, None, None, 0xf0],
  'brk': [None, None, None, None, None, None, None, None, None, None, 0x00, None],
  'cmp': [0xc9, 0xc5, 0xd5, None, 0xcd, 0xdd, 0xd9, None, 0xc1, 0xd1, None, None],
  'cpx': [0xe0, 0xe4, None, None, 0xec, None, None, None, None, None, None, None],
  'cpy': [0xc0, 0xc4, None, None, 0xcc, None, None, None, None, None, None, None],
  'dec': [None, 0xc6, 0xd6, None, 0xce, 0xde, None, None, None, None, None, None],
  'eor': [0x49, 0x45, 0x55, None, 0x4d, 0x5d, 0x59, None, 0x41, 0x51, None, None],
  'clc': [None, None, None, None, None, None, None, None, None, None, 0x18, None],
  'sec': [None, None, None, None, None, None, None, None, None, None, 0x38, None],
  'cli': [None, None, None, None, None, None, None, None, None, None, 0x58, None],
  'sei': [None, None, None, None, None, None, None, None, None, None, 0x78, None],
  'clv': [None, None, None, None, None, None, None, None, None, None, 0xb8, None],
  'cld': [None, None, None, None, None, None, None, None, None, None, 0xd8, None],
  'sed': [None, None, None, None, None, None, None, None, None, None, 0xf8, None],
  'inc': [None, 0xe6, 0xf6, None, 0xee, 0xfe, None, None, None, None, None, None],
  'jmp': [None, None, None, None, 0x4c, None, None, 0x6c, None, None, None, None],
  'jsr': [None, None, None, None, 0x20, None, None, None, None, None, None, None],
  'lda': [0xa9, 0xa5, 0xb5, None, 0xad, 0xbd, 0xb9, None, 0xa1, 0xb1, None, None],
  'ldx': [0xa2, 0xa6, None, 0xb6, 0xae, None, 0xbe, None, None, None, None, None],
  'ldy': [0xa0, 0xa4, 0xb4, None, 0xac, 0xbc, None, None, None, None, None, None],
  'lsr': [None, 0x46, 0x56, None, 0x4e, 0x5e, None, None, None, None, 0x4a, None],
  'nop': [None, None, None, None, None, None, None, None, None, None, 0xea, None],
  'ora': [0x09, 0x05, 0x15, None, 0x0d, 0x1d, 0x19, None, 0x01, 0x11, None, None],
  'tax': [None, None, None, None, None, None, None, None, None, None, 0xaa, None],
  'txa': [None, None, None, None, None, None, None, None, None, None, 0x8a, None],
  'dex': [None, None, None, None, None, None, None, None, None, None, 0xca, None],
  'inx': [None, None, None, None, None, None, None, None, None, None, 0xe8, None],
  'tay': [None, None, None, None, None, None, None, None, None, None, 0xa8, None],
  'tya': [None, None, None, None, None, None, None, None, None, None, 0x98, None],
  'dey': [None, None, None, None, None, None, None, None, None, None, 0x88, None],
  'iny': [None, None, None, None, None, None, None, None, None, None, 0xc8, None],
  'ror': [None, 0x66, 0x76, None, 0x6e, 0x7e, None, None, None, None, 0x6a, None],
  'rol': [None, 0x26, 0x36, None, 0x2e, 0x3e, None, None, None, None, 0x2a, None],
  'rti': [None, None, None, None, None, None, None, None, None, None, 0x40, None],
  'rts': [None, None, None, None, None, None, None, None, None, None, 0x60, None],
  'sbc': [0xe9, 0xe5, 0xf5, None, 0xed, 0xfd, 0xf9, None, 0xe1, 0xf1, None, None],
  'sta': [None, 0x85, 0x95, None, 0x8d, 0x9d, 0x99, None, 0x81, 0x91, None, None],
  'txs': [None, None, None, None, None, None, None, None, None, None, 0x9a, None],
  'tsx': [None, None, None, None, None, None, None, None, None, None, 0xba, None],
  'pha': [None, None, None, None, None, None, None, None, None, None, 0x48, None],
  'pla': [None, None, None, None, None, None, None, None, None, None, 0x68, None],
  'php': [None, None, None, None, None, None, None, None, None, None, 0x08, None],
  'plp': [None, None, None, None, None, None, None, None, None, None, 0x28, None],
  'stx': [None, 0x86, None, 0x96, 0x8e, None, None, None, None, None, None, None],
  'sty': [None, 0x84, 0x94, None, 0x8c, None, None, None, None, None, None, None],
  '---': [None, None, None, None, None, None, None, None, None, None, None, None]
}

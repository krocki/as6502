# as6502
A basic assembler for 6502 cpu

## usage:
```
python3 as6502.py -c [input_file] [-o output_file]
```

### quick start

A short program which writes value of $08 in a loop to memory addresses starting with $200

```
; loop.a65

  LDX #$08
loop:
  DEX
  STX $0200
  CPX #$03
  BNE loop
  STX $0201
  
```

### Print to the console (without -o option)

```
$ python3 as6502.py -c loop.a65
```

```
Assembled, 13 Bytes
labels {'loop': '$0604'}
[LDX 3]    -> [0x0600] ['0xa2', '0x03']
[LDY 00]   -> [0x0602] ['0xa0', '0x00']
[TXA None] -> [0x0604] ['0x8a']
[STA 0200] -> [0x0605] ['0x99', '0x00', '0x02']
[INY None] -> [0x0608] ['0xc8']
[CPY 10]   -> [0x0609] ['0xc0', '0x10']
[BNE 604]  -> [0x060b] ['0xd0', '0xf7']
```

### Or write to a file (-o loop.bin)

```
$ python3 as6502.py -c loop.a65 -o loop.bin
$ xxd loop.bin
```

```
00000000: a203 a000 8a99 0002 c8c0 10d0 f7
```

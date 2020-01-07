# test reference binaries

```
./test.sh
```

# hexwrite.c
Use to make bin files from hex

```
gcc -c hexwrite.c -o hexwrite
```

example:

```
% gcc hexwrite.c -o hexwrite
% ./hexwrite a.ref a9 01 8d 00 02 a9 05 8d 01 02 a9 08 8d 02 02
wrote 15 bytes to a.ref
% xxd a.ref
00000000: a901 8d00 02a9 058d 0102 a908 8d02 02    ...............
```

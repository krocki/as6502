#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

int main(int argc, char **argv) {

  if (argc < 2) {
    fprintf(stderr, "usage: %s fname [vals]\n", argv[0]);
    return -2;
  }

  char *fname = argv[1];

  FILE *f = fopen(fname, "wb");
  if (!f) {
    fprintf(stderr, "couldn't open %s\n", fname);
    return -1;
  }

  int cnt=0;

  for (int i=2; i<argc; i++) {
    uint8_t val = strtol(argv[i], NULL, 16);
    cnt += sizeof(uint8_t);
    fwrite(&val, sizeof(uint8_t), 1, f);
  }

  printf("wrote %d bytes to %s\n", cnt, fname);
  fclose(f);

  return 0;
}

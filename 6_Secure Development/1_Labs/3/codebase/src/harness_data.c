#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../include/data_processing.h"

int main(int argc, char *argv[]) {
    if (argc < 2) { printf("Usage: %s <file>\n", argv[0]); return 1; }
    FILE *f = fopen(argv[1], "r");
    if (!f) { perror("fopen"); return 1; }
    char input[256];
    size_t n = fread(input, 1, sizeof(input) - 1, f);
    fclose(f);
    input[n] = '\0';
    data_processor(input);
    return 0;
}

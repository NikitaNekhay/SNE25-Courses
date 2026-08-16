#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../include/data_processing.h"

void data_processor(char *input) {
    int data[10];
    int index = atoi(input);
    data[index] = 42; // Potential out-of-bounds access
    printf("Data at index %d: %d\n", index, data[index]);
}

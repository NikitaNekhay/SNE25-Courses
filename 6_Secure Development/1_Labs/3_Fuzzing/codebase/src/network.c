#include <stdio.h>
#include <string.h>
#include "../include/network.h"

void network_handler(char *input) {
    char buffer[100];
    strcpy(buffer, input); // Potential buffer overflow
    printf("Network Handler: %s\n", buffer);
}

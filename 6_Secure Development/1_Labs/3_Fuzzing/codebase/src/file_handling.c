#include <stdio.h>
#include <stdlib.h>
#include "../include/file_handling.h"

void file_handler(char *input) {
    FILE *file = fopen(input, "r");
    if (file == NULL) {
        printf("File not found: %s\n", input);
        return;
    }
    char buffer[100];
    fgets(buffer, sizeof(buffer), file); // Potential file handling issue
    printf("File Content: %s\n", buffer);
    fclose(file);
}

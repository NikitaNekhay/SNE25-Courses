#include <stdio.h>
#include <string.h>
#include "../include/authentication.h"

void authenticate(char *input) {
    char password[10] = "secret";
    if (strcmp(input, password) == 0) {
        printf("Authentication successful!\n");
    } else {
        printf("Authentication failed!\n");
    }
}

#include <stdio.h>
#include <string.h>
#include <openssl/md5.h>
#include "../include/crypto.h"

void crypto_handler(char *input) {
    unsigned char digest[MD5_DIGEST_LENGTH];
    MD5((unsigned char*)input, strlen(input), digest); // Potential crypto misuse
    printf("MD5 Hash: ");
    for (int i = 0; i < MD5_DIGEST_LENGTH; i++) {
        printf("%02x", digest[i]);
    }
    printf("\n");
}

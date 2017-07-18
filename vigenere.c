#include <stdlib.h>
#include <cs50.h>
#include <stdio.h>
#include <string.h>
#include <ctype.h>

int main(int argc, string argv[])

{

    if (argc > 2)
        {
            printf("Please enter only a single keyword.\n");
            return 1;
        }
    if (argc < 2)
        {   
            printf("Please enter at least one keyword.\n");
            return 1;
        }
    else
        {
            string k = argv[1];
            for (int i=0, n=strlen(k); i<n; i++)
            {
                char c = k[i];
                if (!isalpha(c))
                {
                    printf("Please only enter alphabetic characters\n");
                    return 1;
                }
            }
        }
    printf("plaintext: ");
    string plaintext = get_string();
    string ciphertext = plaintext ;
    
    string k = argv[1];
    int klength = strlen(k); 
    
    
    for (int i=0, j=0, n=strlen(plaintext); i<n; i++)
        { 
            int kkey = toupper(k[j % klength]) - 65;
            char c = plaintext[i];
            if(isalpha(c))
                {
                    if(isupper(c))
                    {
                    ciphertext[i]=(((c - 65) + kkey) % 26) + 65;
                    j++;
                    //printf("%c - upper\n", kkey]);//
                    }
                    if(islower(c))
                    {
                    ciphertext[i]=(((c - 97) + kkey) % 26) + 97;
                    j++;
                    //printf("%c - lower\n", kkey);//
                    }
                }
        }
    printf("ciphertext: %s\n", ciphertext);
}

    
    
    
    
    
    
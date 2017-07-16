#include <stdlib.h>
#include <cs50.h>
#include <stdio.h>
#include <string.h>
#include <ctype.h>

int main(int argc, string argv[])

{
    string k = argv[1];
    int key = atoi(k);
    if (argc != 2)
    {
        printf("Please enter only one integer\n");
        return 1;
    }
    if (key < 0)
    {
        printf("Please enter a positive integer\n");
        return 1;
    }
    else
    {
        printf("plaintext: ");
        string s = get_string();
        printf("ciphertext: ");
        for (int i=0, n=strlen(s); i<n; i++)
            { 
                char c = s[i];
                if(isalpha(c))
                {
                    if(isupper(c))
                    {
                        char ciph = (((c - 65) + key) % 26) + 65;
                        printf("%c", ciph);  //calc// 
                    }
                    if(islower(c))
                    {
                        char ciph = (((c - 97) + key) % 26) + 97;
                        printf("%c", ciph);  //calc//  
                    }
                }
                else
                {
                    printf("%c",s[i]);  //don't calc//   
                }
            }
    }
    printf("\n");
    return(0);
}



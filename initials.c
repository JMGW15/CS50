#include <cs50.h>
#include <stdio.h>
#include <string.h>
#include <ctype.h>

int main(void)
{
    string s = get_string();
    printf("%c", toupper(s[0]));
    for (int j = 1, n = strlen(s); j < n; j++)
        {
            if (s[j] ==' ')
            {
                printf("%c", toupper(s[j+1]));
            }
        }
    printf("\n");
}

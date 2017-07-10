#include <cs50.h>
#include <stdio.h>
#include <math.h>

int main(void)
{
int coins = 0;
int cents = 0;
float cents_float;

do {
    printf("O hai! How much change is owed?\n");
    cents_float = get_float();
    }

while (cents_float < 0); 
cents = (int)round(cents_float*100);

while (cents >= 25)
    {
    coins = (coins + 1);
    cents = (cents - 25);
    }

while (cents >= 10)
    {
    coins = (coins + 1);
    cents = (cents - 10);
    }
    
while (cents >= 5)
    {
    coins = (coins + 1);
    cents = (cents - 5);
    }

while (cents >= 1)
    {
    coins = (coins + 1);
    cents = (cents - 1);
    }
    
printf("%d\n", coins);

}
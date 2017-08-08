/**
 * Implements a dictionary's functionality.
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <ctype.h>
#include <string.h>
#include "dictionary.h"

// maximum length for a word
// (e.g., pneumonoultramicroscopicsilicovolcanoconiosis)
#define LENGTH 45
typedef struct node //define node structure for dictionary, moved from .h for speed
{ 
    char word[LENGTH+1];
    struct node *next;
} 
node; 

//setting global variables
#define HASHSIZE 65536 //define hashtable, or set of 25 arrays, to capture linked lists per the first letter in the dictionary word
struct node* hashtable[HASHSIZE]; //create a hashtable with 26 buckets using node structure
int numwords = 0; //# of words loaded into hashtable - to be used in load and size functions
int hashindex = 0; //initialize hash index 

/**int hashfunction(const char *word) //https://cs50.stackexchange.com/questions/23951/is-this-hash-function-valid/23952// too slow!
{
    int hash_key = tolower(word[0] - 'a') % 26; 
    return hash_key; 
}
*/

int hashfunction(char* word) //https://www.reddit.com/r/cs50/comments/1x6vc8/pset6_trie_vs_hashtable/cf9nlkn/
{
    unsigned int hash_key = 0;
    for (int i=0, n=strlen(word); i<n; i++)
        hash_key = (hash_key << 2) ^ word[i];
    return hash_key % HASHSIZE;
}

/**
 * Returns true if word is in dictionary else false.
 */
bool check(const char *word)
{
    int checkwordlen = strlen(word); //store length of given word from speller c
    char lowerword[checkwordlen+1];//initialize an array storing the given word, indicating lower, as the lowercase values will be set next
    
    for(int i = 0;i < checkwordlen; i++) //for each character of each given word, look to see if it is upper case
        {   
        if(isupper(word[i])) //if the character is uppercase
            {
                lowerword[i] = tolower(word[i]); //set it to lowercase
            }
        else
            {
                lowerword[i] = word[i]; //else don't do anything, it's already lowercase or another character we don't care about
            }
        }
    
    lowerword[checkwordlen] = '\0';
    hashindex = hashfunction(lowerword); //store hash index of lower case word in a variable called hashindexlowerword
    node* current=hashtable[hashindex];
    while (current != NULL) //while the value of the temporary node is not null compare lower word with word
        {
            if (strcmp(lowerword, current->word) == 0) //it's here!
            {
                return true; //return true
            }
                current = current->next;
        }
    free(current);
    return false;
}

/**
 * Define hash function
 * Loads dictionary into memory. Returns true if successful else false.
 */


bool load(const char *dictionary)
{
    for (int i = 0; i < HASHSIZE; i++)
    {
        hashtable[i] = NULL; //may be unecessary after unload
    }
    char word[LENGTH + 1]; // initialize word and set length to max length + 1 for /n
    FILE *dict = fopen(dictionary, "r"); //open file dictionary
    
  
    if (dict == NULL)
    {
        fclose(dict); 
        fprintf(stderr, "Could not open file");
        return false;
    }
    
    while (fscanf(dict, "%s\n", word)!= EOF) // scan through the file, loading each word into the hash table
    {
        node* new_node = malloc(sizeof(node));// allocate memory for new word
        strcpy(new_node->word, word);// put word in the new node
        int hashindex = hashfunction(word);// hash the word to find what index of the array the word should go in

        if (hashtable[hashindex] == NULL)// if hashtable is empty at linked list of index hashindex  set the first node in the linked list to the new node and point the pnt to the next value (NULL)
        {
            hashtable[hashindex] = new_node;
            new_node->next = NULL;
            numwords++; //increase word count by 1
        }
        
        else // if hashtable is not empty at index, point the new node's pnt to the first node in the linked list, set the first node to the new_node
        {
            new_node->next = hashtable[hashindex]; 
            hashtable[hashindex] = new_node; 
            numwords++; //increase word count by 1
        }
    }    
    fclose(dict); //closing file
    return true; //we are done here, return true
}

/**
 * Returns number of words in dictionary if loaded else 0 if not yet loaded.
 */
unsigned int size(void)
{
    if (numwords > 0)
    {
        return numwords;
    }
    else
    {
        return 0;
    }
}

/**
 * Unloads dictionary from memory. Returns true if successful else false.
 */

bool unload(void)
{
    for (int i = 0; i < HASHSIZE;i++) //for each node in each linked list of the hashtable array
    {
        // check the table for a node at that index
        node* current = hashtable[i]; // set current node to first node in hashtable[index] array
        while (current != NULL) //while it's not null
        {
            node* new_node = current; //set the location of the new node the current node
            current = current->next; //set the current node to point at the next value
            free(new_node); //free the new_node
        }
    }
    return true;
}

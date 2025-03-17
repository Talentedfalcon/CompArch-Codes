#include <stdio.h>

#define SIZE 3

struct merge{
    int val;
    int key;
};

int main(){
    struct merge merged_array[SIZE];
    printf("%d\n",&(merged_array->val));
    printf("%d",&(merged_array->key));
    return 0;
}
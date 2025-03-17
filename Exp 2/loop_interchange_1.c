#include <stdio.h>

int main(){
    int x[5000][100];
    for (int i=0;i<5000;i++){
        for(int j=0;j<100;j++){
            x[i][j]=i;
        }
    }

    for (int j=0;j<100;j++){
        for (int i=0;i<5000;i++){
            x[i][j]*=2;
        }
    }
    return 0;
}
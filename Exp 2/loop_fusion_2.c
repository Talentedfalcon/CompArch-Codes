#include <stdio.h>

#define N 3

int main(){
    int a[N][N],b[N][N],c[N][N],d[N][N];

    for(int i=0;i<N;i++){
        for(int j=0;j<N;j++){
            b[i][j]=2;
            c[i][j]=3;
        }
    }

    for(int i=0;i<N;i++){
        for(int j=0;j<N;j++){
            a[i][j]=1/b[i][j]*c[i][j];
            d[i][j]=a[i][j]+c[i][j];
        }
    }

    return 0;
}
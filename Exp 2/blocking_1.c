#include <stdio.h>

#define N 2

int main(){
    int x[N][N],y[N][N],z[N][N];

    for(int i=0;i<N;i++){
        for(int j=0;j<N;j++){
            y[i][j]=2;
            z[i][j]=3;
        }
    }

    for(int i=0;i<N;i++){
        for(int j=0;j<N;j++){
            int r=0;
            for(int k=0;k<N;k++){
                r+=(y[i][k]*z[k][j]);
            }
            x[i][j]=r;
        }
    }

    return 0;
}
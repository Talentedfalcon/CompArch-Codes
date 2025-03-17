#include <stdio.h>

#define N 2

int min(int a,int b){
    if(a<b){
        return a;
    }
    return b;
}

int main(){
    int x[N][N],y[N][N],z[N][N];

    for(int i=0;i<N;i++){
        for(int j=0;j<N;j++){
            y[i][j]=2;
            z[i][j]=3;
        }
    }

    int B=1;

    for(int jj=0;jj<N;jj+=B){
        for(int kk=0;kk<N;kk+=B){
            for(int i=0;i<N;i+=1){
                for(int j=jj;j<min(jj+B,N);j++){
                    int r=0;
                    for(int k=kk;k<min(kk+B,N);k++){
                        r+=(y[i][k]*z[k][j]);
                    }
                    x[i][j]=x[i][j]+r;
                }
            }
        }
    }

    for(int i=0;i<N;i++){
        for(int j=0;j<N;j++){
            printf("%d ",x[i][j]);
        }
        printf("\n");
    }

    // for(int i=0;i<N;i++){
    //     for(int j=0;j<N;j++){
    //         int r=0;
    //         for(int k=0;k<N;k++){
    //             r+=(y[i][k]*z[k][j]);
    //         }
    //         x[i][j]=r;
    //     }
    // }

    return 0;
}
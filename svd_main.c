#include <stdio.h>
#include <stdlib.h>
extern int Singular_Value_Decomposition(double* A, int nrows, int ncols, double* U, 
                      double* singular_values, double* V, double* dummy_array);
int main() {
     #define M  10                                                            
     #define N  3                                                           
     double A[M][N];
     double A1[N][M] = 
    { {0.64724042, 0.35758181, 0.9512442,  1.29723368, 0.92860612, 0.65345024,
  0.80022358, 0.73112236, 1.0980026,  0.52053852},
 { 1.22940512, 1.66716644, 1.15930556, 1.22476976, 1.33246935, 1.42477522,
  1.5600748,  1.25985761, 1.22146866, 1.75895506},
 {0.37247002, 0.77672062, 0.49042198, 0.37532438, 1.37755089, 0.47549959,
  1.1263332,  0.23312056, 1.03766375, 0.87879653}}     ;                                                        
     double U[M][N];                                                        
     double V[N][N];                                                        
     double singular_values[N];                                             
     double* dummy_array;                                                   

     for (int i=0; i<M; i++) {
         for (int j=0; j<N; j++) {
            A[i][j] = A1[j][i];
         }
    }                                                                            
     dummy_array = (double*) malloc(N * sizeof(double));                    
     if (dummy_array == NULL) {printf(" No memory available\n"); exit(0); } 
                                                                            
     int err = Singular_Value_Decomposition((double*) A, M, N, (double*) U,     
                              singular_values, (double*) V, dummy_array);   
                                                                            
     free(dummy_array);                                                     
     if (err < 0) printf(" Failed to converge\n");                          
     else { printf(" The singular value decomposition of A is \n");  }
    printf("hi");
     for (int i=0; i<N; i++) {
         for (int j=0; j<N; j++) {
            printf("%f, ", V[i][j]);
         }
         printf("\n");
     }
    for (int i=0; i<N; i++) {
        printf("%f, ", singular_values[i]);        
    }
    return 0;
}

C FILE: HELLO.F
      SUBROUTINE FOO(A, B, N)
C
C     INCREMENT THE FIRST ROW AND DECREMENT THE FIRST COLUMN OF A
C
      INTEGER N,I
      REAL*8 A(N)
      REAL*8 B
      REAL*8 M
      M = MAX(A)
      DO I=1,N
         A(I) = ABS(A(I) - B)
         IF (A(I) < M) THEN
            M = A(I)
         END IF
      ENDDO
      END
      
C END OF FILE ARRAY.F

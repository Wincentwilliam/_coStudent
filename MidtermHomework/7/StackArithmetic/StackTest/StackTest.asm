// C_PUSH constant 17
@17
D=A
@SP
A=M
M=D
@SP
M=M+1
// C_PUSH constant 17
@17
D=A
@SP
A=M
M=D
@SP
M=M+1
// eq
@SP
AM=M-1
D=M
A=A-1
D=M-D
@LABEL_0_TRUE
D;JEQ
@SP
A=M-1
M=0
@LABEL_0_END
0;JMP
(LABEL_0_TRUE)
@SP
A=M-1
M=-1
(LABEL_0_END)
// C_PUSH constant 17
@17
D=A
@SP
A=M
M=D
@SP
M=M+1
// C_PUSH constant 16
@16
D=A
@SP
A=M
M=D
@SP
M=M+1
// eq
@SP
AM=M-1
D=M
A=A-1
D=M-D
@LABEL_1_TRUE
D;JEQ
@SP
A=M-1
M=0
@LABEL_1_END
0;JMP
(LABEL_1_TRUE)
@SP
A=M-1
M=-1
(LABEL_1_END)
// C_PUSH constant 16
@16
D=A
@SP
A=M
M=D
@SP
M=M+1
// C_PUSH constant 17
@17
D=A
@SP
A=M
M=D
@SP
M=M+1
// eq
@SP
AM=M-1
D=M
A=A-1
D=M-D
@LABEL_2_TRUE
D;JEQ
@SP
A=M-1
M=0
@LABEL_2_END
0;JMP
(LABEL_2_TRUE)
@SP
A=M-1
M=-1
(LABEL_2_END)
// C_PUSH constant 892
@892
D=A
@SP
A=M
M=D
@SP
M=M+1
// C_PUSH constant 891
@891
D=A
@SP
A=M
M=D
@SP
M=M+1
// lt
@SP
AM=M-1
D=M
A=A-1
D=M-D
@LABEL_3_TRUE
D;JLT
@SP
A=M-1
M=0
@LABEL_3_END
0;JMP
(LABEL_3_TRUE)
@SP
A=M-1
M=-1
(LABEL_3_END)
// C_PUSH constant 891
@891
D=A
@SP
A=M
M=D
@SP
M=M+1
// C_PUSH constant 892
@892
D=A
@SP
A=M
M=D
@SP
M=M+1
// lt
@SP
AM=M-1
D=M
A=A-1
D=M-D
@LABEL_4_TRUE
D;JLT
@SP
A=M-1
M=0
@LABEL_4_END
0;JMP
(LABEL_4_TRUE)
@SP
A=M-1
M=-1
(LABEL_4_END)
// C_PUSH constant 891
@891
D=A
@SP
A=M
M=D
@SP
M=M+1
// C_PUSH constant 891
@891
D=A
@SP
A=M
M=D
@SP
M=M+1
// lt
@SP
AM=M-1
D=M
A=A-1
D=M-D
@LABEL_5_TRUE
D;JLT
@SP
A=M-1
M=0
@LABEL_5_END
0;JMP
(LABEL_5_TRUE)
@SP
A=M-1
M=-1
(LABEL_5_END)
// C_PUSH constant 32767
@32767
D=A
@SP
A=M
M=D
@SP
M=M+1
// C_PUSH constant 32766
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1
// gt
@SP
AM=M-1
D=M
A=A-1
D=M-D
@LABEL_6_TRUE
D;JGT
@SP
A=M-1
M=0
@LABEL_6_END
0;JMP
(LABEL_6_TRUE)
@SP
A=M-1
M=-1
(LABEL_6_END)
// C_PUSH constant 32766
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1
// C_PUSH constant 32767
@32767
D=A
@SP
A=M
M=D
@SP
M=M+1
// gt
@SP
AM=M-1
D=M
A=A-1
D=M-D
@LABEL_7_TRUE
D;JGT
@SP
A=M-1
M=0
@LABEL_7_END
0;JMP
(LABEL_7_TRUE)
@SP
A=M-1
M=-1
(LABEL_7_END)
// C_PUSH constant 32766
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1
// C_PUSH constant 32766
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1
// gt
@SP
AM=M-1
D=M
A=A-1
D=M-D
@LABEL_8_TRUE
D;JGT
@SP
A=M-1
M=0
@LABEL_8_END
0;JMP
(LABEL_8_TRUE)
@SP
A=M-1
M=-1
(LABEL_8_END)
// C_PUSH constant 57
@57
D=A
@SP
A=M
M=D
@SP
M=M+1
// C_PUSH constant 31
@31
D=A
@SP
A=M
M=D
@SP
M=M+1
// C_PUSH constant 53
@53
D=A
@SP
A=M
M=D
@SP
M=M+1
// add
@SP
AM=M-1
D=M
A=A-1
M=D+M
// C_PUSH constant 112
@112
D=A
@SP
A=M
M=D
@SP
M=M+1
// sub
@SP
AM=M-1
D=M
A=A-1
M=M-D
// neg
@SP
A=M-1
M=-M
// and
@SP
AM=M-1
D=M
A=A-1
M=D&M
// C_PUSH constant 82
@82
D=A
@SP
A=M
M=D
@SP
M=M+1
// or
@SP
AM=M-1
D=M
A=A-1
M=D|M
// not
@SP
A=M-1
M=!M

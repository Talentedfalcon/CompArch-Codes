import numpy as np

'''
Functional Units:
    - Integer Addition/Subtraction (IADD Rdst, Rsrc1, Rsrc2)  -  6 CC
    - Integer Multiplication (IMUL Rdst, Rsrc1, Rsrc2)  -  12 CC
    - Floating point Addition/Subtraction (FADD Rdst, Rsrc1, Rsrc2)  -  18 CC
    - Floating point Multiplication (FADD Rdst, Rsrc1, Rsrc2)  -  30 CC
    - Load (LD Rdst, Mem) - 1 CC
    - Store (ST Mem, Rsrc) - 1 CC
    - Logic Unit (AND/OR/XOR Rdst, Rsrc1, Rsrc2)  -  1 CC
    - No Operation (NOP) 1CC
'''

class ExecutionUnit():
    def __init__(self,registers,bits):
        self.bits=bits
        self.registers=registers
        pass

    def IADD(self,Rsrc1,Rsrc2):
        return (Rsrc1['data']+Rsrc2['data'],6)
    
    def IMUL(self,Rsrc1,Rsrc2):
        return (Rsrc1['data']*Rsrc2['data'],12)
    
    def FADD(self,Rsrc1,Rsrc2):
        return (Rsrc1['data']+Rsrc2['data'],18)

    def FMUL(self,Rsrc1,Rsrc2):
        return (Rsrc1['data']*Rsrc2['data'],30)
    
    def LD(self,Mem):
        return (np.random.randint(0,(2**self.bits)),1)
    
    def ST(self,Rsrc):
        Rsrc['free']=True
        Rsrc['data']=0
        return (None,1)
    
    def AND(self,Rsrc1,Rsrc2):
        return (Rsrc1&Rsrc2,1)

    def OR(self,Rsrc1,Rsrc2):
        return (Rsrc1|Rsrc2,1)
     
    def XOR(self,Rsrc1,Rsrc2):
        return (Rsrc1^Rsrc2,1)

    def NOP(self):
        return (None,1)

class InstructionFetchUnit():
    def __init__(self):
        pass

    def fetch(self,instructions,pc):
        return instructions[pc]
    
class InstructionDecodeUnit():
    def __init__(self):
        pass

    def decode(self,instruction):
        for i in range(len(instruction[1])):
            if(instruction[1][i].startswith('R')):
                instruction[1][i]=int(instruction[1][i][1:])
        return instruction

class VLIWProcessor():
    def __init__(self,bits,num_registers):
        self.bits=bits
        self.num_registers=num_registers
        self.registers=[]
        #Initializing the registers
        for i in range(num_registers):
            self.registers.append({
                'free':True,
                'data':0,
            })
        self.instructions=[]
        self.IF=InstructionFetchUnit()
        self.ID=InstructionDecodeUnit()
        self.EX=ExecutionUnit(self.registers,bits)

    
    def get_instructions(self,filename):
        try:
            file=open(filename,'r')
            for i in file.read().upper().split('\n'):
                temp=[]
                for j in i.split(' '):
                    temp.append(j.split(','))
                self.instructions.append(temp)
        except:
            raise Exception("File not found")
        # print(self.instructions)

    def show_registers(self):
        for i,reg in enumerate(self.registers):
            print(f"R{i}:\t{reg}")

    def run_instructions(self,filename):
        self.get_instructions(filename)
        # self.show_registers()

        self.pc=0
        self.clock_cycles=0

        done=False

        while not done:
            instruction=self.IF.fetch(self.instructions,self.pc)
            # print(instruction)
            decoded=self.ID.decode(instruction)
            # print(decoded)
            self.EX.execute(decoded)
            
            break

        # while(self.pc<len(self.instructions)):
        #     #Instruction Fetch
        #     instruction=self.instructions[self.pc]
        #     print(instruction)
        #     #Instruction Decode

        #     #Execute

        #     #Memory

        #     #Write Back
        #     self.pc+=1


    def isRegFree(self,reg_num):
        return self.registers[reg_num]['free']
    

processor=VLIWProcessor(64,32)
processor.run_instructions('instr.txt')
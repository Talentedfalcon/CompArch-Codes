from time import sleep

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

class VLIWProcessor():
    def __init__(self,bits,num_registers):
        self.bits=bits
        self.num_registers=num_registers
        self.registers=[]
        #Initializing the registers
        for i in range(num_registers):
            self.registers.append({
                'Free':1,
                'Data':0,
            })
        self.instructions=[]
    
    def update_FU_status(self,Free,InstrNum,ClkRemaining,Completed):
        status={
            'Free':Free,
            'InstrNum':InstrNum,
            'ClkRemaining':ClkRemaining,
            'Completed':Completed
        }
        return status
    
    def reset_FU_status(self):
        status={'Free':1,'InstrNum':-1,'ClkRemaining':0,'Completed':1}
        return status
    
    def update_instruction_status(self,CurrentFU,NextFU,Executed,Processing):
        status={
            'Current FU':CurrentFU,
            'Next FU':NextFU,
            'Executed':Executed,
            'Processing':Processing
        }
        return status

    def get_instructions(self,filename):
        try:
            file=open(filename,'r')
            for i in file.read().upper().split('\n'):
                temp=[]
                for j in i.split(' '):
                    temp.append(j.split(','))
                if(len(i.split(' '))==1):
                    temp.append([' '])
                self.instructions.append(temp)
        except:
            raise Exception("File not found")
        # print(self.instructions)

    def show_registers(self):
        for i,reg in enumerate(self.registers):
            print(f"R{i}:\t{reg}")

    def run_instructions(self,filename):
        self.get_instructions(filename)

        instruction_status=[]
        for _ in range(len(self.instructions)):
            instruction_status.append({
                'Current FU':None,
                'Next FU':'IF',
                'Executed':0,
                'Processing':0
            })

        FU_status={
            'IF':{},
            'ID':{},
            'IADD':{},
            'IMUL':{},
            'FADD':{},
            'FMUL':{},
            'LD':{},
            'ST':{},
            'LU':{},
            'MEM':{},
            'WB':{},
        }

        for FU in FU_status:
            FU_status[FU]=self.reset_FU_status()

        cc_execution={
            'IADD':6,
            'IMUL':12,
            'FADD':18,
            'FMUL':30,
            'LD':1,
            'ST':1,
            'LU':1,
        }

        pc=-1
        clock_cycles=0

        instructions_completed=0

        print(self.instructions)

        while instructions_completed<len(self.instructions):
            #Write Back
            if(FU_status['MEM']['Completed'] and not FU_status['MEM']['Free']):
                if(FU_status['WB']['Free']):
                    instr_num=FU_status['MEM']['InstrNum']
                    FU_status['MEM']=self.reset_FU_status()

                    FU_status['WB']=self.update_FU_status(
                        Free=0,
                        InstrNum=instr_num,
                        ClkRemaining=1,
                        Completed=0
                    )

                    instruction_status[instr_num]=self.update_instruction_status(
                        CurrentFU='WB',
                        NextFU=None,
                        Executed=instruction_status[instr_num]['Executed'],
                        Processing=instruction_status[instr_num]['Processing']
                    )
                    
            #Memory
            if(FU_status['MEM']['Free']):
                for i in range(2,9):
                    execution_unit=list(FU_status)[i]
                    if(FU_status[execution_unit]['Completed'] and not FU_status[execution_unit]['Free']):
                        instr_num=FU_status[execution_unit]['InstrNum']
                        FU_status[execution_unit]=self.reset_FU_status()

                        FU_status['MEM']=self.update_FU_status(
                            Free=0,
                            InstrNum=instr_num,
                            ClkRemaining=1,
                            Completed=0
                        )

                        instruction_status[instr_num]=self.update_instruction_status(
                            CurrentFU='MEM',
                            NextFU='WB',
                            Executed=instruction_status[instr_num]['Executed'],
                            Processing=instruction_status[instr_num]['Processing']
                        )

                        break

            #Execution
            if(FU_status['ID']['Completed'] and not FU_status['ID']['Free']):
                execution_unit=self.instructions[FU_status['ID']['InstrNum']][0][0]
                if(execution_unit in ['AND','OR','XOR']):
                    execution_unit='LU'
                if(execution_unit=='NOP'):
                    instruction_status[FU_status['ID']['InstrNum']]=self.update_instruction_status(
                        CurrentFU=None,
                        NextFU=None,
                        Executed=1,
                        Processing=instruction_status[instr_num]['Processing']
                    )
                    instructions_completed+=1

                    FU_status['ID']=self.reset_FU_status()

                elif(FU_status[execution_unit]['Free']):
                    instr_num=FU_status['ID']['InstrNum']
                    FU_status['ID']=self.reset_FU_status()

                    FU_status[execution_unit]=self.update_FU_status(
                        Free=0,
                        InstrNum=instr_num,
                        ClkRemaining=cc_execution[execution_unit],
                        Completed=0
                    )

                    instruction_status[instr_num]=self.update_instruction_status(
                        CurrentFU=execution_unit,
                        NextFU='MEM',
                        Executed=instruction_status[instr_num]['Executed'],
                        Processing=instruction_status[instr_num]['Processing']
                    )

            #Decode
            if(FU_status['IF']['Completed'] and not FU_status['IF']['Free']):
                if(FU_status['ID']['Free']):
                    instr_num=FU_status['IF']['InstrNum']
                    FU_status['IF']=self.reset_FU_status()

                    FU_status['ID']=self.update_FU_status(
                        Free=0,
                        InstrNum=instr_num,
                        ClkRemaining=1,
                        Completed=0
                    )

                    instruction_status[instr_num]=self.update_instruction_status(
                        CurrentFU='ID',
                        NextFU=None if(self.instructions[FU_status['ID']['InstrNum']][0][0]=='NOP') else self.instructions[FU_status['ID']['InstrNum']][0][0],
                        Executed=instruction_status[instr_num]['Executed'],
                        Processing=instruction_status[instr_num]['Processing']
                    )

            #Instruction Fetch
            if(FU_status['IF']['Free']):
                pc+=1
                if(pc<len(self.instructions)):
                    FU_status['IF']=self.update_FU_status(
                        Free=0,
                        InstrNum=pc,
                        ClkRemaining=1,
                        Completed=0
                    )

                    instruction_status[pc]=self.update_instruction_status(
                        CurrentFU='IF',
                        NextFU='ID',
                        Executed=instruction_status[pc]['Executed'],
                        Processing=1
                    )

            self.printStatus(clock_cycles,instruction_status,FU_status,mode='pretty')

            #Checks and other processes
            for FU in FU_status.values():
                FU['ClkRemaining']=max(0,FU['ClkRemaining']-1)
                if(FU['ClkRemaining']==0):
                    FU['Completed']=1

            for instr in instruction_status:
                if(instr['Current FU']=="WB"):
                    if(FU_status[instr['Current FU']]['Completed']):
                        FU_status[instr['Current FU']]=self.reset_FU_status()
                        instr['Executed']=1
                        instr['Current FU']=None
                        instructions_completed+=1

            clock_cycles+=1
            sleep(0.5)
        
        self.printStatus(clock_cycles,instruction_status,FU_status,mode='pretty')

    def printStatus(self,clock_cycles,instruction_status,FU_status,mode='full'):
        if(mode=='full'):
            print('Cycle: ',clock_cycles)
            for i,instr in enumerate(instruction_status):
                print(f"{self.instructions[i][0][0]} {','.join(self.instructions[i][1])}:\t{instr}")
            print("\n")

            for FU in FU_status.keys():
                if(not FU_status[FU]['Free']):
                    print(f"{FU}:\t{FU_status[FU]}")
            print("\n\n")
        elif(mode=='pretty'):
            print('Cycle: ',clock_cycles)
            print("Instructions: ")
            for i,instr in enumerate(instruction_status):
                if(instr['Processing']):
                    executed=" " if (not instr['Executed']) else "✔"
                    print(f"\t[{executed}] {i}: {self.instructions[i][0][0]}\t{','.join(self.instructions[i][1])}")
            print("\n")

            print("Processor: ")
            for i,FU in enumerate(FU_status):
                if(i<=2 or i>=9):
                    if(not FU_status[FU]['Free']):
                        printGreen(f"\t{FU}",end="")
                    else:
                        print(f"\t{FU}",end="")
            print()
            for i,FU in enumerate(FU_status):
                if(i<=2 or i>=9):
                    instr_string=f"\t{FU_status[FU]['InstrNum']} ({FU_status[FU]['ClkRemaining']})"
                    if(FU_status[FU]['InstrNum']>=0):
                        printRed(instr_string,end="")
                    else:
                        print(instr_string,end="")
            print()
            for i,FU in enumerate(FU_status):
                if(i>2 and i<9):
                    if(not FU_status[FU]['Free']):
                        printGreen(f"\t\t\t{FU}")
                    else:
                        print(f"\t\t\t{FU}")
                    instr_string=f"\t\t\t{FU_status[FU]['InstrNum']} ({FU_status[FU]['ClkRemaining']})"
                    if(FU_status[FU]['InstrNum']>=0):
                        printRed(instr_string)
                    else:
                        print(instr_string)

            print("\n\n")
            
def printRed(text,end="\n"):
    print("\033[91m{}\033[00m".format(text),end=end)

def printGreen(text,end="\n"):
    print("\033[92m {}\033[00m".format(text),end=end)

processor=VLIWProcessor(64,32)
# processor.run_instructions('./instr1.txt')
# processor.run_instructions('./instr2.txt')
processor.run_instructions('./instr3.txt')
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


        instruction_status=[]
        for _ in range(len(self.instructions)):
            instruction_status.append({'Current FU':None,'Executed':0})

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
            FU_status[FU]={'Free':1,'InstrNum':-1,'ClkRemaining':0,'Completed':0}

        pc=-1
        clock_cycles=0
        done=False

        instructions_completed=0

        while instructions_completed<len(self.instructions):
            print('Cycle: ',clock_cycles)
            # if(FU_status['ID']['Completed']):
            #     if(FU_status['IADD']['Free']):



            #Decode
            if(FU_status['IF']['Completed']):
                if(FU_status['ID']['Free']):
                    FU_status['IF']['Free']=1
                    FU_status['ID']['InstrNum']=FU_status['IF']['InstrNum']
                    FU_status['ID']['Free']=0
                    FU_status['ID']['ClkRemaining']=1
                    FU_status['ID']['Completed']=0
                    instruction_status[FU_status['ID']['InstrNum']]['Current FU']='ID'

            #Instruction Fetch
            if(FU_status['IF']['Free']):
                pc+=1
                if(pc<len(self.instructions)):
                    FU_status['IF']['InstrNum']=pc
                    FU_status['IF']['Free']=0
                    FU_status['IF']['ClkRemaining']=1
                    FU_status['IF']['Completed']=0
                    instruction_status[FU_status['IF']['InstrNum']]['Current FU']='IF'

            for i in instruction_status:
                print(i)
            print("\n")
            for FU in FU_status.values():
                print(FU)

            for FU in FU_status.values():
                FU['ClkRemaining']=max(0,FU['ClkRemaining']-1)
                if(FU['ClkRemaining']==0):
                    FU['Completed']=1

            for instr in instruction_status:
                if(instr['Current FU']=="ID"):
                    if(FU_status[instr['Current FU']]['Completed']):
                        FU_status[instr['Current FU']]['Free']=1
                        instr['Executed']=1
                        instr['Current FU']=None
                        instructions_completed+=1
                # else:
                #     if(instr['Current FU']!=None and FU_status[instr['Current FU']]['Completed']):
                #         next_FU=list(FU_status.keys())[list(FU_status.keys()).index(instr['Current FU'])+1]
                #         if(FU_status[next_FU]['Free']):
                #             FU_status[instr['Current FU']]['Free']=1


            print('\n\n\n')
            clock_cycles+=1
            sleep(0.4)
        
        print('Cycle: ',clock_cycles)
        for i in instruction_status:
            print(i)
        for FU in FU_status.values():
            print(FU)

    def isRegFree(self,reg_num):
        return self.registers[reg_num]['free']
    

processor=VLIWProcessor(64,32)
processor.run_instructions('./instr.txt')
import numpy as np

class Memory():
    def __init__(self,block_size,word_size,num_words):
        self.block_size=block_size
        self.word_size=word_size
        self.num_words=num_words
        self.addr_size=int(np.ceil(np.log2(num_words)))
        self.mem=[]

    def display(self):
        print('Addr\tWords')
        for i in range(len(self.mem)):
            print(f"{hex(i)}\t",end='')
            print(f"{self.mem[i]['words']}")
            print()

    def info(self):
        print(f"Block Size: {self.block_size}")
        print(f"Word Size: {self.word_size}")
        print(f"Num Words: {self.num_words}")
        print(f"Address Size: {self.addr_size}")

class Main_Memory(Memory):
    def __init__(self, block_size, word_size, num_words):
        super().__init__(block_size, word_size, num_words)
        self.num_blocks=int(self.num_words/self.block_size)
        for i in range(self.num_blocks):
            self.mem.append(
                {
                    'words':[0 for j in range(block_size)]
                }
            )
    
    def initiate_mem(self,mem_file):
        file=open(mem_file,'r')
        content=np.array([i.split(' ') for i in file.read().split('\n')])
        file.close()
        for i in content:
            addr=int(i[0])
            block_num=int(np.floor(addr/self.block_size))
            word_num=int((addr)%self.block_size)
            self.mem[block_num]['words'][word_num]=str(i[1])

    def get_block(self,addr):
        block_index=int(addr/self.block_size)
        if(block_index>self.num_blocks):
            raise Exception ("Invalid Address")
        return self.mem[block_index]
    
class L2_Cache(Memory):
    def __init__(self, block_size, word_size, num_words,associativity):
        super().__init__(block_size, word_size, num_words)
        self.associativity=associativity
        self.num_blocks=int((self.num_words/self.block_size)/associativity)
        for i in range(self.num_blocks):
            self.mem.append(
                [{
                    'valid':0,
                    'dirty':0,
                    'lru':0,
                    'block_index':0,
                    'words':[0 for j in range(block_size)],
                } for j in range(associativity)]
            )

    def display(self,OnlyValid=False):
        print('Index\tValid\tDirty\tLRU\tBlock_Index\tWords')
        for i in range(self.num_blocks):
            for j in range(self.associativity):
                if(OnlyValid and self.mem[i][j]['valid']!=1):
                    continue
                if(j==0):
                    print(f"{i}",end='')
                current_block=self.mem[i][j]
                print(f"\t{current_block['valid']}\t{current_block['dirty']}\t{current_block['lru']}\t{current_block['block_index']}\t{current_block['words']}",end='')
                print()
            if(not OnlyValid):
                print()

class L1_Cache(Memory):
    def __init__(self, block_size, word_size, num_words):
        super().__init__(block_size, word_size, num_words)
        self.num_blocks=int(self.num_words/self.block_size)
        for i in range(self.num_blocks):
            self.mem.append(
                {
                    'valid':0,
                    'dirty':0,
                    'block_index':0,
                    'words':[0 for j in range(block_size)]
                }
            )

    def display(self):
        print('Index\tValid\tDirty\tBlock_Index\tWords')
        for i in range(self.num_blocks):
            current_block=self.mem[i]
            print(f"{i}\t{current_block['valid']}\t{current_block['dirty']}\t{current_block['block_index']}\t{current_block['words']}",end='')
            print()

class Small_Memory_Associative(Memory):
    def __init__(self, block_size, word_size, num_words):
        super().__init__(block_size, word_size, num_words)
        self.num_blocks=int(self.num_words/self.block_size)
        for i in range(self.num_blocks):
            self.mem.append(
                {
                    'valid':0,
                    'lru':0,
                    'tag':0,
                    'words':[0 for j in range(block_size)]
                }
            )
    def display(self):
        print("Index\tValid\tLRU\tTag\tWords")
        for i in range(len(self.mem)):
            print(f"{i}\t{self.mem[i]['valid']}\t{self.mem[i]['lru']}\t{self.mem[i]['tag']}\t{self.mem[i]['words']}")

class Small_Memory_FIFO(Memory):
    def __init__(self, block_size, word_size, num_words):
        super().__init__(block_size, word_size, num_words)
        self.pointer=0
        self.num_blocks=int(self.num_words/self.block_size)
        for i in range(self.num_blocks):
            self.mem.append(
                {
                    'valid':0,
                    'tag':0,
                    'words':[0 for j in range(block_size)]
                }
            )
    def display(self):
        print("Index\tValid\tTag\tWords")
        for i in range(len(self.mem)):
            print(f"{i}\t{self.mem[i]['valid']}\t{self.mem[i]['tag']}\t{self.mem[i]['words']}")

class Memory_System():
    def __init__(self,block_size,word_size,L1_size,L2_size,main_size,write_buffer_size,victim_size,prefetch_size):
        self.main=Main_Memory(block_size,word_size,main_size)
        self.L2=L2_Cache(block_size,word_size,L2_size,4)
        self.L1=L1_Cache(block_size,word_size,L1_size)
        self.write_buffer=Small_Memory_FIFO(block_size,word_size,write_buffer_size)
        self.victim=Small_Memory_Associative(block_size,word_size,victim_size)
        self.prefetch=Small_Memory_Associative(block_size,word_size,prefetch_size)
    
    def access_sequence(self,access_seq_file):
        file=open(access_seq_file,'r')
        self.sequence=[int(i) for i in file.read().split('\n')]
    
    def run_mem_access(self,mem_file,access_seq_file,write_chance=0,blocks_per_prefetch=1):
        self.main.initiate_mem(mem_file)
        self.access_sequence(access_seq_file)

        L1_searches=0
        L1_hits=0
        L1_misses=0
        L1_swaps=0

        wb_searches=0
        wb_hits=0
        wb_misses=0

        victim_searches=0
        victim_hits=0
        victim_misses=0
        
        prefetch_searches=0
        prefetch_hits=0
        prefetch_misses=0

        L2_searches=0
        L2_hits=0
        L2_misses=0
        L2_swaps=0
        
        main_searches=0

        total_writes=0
        for addr in self.sequence:
            isWrite=False
            print()
            block=int(addr/16)
            print(f"Fetching Block {block} ({hex(addr)}) [Address {addr} ({hex(addr)})]")
            
            r=np.random.random(1)
            if(r<write_chance):
                isWrite=True
                print(f"\tWrite = {isWrite}")
                total_writes+=1

            isL1ConflictMiss=False
            L1_block_num=block%self.L1.num_blocks
            L1_block_index=int(block/self.L1.num_blocks)
            L1_searches+=1
            if(self.L1.mem[L1_block_num]['valid']==1):
                if(self.L1.mem[L1_block_num]['block_index']==L1_block_index):
                    L1_offset=addr%self.L1.block_size
                    print(f"\tL1 CACHE HIT: Data {self.L1.mem[L1_block_num]['words'][L1_offset]}")
                    L1_hits+=1
                    if(isWrite):
                        self.writetoL1(L1_block_num,addr)
                    continue
                else:
                    isL1ConflictMiss=True
            L1_misses+=1

            if(isL1ConflictMiss):
                print(f"\tL1 CACHE MISS: Checking Write Buffer... (Confict Miss)")
            else:
                print(f"\tL1 CACHE MISS: Checking Write Buffer...")
            #If L1 Miss Look through Write Buffer
            isWriteBufferHit=False
            for i in range(self.write_buffer.num_blocks):
                wb_searches+=1
                if(self.write_buffer.mem[i]['valid']==1):
                    if(self.write_buffer.mem[i]['tag']==block):
                        self.write_buffer.mem[i]['valid']=0
                        words=self.write_buffer.mem[i]['words']
                        print(f"\tWrite Buffer HIT: Data {self.write_buffer.mem[i]['words'][addr%self.main.block_size]}")
                        isWriteBufferHit=True
                        L1_swaps+=self.replaceL1Cache(L1_block_num)
                        self.L1.mem[L1_block_num]['valid']=1
                        self.L1.mem[L1_block_num]['dirty']=1
                        self.L1.mem[L1_block_num]['block_index']=L1_block_index
                        self.L1.mem[L1_block_num]['words']=words
                        if(isWrite):
                            self.writetoL1(L1_block_num,addr)
                        wb_hits+=1
                        break
            if(isWriteBufferHit):
                continue
            
            if(isL1ConflictMiss):
                print(f"\tWrite Buffer MISS: Checking Victim CACHE...")
            else:
                print(f"\tWrite Buffer MISS: Checking Prefetch CACHE...")

            wb_misses+=1

            #If Write Buffer Look through Victim Cache
            if(isL1ConflictMiss):
                isVictimHit=False
                for i in range(self.victim.num_blocks):
                    victim_searches+=1
                    if(self.victim.mem[i]['valid']==1):
                        if(self.victim.mem[i]['tag']==block):
                            print(f"\tVictim CACHE HIT: Data {self.victim.mem[i]['words'][addr%self.main.block_size]}")
                            isVictimHit=True
                            self.victim.mem[i]['valid']=0
                            L1_swaps+=self.replaceL1Cache(L1_block_num)
                            self.L1.mem[L1_block_num]['valid']=1
                            self.L1.mem[L1_block_num]['block_index']=L1_block_index
                            self.L1.mem[L1_block_num]['words']=self.main.mem[block]['words']
                            if(isWrite):
                                self.writetoL1(L1_block_num,addr)
                            victim_hits+=1
                            break
                if(isVictimHit):
                    continue

                print(f"\tVictim CACHE MISS: Checking Prefetch Cache...")
                victim_misses+=1

            #If Victim Cache miss then looking through Prefetch Cache
            isPrefetchHit=False
            for i in range(self.prefetch.num_blocks):
                if(self.prefetch.mem[i]['valid']==1):
                    prefetch_searches+=1
                    if(self.prefetch.mem[i]['tag']==block):
                        print(f"\tPrefetch Cache HIT: Data {self.prefetch.mem[i]['words'][addr%16]}")
                        isPrefetchHit=True
                        self.prefetch.mem[i]['lru']=0
                        for j in range(self.prefetch.num_blocks):
                            if(self.prefetch.mem[j]['valid']==1):
                                self.prefetch.mem[j]['lru']+=1
                        L1_swaps+=self.replaceL1Cache(L1_block_num)
                        self.L1.mem[L1_block_num]['valid']=1
                        self.L1.mem[L1_block_num]['block_index']=L1_block_index
                        self.L1.mem[L1_block_num]['words']=self.main.mem[block]['words']
                        if(isWrite):
                            self.writetoL1(L1_block_num,addr)
                        prefetch_hits+=1
                        self.prefetch.mem[i]['valid']=0
                        break
            if(isPrefetchHit):
                continue

            print(f"\tPrefetch Cache MISS: Checking L2 CACHE...")
            prefetch_misses+=1

            #If Prefetch Cache miss then looking through L2 Cache
            L2_block_num=block%self.L2.num_blocks
            L2_block=self.L2.mem[L2_block_num]
            L2_block_index=int(block/self.L2.num_blocks)
            isL2hit=False
            for i in range(self.L2.associativity):
                L2_searches+=1
                if(L2_block[i]['valid']==1):
                    if(L2_block[i]['block_index']==L2_block_index):
                        L2_offset=addr%self.L2.block_size
                        print(f"\tL2 CACHE HIT: Data {L2_block[i]['words'][L2_offset]}")
                        L2_hits+=1
                        isL2hit=True
                        L2_block[i]['lru']=0
                        for j in range(self.L2.associativity):
                            if(L2_block[j]['valid']==1):
                                L2_block[j]['lru']+=1

                        L1_swaps+=self.replaceL1Cache(L1_block_num)
                        self.L1.mem[L1_block_num]['valid']=1
                        self.L1.mem[L1_block_num]['block_index']=L1_block_index
                        self.L1.mem[L1_block_num]['words']=L2_block[i]['words']
                        if(isWrite):
                            self.writetoL1(L1_block_num,addr)
                        break
            if(isL2hit):
                continue

            #If L2 miss then looking through Main Memory
            else:
                L2_misses+=1
                print(f"\tL2 CACHE MISS: Checking Main Memory...")
                main_searches+=1
                main_block=self.main.get_block(addr)
                print(f"\tMain Memory HIT: Data {main_block['words'][addr%16]}")
                #Fetching to the L2 Cache
                L2EmptyFound=False
                L2_replacement_block=-1
                for i in range(self.L2.associativity):
                    maxLRU=L2_block[0]['lru']
                    maxLRUBlock=0
                    if(L2_block[i]['valid']==0):
                        L2EmptyFound=True
                        L2_replacement_block=i
                        break
                    if(L2_block[i]['lru']>maxLRU):
                        maxLRU=L2_block[i]['lru']
                        maxLRUBlock=i
                #Replacing L2 Cache Block if there is a conflict
                if(not L2EmptyFound):
                    L2_swaps+=1
                    L2_replacement_block=maxLRUBlock
                    print(f"\tL2 CACHE Conflict: Replacing block {L2_block[L2_replacement_block]['block_index']*self.L2.num_blocks+L2_block_num} [L2 Block Number={L2_block_num}]")
                L2_block[L2_replacement_block]['valid']=1
                L2_block[L2_replacement_block]['lru']=0
                L2_block[L2_replacement_block]['block_index']=L2_block_index
                L2_block[L2_replacement_block]['words']=main_block['words']
                for i in range(self.L2.associativity):
                    if(L2_block[i]['valid']==1):
                        L2_block[i]['lru']+=1

                #Fetching the adjacent blocks to the Prefetch Cache
                for i in range(1,blocks_per_prefetch+1):
                    next_block=self.main.get_block(((block+i)*16)%self.main.num_words)
                    print(f"\tFetching block {(block+i)%self.main.num_blocks} ({hex((block+i)%self.main.num_blocks)}) into Prefetch Cache...")
                    self.place_in_PrefetchCache(block,next_block,block_offset=i)

                #Fetching to the L1 Cache
                #Replacing L1 Cache Block if there is a conflict
                L1_swaps+=self.replaceL1Cache(L1_block_num)
                self.L1.mem[L1_block_num]['valid']=1
                self.L1.mem[L1_block_num]['block_index']=L1_block_index
                self.L1.mem[L1_block_num]['words']=L2_block[L2_replacement_block]['words']
                if(isWrite):
                    self.writetoL1(L1_block_num,addr)
                continue

        for i in range(self.write_buffer.num_blocks):
            if(i==0):
                print("\nEmptying Write Buffer...")
            if(self.write_buffer.mem[i]['valid']==1):
                dirty_block=self.write_buffer.mem[i]['tag']
                print(f"\tWriting back block {dirty_block}")
                self.writeBack(dirty_block,i)

        #Printing out the stats
        print()
        print("L1:")
        print(f"\tSearches: {L1_searches}")
        print(f"\tHits: {L1_hits}")
        print(f"\tMisses: {L1_misses}")
        print(f"\tSwaps: {L1_swaps}")
        print()
        print("Write Buffer:")
        print(f"\tSearches: {wb_searches}")
        print(f"\tHits: {wb_hits}")
        print(f"\tMisses: {wb_misses}")
        print()
        print("Victim:")
        print(f"\tSearches: {victim_searches}")
        print(f"\tHits: {victim_hits}")
        print(f"\tMisses: {victim_misses}")
        print()
        print("Prefetch Cache:")
        print(f"\tSearches: {prefetch_searches}")
        print(f"\tHits: {prefetch_hits}")
        print(f"\tMisses: {prefetch_misses}")
        print()
        print("L2:")
        print(f"\tSearches: {L2_searches}")
        print(f"\tHits: {L2_hits}")
        print(f"\tMisses: {L2_misses}")
        print(f"\tSwaps: {L2_swaps}")
        print()
        print("Main Memory:")
        print(f"\tSearches: {main_searches}")
        print()
        print(f"Total Writes = {total_writes}")
        print()

    #L1 Block Replacement function return 1 if there is a swap
    def replaceL1Cache(self,L1_block_num):
        #Replacing Block from L1 Cache if there is a conflict
        if(self.L1.mem[L1_block_num]['valid']==1):
            #If block is a dirty then send it to the Write Buffer rather than the Victim Cache
            print(f"\tL1 CACHE Conflict: Replacing block {self.L1.mem[L1_block_num]['block_index']*self.L1.num_blocks+L1_block_num} [L1 Block Number={L1_block_num}]")
            if(self.L1.mem[L1_block_num]['dirty']==1):
                print(f"\tDIRTY: Block {self.L1.mem[L1_block_num]['block_index']*self.L1.num_blocks+L1_block_num}")
                print("\tSending Block to Write Buffer...")
                self.place_in_WriteBuffer(L1_block_num,self.L1.mem[L1_block_num]['block_index']*self.L1.num_blocks+L1_block_num)
                self.L1.mem[L1_block_num]['dirty']=0
            else:
                #Adding victim block to the Victim Cache
                print(f"\tSending victim block to Victim Cache...")
                self.place_in_VictimCache(L1_block_num,self.L1.mem[L1_block_num]['block_index']*self.L1.num_blocks+L1_block_num)
            return 1
        return 0

    def place_in_WriteBuffer(self,L1_block_num,block):
        wb_mem=self.write_buffer.mem
        wb_index=self.write_buffer.pointer
        #Checking if block already in the Write Buffer
        for i in range(self.write_buffer.num_blocks):
            if(wb_mem[i]['tag']==block and wb_mem[i]['valid']==1):
                print(f"\tBlock {block}({hex(block)}) already in Write Buffer...")
                print(f"\t\tUpdating block data...")
                wb_mem[i]['words']=self.L1.mem[L1_block_num]['words']
                return
        
        dirty_block=wb_mem[wb_index]['tag']
        if(wb_mem[wb_index]['valid']==1):
            print(f"\tWrite Buffer at Capacity: Writing back block {dirty_block}")
            #Initiate Memory Writeback
            self.writeBack(dirty_block,wb_index)
        wb_mem[wb_index]['valid']=1
        wb_mem[wb_index]['tag']=block
        wb_mem[wb_index]['words']=self.L1.mem[L1_block_num]['words']
        #Increment the pointer
        self.write_buffer.pointer=(self.write_buffer.pointer+1)%self.write_buffer.num_blocks        

    def writeBack(self,dirty_block,wb_index):
        #Writeback to Victim Cache
        for i in range(self.victim.num_blocks):
            if(self.victim.mem[i]['tag']==dirty_block):
                print("\t\tWriting to Victim Cache")
                self.victim.mem[i]['words']=self.write_buffer.mem[wb_index]['words']
                break

        #Writeback to Prefetch
        for i in range(self.prefetch.num_blocks):
            if(self.prefetch.mem[i]['tag']==dirty_block):
                print("\t\tWriting to Prefetch Cache")
                self.prefetch.mem[i]['words']=self.write_buffer.mem[wb_index]['words']
                break

        #Writeback to L2 Cache
        L2_block=self.L2.mem[int(dirty_block/self.L2.num_blocks)]
        for i in range(self.L2.associativity):
            if((L2_block[i]['block_index']*self.L2.num_blocks)+(dirty_block%self.L2.num_blocks)==dirty_block):
                print("\t\tWriting to L2 Cache")
                L2_block[i]['words']=self.write_buffer.mem[wb_index]['words']
                break

        #Writeback to Main Memory
        print("\t\tWriting to Main Memory")
        self.main.mem[dirty_block]['words']=self.write_buffer.mem[wb_index]['words']

        self.write_buffer.mem[wb_index]['valid']=0


    def place_in_VictimCache(self,L1_block_num,block):
        victim_mem=self.victim.mem
        #Checking if block already in the victim cache
        for i in range(self.victim.num_blocks):
            if(victim_mem[i]['tag']==block and victim_mem[i]['valid']==1):
                print(f"\tBlock {block}({hex(block)}) already in Victim Cache...")
                return
        #Checking for empty blocks in victim cache
        VictimEmptyFound=False
        victim_replacement_block=0
        maxLRU=victim_mem[0]['lru']
        maxLRUBlock=0
        for i in range(self.victim.num_blocks):
            if(victim_mem[i]['valid']==0):
                VictimEmptyFound=True
                victim_replacement_block=i
                break
            if(victim_mem[i]['lru']>maxLRU):
                maxLRU=victim_mem[i]['lru']
                maxLRUBlock=i
            #If Victim Cache at capacity then replaced based on LRU
            if(i==self.victim.num_blocks-1 and not VictimEmptyFound):
                victim_replacement_block=maxLRUBlock
                print(f"\tVictim CACHE at Capacity: Replacing block {self.victim.mem[victim_replacement_block]['tag']}")
        victim_mem[victim_replacement_block]['valid']=1
        victim_mem[victim_replacement_block]['lru']=0
        victim_mem[victim_replacement_block]['tag']=self.L1.mem[L1_block_num]['block_index']*self.L1.num_blocks+L1_block_num
        victim_mem[victim_replacement_block]['words']=self.L1.mem[L1_block_num]['words']
        for j in range(self.victim.num_blocks):
            if(victim_mem[j]['valid']==1):
                victim_mem[j]['lru']+=1

    def place_in_PrefetchCache(self,block,next_block,block_offset=1):
        #Checking if block already in the Prefetch Cache
        for i in range(self.prefetch.num_blocks):
            if(self.prefetch.mem[i]['tag']==block and self.prefetch.mem[i]['valid']==1):
                print(f"\tBlock {block}({hex(block)}) already in Prefetch Cache...")
                return
        
        PrefetchEmptyFound=False
        Prefetch_replacement_block=0
        maxLRU=self.prefetch.mem[0]['lru']
        maxLRUBlock=0
        for i in range(self.prefetch.num_blocks):
            if(self.prefetch.mem[i]['valid']==0):
                PrefetchEmptyFound=True
                Prefetch_replacement_block=i
                break
            if(self.prefetch.mem[i]['lru']>maxLRU):
                maxLRU=self.prefetch.mem[i]['lru']
                maxLRUBlock=i
        #If Prefetch Cache is at capacity then replace a block
        if(not PrefetchEmptyFound):
            Prefetch_replacement_block=maxLRUBlock
            print(f"\tPrefetch Cache at Capacity: Replacing block {self.prefetch.mem[Prefetch_replacement_block]['tag']}")
        self.prefetch.mem[Prefetch_replacement_block]['valid']=1
        self.prefetch.mem[Prefetch_replacement_block]['lru']=0
        self.prefetch.mem[Prefetch_replacement_block]['tag']=(block+block_offset)%self.main.num_blocks
        self.prefetch.mem[Prefetch_replacement_block]['words']=next_block['words']
        for i in range(self.prefetch.num_blocks):
            if(self.prefetch.mem[i]['valid']==1):
                self.prefetch.mem[i]['lru']+=1

    def writetoL1(self,L1_block_num,addr):
        self.L1.mem[L1_block_num]['dirty']=1
        self.L1.mem[L1_block_num]['words'][addr%16]=str(hex(np.random.randint(0,2**self.main.word_size,dtype='uint64')))
        print(f"\tData Updated to {self.L1.mem[L1_block_num]['words'][addr%16]}")

    def display(self):
        print("L1 Cache:")
        self.L1.display()
        print("L2 Cache:")
        self.L2.display()
        print("Main Memory:")
        self.main.display()
        print("Write Buffer:")
        self.write_buffer.display()
        print("Victim Cache:")
        self.victim.display()
        print("Prefetch Cache:")
        self.prefetch.display()
    def info(self):
        pass

def generate_main_memory(main_mem,filename):
    word_size=main_mem.word_size
    num_words=main_mem.num_words
    file=open(filename,'w')
    for i in range(num_words):
        data=np.random.randint(0,2**word_size,dtype='uint64')
        if(i==num_words-1):
            file.write(f"{i} {hex(data)}")
        else:
            file.write(f"{i} {hex(data)}\n")
    file.close()

def generate_access_sequence(main_mem,len_seq,filename):
    num_words=main_mem.num_words
    file=open(filename,'w')
    for i in range(len_seq):
        addr=np.random.randint(0,num_words)
        if(i==len_seq-1):
            file.write(f"{addr}")
        else:
            file.write(f"{addr}\n")

'''
Note:
    mem.txt contains {memory_address  data} pairs
    access_seq_.txt contains the order in which memory address is accessed 
    By default all undefined main memory location values are set to 0
    Multiple run_mem_access can be done one after the other but the cache and main memory will keep it's previous value
'''

mem=Memory_System(
    block_size=16,
    word_size=64,
    L1_size=2000,
    L2_size=16000,
    main_size=64000,
    write_buffer_size=64,
    victim_size=64,
    prefetch_size=128,
)

generate_main_memory(mem.main,'mem.txt')
# generate_access_sequence(mem.main,80000,'access_seq.txt')

mem.run_mem_access('mem.txt','access_seq1.txt',write_chance=0.2,blocks_per_prefetch=2)
'''
Total Access Sequences = 20
Access Sequence File = cache_replacement_test.txt

L1:
        Searches: 20
        Hits: 8
        Misses: 12
        Swaps: 8

Write Buffer:
        Searches: 42
        Hits: 3
        Misses: 9

Victim:
        Searches: 33
        Hits: 1
        Misses: 8

Prefetch Cache:
        Searches: 22
        Hits: 2
        Misses: 6

L2:
        Searches: 24
        Hits: 0
        Misses: 6
        Swaps: 1

Main Memory:
        Searches: 6

Total Writes = 7
Total Searches = 147
'''



# mem.run_mem_access('mem.txt','access_seq_rand.txt',write_chance=0.2,blocks_per_prefetch=2)
'''
Total Access Sequence = 80000
Access Sequence File = access_seq_rand.txt

L1:
        Searches: 80000
        Hits: 2443
        Misses: 77557
        Swaps: 77432

Write Buffer:
        Searches: 310115
        Hits: 81
        Misses: 77476

Victim:
        Searches: 309801
        Hits: 74
        Misses: 77402

Prefetch Cache:
        Searches: 618420
        Hits: 158
        Misses: 77244

L2:
        Searches: 283135
        Hits: 17094
        Misses: 60150
        Swaps: 59150

Main Memory:
        Searches: 60150

Total Writes = 16195
Total Searches = 1661621
'''
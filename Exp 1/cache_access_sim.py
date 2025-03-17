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

class Cache(Memory):
    def __init__(self, block_size, word_size, words_in_cache):
        super().__init__(block_size, word_size, words_in_cache)
        for i in range(int(self.num_words/self.block_size)):
            self.mem.append(
                {
                    'valid':0,
                    'lru':0,
                    'tags':[0 for j in range(block_size)],
                    'words':[0 for j in range(block_size)]
                }
            )
    
    def display(self,OnlyValid=False):
        print('Addr\tValid\tLRU\tTags\tWords')
        for i in range(len(self.mem)):
            if(not(OnlyValid and self.mem[i]['valid']==1)):
                continue
            print(f"{hex(i)}\t{self.mem[i]['valid']}\t{self.mem[i]['lru']}\t",end='')
            print(f"{self.mem[i]['tags']}\t",end='')
            print(f"{self.mem[i]['words']}")
            print()

    def access_sequence(self,access_seq_file):
        file=open(access_seq_file,'r')
        self.sequence=[int(i) for i in file.read().split('\n')]

class Main_Mem(Memory):
    def __init__(self, block_size, word_size, words_in_main):
        super().__init__(block_size, word_size, words_in_main)
        for i in range(int(self.num_words/self.block_size)):
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
            self.mem[block_num]['valid']=1
            self.mem[block_num]['words'][word_num]=str(i[1])

class Memory_System():
    def __init__(self,block_size,word_size,words_in_main,words_in_cache):
        self.cache=Cache(block_size,word_size,words_in_cache)
        self.main_mem=Main_Mem(block_size,word_size,words_in_main)

    def run_mem_access(self,mem_file,access_seq_file):
        self.main_mem.initiate_mem(mem_file)
        self.cache.access_sequence(access_seq_file)

        cache_search=0
        cache_miss=0
        cache_hit=0
        cache_discard=0


        cache_store_position=0
        for addr in self.cache.sequence:
            hit=0
            for block in self.cache.mem:
                cache_search+=1
                if(block['valid']==1):
                    index=addr-block['tags'][0]
                    if(index>=0 and index<16):
                        tag=block['tags'][index]
                        print(f"Cache HIT: Accessing {tag}({hex(tag)}) with Data {block['words'][index]}")
                        hit=1
                        cache_hit+=1
                        if(block['lru']!=1):
                            block['lru']=0
                            for b in self.cache.mem:
                                if(b['valid']==1):
                                    b['lru']+=1
                        break

            if(not hit):
                cache_miss+=1
                block_num=int(addr/self.main_mem.block_size)
                print(f"Cache MISS: while accessing Word:{addr}({hex(addr)})")

                #Accessing from main memory and storing in cache

                #If the current position is already valid then perform LRU replacement
                if(self.cache.mem[cache_store_position]['valid']==1):
                    cache_discard+=1
                    replace_index_lru=-1
                    replace_index=-1
                    for index,block in enumerate(self.cache.mem):
                        if(replace_index_lru<block['lru']):
                            replace_index_lru=block['lru']
                            replace_index=index
                    print(f"Cache REPLACEMENT: Block:{replace_index}({hex(replace_index)}) with Block:{block_num}({hex(block_num)})")
                    cache_store_position=replace_index                

                tags=[]
                for word_index,_ in enumerate(self.main_mem.mem[block_num]['words']):
                    tags.append((block_num*16)+word_index)

                self.cache.mem[cache_store_position]['lru']=0
                self.cache.mem[cache_store_position]['valid']=1
                self.cache.mem[cache_store_position]['tags']=tags
                self.cache.mem[cache_store_position]['words']=self.main_mem.mem[block_num]['words']
                for block in self.cache.mem:
                    if(block['valid']==1):
                        block['lru']+=1

                cache_store_position=(cache_store_position+1)%(int(self.cache.num_words/self.cache.block_size))
    
        print("\nCache Status:")
        self.cache.display(OnlyValid=True)
        
        print("\nInfo:")
        print(f"\tCache Searches: {cache_search}")
        print(f"\tCache Hits: {cache_hit}")
        print(f"\tCache Misses: {cache_miss}")
        print(f"\tCache Discards: {cache_discard}\n")

        print(f"\tMain Memory Searches: {cache_miss}\n")

    def display(self):
        print("Cache:")
        self.cache.display()
        print("Main Memory:")
        self.main_mem.display()

    def info(self):
        print("Cache:")
        self.cache.info()
        print("Main Memory:")
        self.main_mem.info()

def generate_main_memory(main_mem,filename):
    word_size=main_mem.word_size
    num_words=main_mem.num_words
    file=open(filename,'w')
    for i in range(num_words):
        data=np.random.randint(0,2**word_size,dtype='int64')
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

mem=Memory_System(16,32,64000,2000)


'''Fill all the main memory addresses with random data'''
# generate_main_memory(mem.main_mem,'mem.txt')

'''Spatial Data Access'''
# mem.run_mem_access('mem.txt','access_seq1.txt')

'''Temporal Data Access'''
# mem.run_mem_access('mem.txt','access_seq2.txt')

'''Random Data Access'''
'''Generate a random memory access sequence'''
# generate_access_sequence(mem.main_mem,2000,'access_seq_rand.txt')
# mem.run_mem_access('mem.txt','access_seq_rand.txt')
'''
    Total Access Sequence = 80000
    Access Sequence File = access_seq_rand.txt

    Cache Searches: 9847167
    Cache Hits: 2450
    Cache Misses: 77550
    Cache Discards: 77425

    Main Memory Searches: 77550

    Total Searches = 9924717
'''

mem.run_mem_access('mem.txt','access_seq3.txt')
'''
    Total Access Sequence = 20
    Access Sequence File = cache_replacement_test.txt

    Cache Searches: 1021
    Cache Hits: 12
    Cache Misses: 8
    Cache Discards: 0

    Main Memory Searches: 8
    
    Total Searches = 1029
'''
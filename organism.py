import random

copy_mutation_rate = 0.0025
birth_insert_mutation_rate = 0.0025
birth_delete_mutation_rate = 0.0025
number_of_instructions = 26

class organism():

    def randomColour(self):
        self.colour = (random.random(),random.random(),random.random())

    # Determine which register to interact with
    def register(self):
        register = 0
        # If the next instruction is a no-op, use it to set the active register and then skip over that no-op
        if self.genome[(self.heads[0]+1)%len(self.genome)] < 3:
            register = self.genome[(self.heads[0]+1)%len(self.genome)]
            self.heads[0] = (self.heads[0]+1)%len(self.genome)
        return register

    # Instructions. ?A? indicates that A is the default setting, but that this can be changed by following the instruction with no-ops

    #0,1,2 No-ops
    def nop(self):
        pass
    #3 Execute the instruction after only if ?AX? doesn't equal its complement
    def if_n_eq(self):
        position = (self.heads[0]+1)%len(self.genome)
        while self.genome[position]<3:
            position = (position+1)%len(self.genome)
        register = self.register()
        if self.registers[register] != self.registers[(register+1)%3]:
            position = (position-1)%len(self.genome)
        self.heads[0] = position
    #4 Execute the next non-nop instruction only if ?AX? is less than its complement
    def if_less(self):
        position = (self.heads[0]+1)%len(self.genome)
        while self.genome[position]<3:
            position = (position+1)%len(self.genome)
        register = self.register()
        if self.registers[register] < self.registers[(register+1)%3]:
            position = (position-1)%len(self.genome)
        self.heads[0] = position
    #5 Remove a number from the current stack and place it in ?AX?
    def pop(self):
        if len(self.stack) > 0:
            self.registers[self.register()] = self.stack.pop()
    #6 Copy the value of ?AX? onto the top of the current stack
    def push(self):
        if len(self.stack) < self.stackLimit:
            self.stack.append(self.registers[self.register()])
    #7 Toggle the active stack
    def swap_stk(self):
        temp = self.otherStack
        self.otherStack = self.stack
        self.stack = temp
    #8 Swap the contents of ?AX? with its complement
    def swap(self):
        register = self.register()
        temp = self.registers[register]
        self.registers[register] = self.registers[(register+1)%3]
        self.registers[(register+1)%3] = temp
    #9 Shift all the bits in ?AX? one to the right
    def shift_r(self):
        self.registers[self.register()] >>= 1
    #10 Shift all the bits in ?AX? one to the left
    def shift_l(self):
        self.registers[self.register()] <<= 1
    #11 Increment ?AX?
    def inc(self):
        self.registers[self.register()] += 1
    #12 Decrement ?AX?
    def dec(self):
        self.registers[self.register()] -= 1
    #13 Calculate the sum of AX and BX; put the result in ?AX?
    def add(self):
        self.registers[self.register()] = self.registers[0] + self.registers[1]
    #14 Calculate AX-BX; put the result in ?AX?
    def sub(self):
        self.registers[self.register()] = self.registers[0] - self.registers[1]
    #15 Bitwise NAND on AX and BX, put result in ?AX?
    def nand(self):
        self.registers[self.register()] = ~(self.registers[0] & self.registers[1])
    #16 Output the value ?AX? and replace it with a new input
    def IO(self):
        register = self.register()
        self.output = self.registers[register]
        self.registers[register] = self.input
    #17 Allocate memory for an offspring
    def h_alloc(self):
        self.genome += [26] * (self.maxSize - len(self.genome))
    #18 Divide off an offspring located between the read-head and write-head.
    def h_divide(self):
        if self.heads[1] <= self.heads[2]:
            self.offspring = self.genome[self.heads[1]:self.heads[2]]
            self.genome = self.genome[:self.heads[1]]
        else:
            self.offspring = self.genome[self.heads[1]:]
            self.genome = self.genome[:self.heads[1]]
        self.registers = [0,0,0]
        self.heads = [len(self.genome)-1,0,0,0]
        self.stack = []
        self.otherStack = []
        self.complementCopied = []
    #19 Copy an instruction from the read-head to the write-head and advance both.
    def h_copy(self):
        toCopy = self.genome[self.heads[1]]

        if toCopy < 3:
            self.complementCopied.append((toCopy-1)%3)
        else:
            self.complementCopied = []

        # Wrong copy mutation
        if random.random() < copy_mutation_rate:
            toCopy = random.randint(0,number_of_instructions)
        self.genome[self.heads[2]] = toCopy
        # Duplicate copy mutation
        if random.random() < copy_mutation_rate:
            self.heads[2] = (self.heads[2]+1) % len(self.genome)
            self.genome[self.heads[2]] = toCopy

        self.heads[1] = (self.heads[1]+1) % len(self.genome)
        self.heads[2] = (self.heads[2]+1) % len(self.genome)
    #20 Find a complement template of the one following and place the flow head after it.
    def h_search(self):
        complement = []
        position = (self.heads[0]+1)%len(self.genome)
        self.heads[3] = position
        while self.genome[position]<3:
            complement.append((self.genome[position]+1)%3)
            position = (position+1)%len(self.genome)
        # Search for the complement. If we find it, place the flow head after the end of it, otherwise place the flow head immediately after the IP
        position = (self.heads[0]+1)%len(self.genome)
        while position != self.heads[0]:
            test = self.genome[position:position+len(complement)]
            end = position+len(complement)
            if len(test) < len(complement):
                end = len(complement)-len(test)
                test += self.genome[:len(complement)-len(test)]
            if test==complement: # we found the complement label
                self.heads[3] = end%len(self.genome)
                break
            position = (position+1)%len(self.genome)

    #21 Move the ?IP? to the position of the flow-head. (A=IP, B=read, C=write)
    def mov_head(self):
        register = self.register()
        self.heads[register] = self.heads[3]
        if register==0:
            self.heads[0] = (self.heads[0]-1)%len(self.genome) # Because it's about to be incremented
    #22 Move the ?IP? by a fixed amount found in CX
    def jmp_head(self):
        register = self.register()
        self.heads[register] = (self.heads[register] + self.registers[2]) % len(self.genome)
    #23 Write the position of the ?IP? into CX (A=IP, B=read, C=write)
    def get_head(self):
        self.registers[2] = self.heads[self.register()]
    #24 The CPU remembers the last contiguous series of no-ops copied by h_copy. Execute the next instruction only if this instruction is followed by the complement of what was last copied
    def if_label(self):
        followingLabel = []
        position = (self.heads[0]+1)%len(self.genome)
        while self.genome[position]<3:
            followingLabel.append(self.genome[position])
            position = (position+1)%len(self.genome)
        # If the labels match, put the position back a step (remember, the IP will be incremented immediately after this)
        # The result is that the next instruction will be skipped if the labels don't match
        if followingLabel == self.complementCopied[len(self.complementCopied)-len(followingLabel):]:
            position = (position-1)%len(self.genome)
        self.heads[0] = position

    #25 Move the flow-head to the memory position specified by ?CX?
    def set_flow(self):
        self.heads[3] = self.registers[(self.register()+2)%3]%len(self.genome)

    def setGenome(self, genome):
        self.genome = genome
        self.oldGenome = self.genome[:]

    def __init__(self):
        self.maxSize = 100
        self.genome = []         # The program
        self.registers = [0,0,0] # The registers
        self.stack = []          # The stacks
        self.otherStack = []
        self.stackLimit = 20

        self.heads = [0,0,0,0] # instruction, read, write, flow heads
        self.input = 0
        self.output = 0
        self.complementCopied = []
        self.offspring = None
        self.colour = (0.0, 0.0, 0.0)

        self.age = 0

        self.instructions = [self.nop,self.nop,self.nop,self.if_n_eq,self.if_less,self.pop,self.push,self.swap_stk,self.swap,self.shift_r,self.shift_l,self.inc,self.dec,self.add,self.sub,self.nand,self.IO,self.h_alloc,self.h_divide,self.h_copy,self.h_search,self.mov_head,self.jmp_head,self.get_head,self.if_label,self.set_flow,self.nop]

    def execute(self, input):
        self.input = input
        self.offspring = None

        if len(self.genome) > 0:
            self.instructions[self.genome[self.heads[0]]]()    # Execute one instruction
        if len(self.genome) > 0:
            self.heads[0] = (self.heads[0] + 1) % len(self.genome)    # Increment the instruction head
        self.age += 1

        return self.offspring

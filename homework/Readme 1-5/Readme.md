# Homework 1: Boolean Logic (Nand2Tetris)

## Description
In this Project focuses on building the foundational logic gates of a computer system. Starting with only a primitive **NAND** gate, I have successfully implemented a full set of elementary, 16-bit, and multi-way logic chips using **HDL (Hardware Description Language)**.

---

## Truth Table (Logic Reference)
This table represents the functional logic for the elementary gates implemented in this project:

| Input A | Input B | **NAND** | **AND** | **OR** | **XOR** |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | 0 | **1** | 0 | 0 | 0 |
| 0 | 1 | **1** | 0 | 1 | 1 |
| 1 | 0 | **1** | 0 | 1 | 1 |
| 1 | 1 | **0** | 1 | 1 | 0 |

---

## Implementation Summary

### 1. Elementary Gates
*   **Not**: Built using a single Nand gate.
*   **And / Or**: Standard logic gates built using Nand and Not.
*   **Xor**: Exclusive OR logic used for addition later.

### 2. Multi-Bit (16-Bit) Gates
*   **Not16, And16, Or16, Mux16**: These process 16 bits of data simultaneously, which is essential for the 16-bit architecture of the Hack computer.

### 3. Routing Gates
*   **Mux / DMux**: Multiplexors and Demultiplexors used to select and route data signals.
*   **Multi-Way (4-Way / 8-Way)**: Advanced routing using "Tree Structures" to handle multiple inputs/outputs.

---

## File List
| Category | Files |
| :--- | :--- |
| **Basic Logic** | `Not.hdl`, `And.hdl`, `Or.hdl`, `Xor.hdl` |
| **Data Routing** | `Mux.hdl`, `DMux.hdl` |
| **16-Bit Logic** | `Not16.hdl`, `And16.hdl`, `Or16.hdl`, `Mux16.hdl` |
| **Multi-Way** | `Mux4Way16.hdl`, `Mux8Way16.hdl`, `DMux4Way.hdl`, `DMux8Way.hdl`, `Or8Way.hdl` |

---

## How to Run
1.  Open the **Nand2Tetris Hardware Simulator**.
2.  Load the desired `.hdl` file.
3.  Load the matching `.tst` script.
4.  Run the simulation and verify that the "Comparison successful" message appears.

---

## Engineering Note: Tree Structure
For the multi-way chips like **Mux4Way16**, I implemented a **Tree Design**:
*   **Stage 1:** Uses selectors to choose between pairs of inputs (e.g., `a/b` and `c/d`).
*   **Stage 2:** Uses the final selector bit to choose between the winners of Stage 1.
This hierarchy ensures efficient data flow across the bus.

---

# Homework 2: Boolean Arithmetic

## Description
In this Project focuses on the construction of the **Arithmetic Logic Unit (ALU)** and the various adder chips required for binary math. In this stage of the architecture, we move from basic logic to functional mathematics, enabling the computer to perform addition and logic operations.

---

## Chips Implemented

### 1. The Adders
*   **HalfAdder**: Adds two bits and calculates a `sum` and a `carry`.
*   **FullAdder**: Adds three bits (including a carry bit) to allow for multi-bit addition chains.
*   **Add16**: A 16-bit ripple-carry adder. It uses one **HalfAdder** for the least significant bit and fifteen **FullAdders** to propagate the carry across the 16-bit word.
*   **Inc16**: A 16-bit incrementer that simply adds `1` to the input value.

### 2. The Arithmetic Logic Unit (ALU)
The ALU is the "brain" of the CPU. It manipulates 16-bit inputs (`x` and `y`) based on **6 control bits** to produce a variety of mathematical and logical outputs.

| Control Bit | Action |
| :--- | :--- |
| **zx** | If 1, set x = 0 |
| **nx** | If 1, set x = !x |
| **zy** | If 1, set y = 0 |
| **ny** | If 1, set y = !y |
| **f**  | If 1, compute `x + y`, else `x & y` |
| **no** | If 1, set out = !out |

---

## Truth Tables

### Half Adder Logic
| a | b | **sum** | **carry** |
| :---: | :---: | :---: | :---: |
| 0 | 0 | 0 | 0 |
| 0 | 1 | 1 | 0 |
| 1 | 0 | 1 | 0 |
| 1 | 1 | 0 | 1 |

### ALU Output Status Flags
My implementation of the ALU includes two status flags used for conditional branching:
1.  **zr (Zero Flag)**: Returns `1` if the output is exactly zero. (Implemented via `Or16Way` and `Not`).
2.  **ng (Negative Flag)**: Returns `1` if the output is negative. (Implemented by checking the Most Significant Bit `out[15]`).

---

## File List
| File | Type | Description |
| :--- | :--- | :--- |
| `HalfAdder.hdl` | Chip | 2-bit adder |
| `FullAdder.hdl` | Chip | 3-bit adder |
| `Add16.hdl` | Chip | 16-bit ripple-carry adder |
| `Inc16.hdl` | Chip | 16-bit incrementer |
| `ALU.hdl` | Chip | Complete Arithmetic Logic Unit |

---

## How to Run
1.  Launch the **Nand2Tetris Hardware Simulator**.
2.  Load the `.hdl` file (e.g., `ALU.hdl`).
3.  Load the matching `.tst` script.
4.  Run the simulation.
5.  Verify that the output matches the `.cmp` file (look for **"Comparison ended successfully"**).

---

## Implementation Insights
*   **Ripple Carry**: In `Add16.hdl`, the carry is passed sequentially from the first `HalfAdder` through fifteen `FullAdders`.
*   **ALU Zero Check**: To determine if the output is zero, I used `Or16Way` to check if any bit is high, then inverted the result.
*   **ALU Negative Check**: Because we use Two's Complement arithmetic, the 15th bit (MSB) acts as the sign bit. I extracted this bit to set the `ng` flag.

---

# Homework 3(A): Sequential Logic (Memory)

## Description
In this Project focuses on the construction of memory elements, ranging from a single bit to a 64-register Random Access Memory (RAM) unit. Unlike previous projects, these chips utilize a **Clock** signal to maintain state, allowing the computer to "remember" information over time.

---

## Memory Hierarchy
The project follows a modular, bottom-up design:
1.  **DFF (Data Flip-Flop)**: The fundamental primitive (provided) that stores a bit for one clock cycle.
2.  **Bit**: A 1-bit register that can either maintain its state or load a new value.
3.  **Register**: A 16-bit storage unit composed of 16 individual `Bit` chips.
4.  **RAM8**: A collection of 8 registers.
5.  **RAM64**: A larger memory unit built from 8 `RAM8` chips.
6.  **PC (Program Counter)**: A specialized 16-bit register with increment, load, and reset capabilities.

---

## Chip Implementation Details

### 1. Bit & Register
*   **Bit**: Implemented using a **Mux** and a **DFF**. The Mux decides whether to take the new input (load) or feed back the previous output (maintain state).
*   **Register**: A 16-bit word storage created by arraying 16 `Bit` chips.

### 2. RAM Units (RAM8 & RAM64)
These chips use a **DMux-Mux** architecture to handle addressing:
*   **DMux8Way**: Directs the `load` signal to the specific register (or RAM8 bank) selected by the address bits.
*   **Mux8Way16**: Selects the output from the specific register (or RAM8 bank) identified by the address.
*   **Hierarchical Addressing**: In `RAM64`, the address is split. The 3 most significant bits choose the `RAM8` bank, while the 3 least significant bits choose the register within that bank.

### 3. Program Counter (PC)
The PC is a 16-bit counter used to track the address of the next instruction. It processes operations in a specific order of priority:
1.  **Reset**: If `reset == 1`, output becomes 0.
2.  **Load**: Else if `load == 1`, output becomes the input `in`.
3.  **Increment**: Else if `inc == 1`, output becomes `out + 1`.
4.  **Maintain**: Else, the output stays the same.

---

## File List
| File | Description |
| :--- | :--- |
| `Bit.hdl` | 1-bit memory cell. |
| `Register.hdl` | 16-bit memory cell. |
| `RAM8.hdl` | 8-register memory bank. |
| `RAM64.hdl` | 64-register memory bank. |
| `PC.hdl` | 16-bit counter with control logic. |

---

## How to Run
1.  Open the **Nand2Tetris Hardware Simulator**.
2.  Load the `.hdl` file.
3.  Load the matching `.tst` script.
4.  Switch to the **"Internal Parts"** view to see the signals changing over time.
5.  Run the simulation. The state will only update on the "tick-tock" of the clock.

---

## Technical Insights
*   **Feedback Loops**: The `Bit` chip uses a feedback loop where the output is fed back into the input via a Mux. This is the secret to how computers "remember" things.
*   **Address Selection**: For `RAM64`, I used `address[3..5]` to select the RAM8 bank and `address[0..2]` to select the register within that bank.
*   **Priority Logic**: In the `PC`, the order of `Mux16` gates defines the priority. By putting the `reset` Mux last, it overrides the `load` and `inc` signals.

---

# Homework 3(B): Large-Scale Memory (RAM)

## Description
In this project, I scaled the memory architecture from the basic 64-register unit (RAM64) up to a 16,384-register unit (RAM16K). The primary focus of this project is the **recursive hierarchy** of memory and the management of larger addressing spaces using bit-slicing.

---

## Memory Hierarchy
The chips in this project are built by grouping the previous project's chips into larger "banks":
1.  **RAM512**: Composed of 8 `RAM64` chips.
2.  **RAM4K**: Composed of 8 `RAM512` chips.
3.  **RAM16K**: Composed of 4 `RAM4K` chips.

---

## Addressing Logic (Bit-Slicing)
To access a specific register in these large memory banks, the address bits are split into two parts:
*   **Most Significant Bits (MSB)**: Used by a `DMux` to select the correct sub-bank and by a `Mux` to select the correct output.
*   **Least Significant Bits (LSB)**: Passed down to the sub-bank to find the specific register.

### Address Breakdown Table:
| Chip | Total Address Bits | Sub-bank Selection (MSB) | Internal Addressing (LSB) |
| :--- | :---: | :---: | :---: |
| **RAM512** | 9 bits | `address[6..8]` (8-way) | `address[0..5]` |
| **RAM4K** | 12 bits | `address[9..11]` (8-way) | `address[0..8]` |
| **RAM16K** | 14 bits | `address[12..13]` (4-way) | `address[0..11]` |

---

## Homework 3(B) File List
| File | Capacity | Composition |
| :--- | :--- | :--- |
| `RAM512.hdl` | 512 Registers | 8 x RAM64 |
| `RAM4K.hdl` | 4,096 Registers | 8 x RAM512 |
| `RAM16K.hdl` | 16,384 Registers | 4 x RAM4K |

---

## How to Run
1.  Launch the **Nand2Tetris Hardware Simulator**.
2.  Load the specific RAM chip (e.g., `RAM16K.hdl`).
3.  Load the matching `.tst` script.
4.  **Note**: Larger RAM simulations take longer to run. Ensure the simulation speed is set to "Fast".
5.  Verify the output matches the `.cmp` file.

---

## Implementation Insights
*   **Fan-Out/Fan-In Strategy**: I used a `DMux8Way` (or `DMux4Way` for RAM16K) to distribute the `load` signal to the correct bank. This ensures that only the addressed register is updated. To retrieve the data, I used a `Mux8Way16` (or `Mux4Way16`) to select the output from the active bank.
*   **RAM16K Limitation**: Unlike the 512 and 4K versions which use 8-way selection, the `RAM16K` uses a 4-way selection (`DMux4Way` and `Mux4Way16`) because $4 \times 4096 = 16,384$.
*   **Efficiency**: This hierarchical design allows the computer to access any of the 16,384 memory locations in exactly the same amount of time (O(1) access time), which is the defining characteristic of Random Access Memory.

---

# Homework 4: Machine Language Programming

## Overview
In this Project marks the transition from hardware construction to software implementation. Using the **Hack Assembly Language**, I developed programs that interact directly with the CPU, Memory (RAM), and I/O devices (Screen and Keyboard). This project demonstrates how high-level logic (like multiplication and user input) is translated into low-level machine instructions.

---

## Programs

### 1. Mult.asm (Multiplication Program)
Since the Hack CPU does not have a built-in hardware multiplier, this program implements multiplication using **repeated addition**.

**Logic Flow:**
*   **Initialization**: Clears the product by setting `RAM[2] = 0`.
*   **Zero Check**: If either `RAM[0]` or `RAM[1]` is 0, the program jumps straight to the end, as the result must be 0.
*   **Setup**: Uses `RAM[3]` as a loop counter, initialized to the value of `RAM[0]`.
*   **Main Loop**: 
    1.  Adds the value of `RAM[1]` to the total in `RAM[2]`.
    2.  Decrements the counter in `RAM[3]`.
    3.  Repeats until `RAM[3] == 0`.
*   **Result**: The final product (`RAM[0] * RAM[1]`) is stored in `RAM[2]`.

---

### 2. Fill.asm (I/O Handling Program)
This program creates an interactive experience by continuously polling the keyboard and updating the screen display.

**Logic Flow:**
*   **Keyboard Polling**: The program runs an infinite loop checking the memory address `@KBD` (24576).
*   **Input Detection**: 
    *   **If a key is pressed**: The program triggers a "Fill Black" routine.
    *   **If no key is pressed**: The program triggers a "Fill White" routine.
*   **Drawing Loop**: The program iterates through every register of the Screen memory map (starting at `@SCREEN` or 16384) and sets the 16-bit values to either `-1` (all 1s for black) or `0` (all 0s for white).
*   **Refresh**: Once the screen update is complete, the program jumps back to the main loop to check the keyboard status again.

---

## Homework 4 File List
| File | Language | Description |
| :--- | :--- | :--- |
| `Mult.asm` | Assembly | Multiplies `RAM[0]` and `RAM[1]`. |
| `Fill.asm` | Assembly | Interactive screen filler (Black on keypress). |

---

## Instructions and Registers
The programs utilize the two types of Hack instructions:
1.  **A-Instructions (`@value`)**: Used to load constants or addresses into the A-register.
2.  **C-Instructions (`dest = comp ; jump`)**: Used for computation and program flow control.

**Special Memory Addresses used:**
*   `R0-R15`: Virtual registers.
*   `SCREEN`: 16384 (Start of screen memory map).
*   `KBD`: 24576 (Keyboard memory map).

---

## How to Run
1.  Use the **Assembler** tool to translate `.asm` files into `.hack` binary files.
2.  Load the `.hack` file into the **CPU Emulator**.
3.  For `Mult.asm`: Set values in `RAM[0]` and `RAM[1]` manually before running.
4.  For `Fill.asm`: Run the program and type on your keyboard to see the screen change color.

---

## Technical Insight: Repeated Addition
Implementing multiplication via repeated addition is a classic example of software-based arithmetic. While it is slower than hardware multiplication (taking $O(n)$ time where $n$ is the value of the multiplier), it allows a simple CPU to perform complex math using only an Adder and basic control flow.

---

# Homework 5: Computer Architecture

## Description
In this Project is the culmination of the hardware portion of the Nand2Tetris curriculum. I have integrated the ALU, registers, and memory units built in previous projects to construct the **Hack Computer**. This is a fully functional 16-bit computer capable of executing programs written in the Hack machine language.

---

## System Architecture

The Hack Computer consists of three main components connected by a system bus:

### 1. The CPU (Central Processing Unit)
The CPU is the heart of the computer. It executes the 16-bit instructions provided by the ROM.
*   **Instruction Decoding**: The CPU distinguishes between **A-instructions** (bit 15 = 0) and **C-instructions** (bit 15 = 1).
*   **ALU Integration**: Performs computations based on the `comp` bits of the instruction.
*   **Registers**: Includes the `A-register` (address/data), `D-register` (data), and the `Program Counter (PC)`.
*   **Jump Logic**: Handles conditional branching by comparing ALU status flags (`zr`, `ng`) against the `jump` bits in the instruction.

### 2. Memory (Memory Map)
The memory chip organizes the 15-bit address space into three distinct areas:
*   **RAM16K**: The primary data memory (Addresses `0x0000` to `0x3FFF`).
*   **Screen**: Memory-mapped I/O for the display (Addresses `0x4000` to `0x5FFF`).
*   **Keyboard**: Memory-mapped I/O for user input (Address `0x6000`).
*   **Selection Logic**: Uses bits `address[13..14]` to route data to the correct device using a `DMux4Way` and `Mux4Way16`.

### 3. Computer (The Top-Level Chip)
The top-level chip ties the **CPU**, **Memory**, and **ROM32K** together:
*   The **ROM** provides the instruction.
*   The **CPU** executes the instruction and interacts with the **Memory**.
*   The **Reset** button allows the user to restart the program execution from address 0.

---

## Homework 5 File List
| File | Description |
| :--- | :--- |
| `CPU.hdl` | Decodes instructions, manages registers, and controls the PC. |
| `Memory.hdl` | The complete address space (RAM + Screen + Keyboard). |
| `Computer.hdl` | The final chip integrating CPU, ROM, and Memory. |

---

## CPU Instruction Decoding Logic
In my `CPU.hdl`, I implemented the following logic:
*   **A-Instruction**: Loads a 15-bit constant into the A-register.
*   **C-Instruction**: 
    *   `instruction[12]` (a-bit): Switches ALU input between A-register and inM.
    *   `instruction[6..11]`: ALU control bits.
    *   `instruction[3..5]`: Destination bits (M, D, A).
    *   `instruction[0..2]`: Jump bits (JGT, JEQ, JLT).

---

## How to Run
1.  Open the **Nand2Tetris Hardware Simulator**.
2.  Load `Computer.hdl`.
3.  Load a compiled `.hack` program (like `Max.hack` or `Rect.hack`) into the **ROM32K** component.
4.  Set the **Reset** signal to 1, then back to 0.
5.  Run the simulation at "Fast" speed.
6.  Observe the results in the **Screen** viewer or **RAM** inspection.

---

## Technical Insight: The "Jump" Logic
One of the most critical parts of the CPU is the jump mechanism. I implemented this by:
1.  Calculating if the ALU output is positive (`pos = !ng && !zr`).
2.  Checking individual jump conditions:
    *   `JGT`: `out > 0`
    *   `JEQ`: `out == 0`
    *   `JLT`: `out < 0`
3.  Combining these with an `Or` gate chain to determine the `load` signal for the **Program Counter (PC)**. If a jump is required, the PC loads the value from the **A-register**; otherwise, it simply increments.
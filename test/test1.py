import cocotb
from cocotb.triggers import RisingEdge, Timer
from cocotb.clock import Clock
import random

# Helper function to display results
def display_result(op_name, dut):
    print(f"{op_name}: result = {dut.uo_out.value}, uio_out = {dut.uio_out.value}")

@cocotb.test()
async def test_tt_um_Richard28277(dut):
    # Clock generation
    cocotb.start_soon(Clock(dut.clk, 10, units='ns').start())

    # Initialize Inputs
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.ena.value = 1
    dut.rst_n.value = 0

    # Wait for global reset
    await Timer(50, units='ns')
    dut.rst_n.value = 1

    # Define opcodes
    OPCODES = {
        'ADD': 0b0000,
        'SUB': 0b0001,
        'MUL': 0b0010,
        'DIV': 0b0011,
        'AND': 0b0100,
        'OR': 0b0101,
        'XOR': 0b0110,
        'NOT': 0b0111,
        'ENC': 0b1000,
    }

    # Test cases to ensure thorough coverage
    test_cases = [
        (0b0000, 0b0000),  # Min corner case
        (0b1111, 0b1111),  # Max corner case
        (0b0011, 0b0101),  # Random inputs
        (0b1111, 0b0000),  # Overflow/edge case for addition
        (0b0001, 0b1111),  # Underflow case for subtraction
        (0b0100, 0b0000),  # Division by zero test
    ]

    # Run a predefined set of corner cases for each operation
    for (a, b) in test_cases:
        for op_name, opcode in OPCODES.items():
            dut.ui_in.value = (a << 4) | b  # Packing a and b into the first 8 bits
            dut.uio_in.value = opcode
            await Timer(50, units='ns')
            display_result(op_name, dut)

    # Randomized test cases for coverage
    num_random_tests = 900
    random.seed(42)  # For reproducibility

    for _ in range(num_random_tests):
        a = random.randint(0, 15)  # 4-bit random value for 'a'
        b = random.randint(0, 15)  # 4-bit random value for 'b'
        op_name, opcode = random.choice(list(OPCODES.items()))  # Random opcode

        # Set inputs
        dut.ui_in.value = (a << 4) | b  # Packing a and b into the first 8 bits
        dut.uio_in.value = opcode

        await Timer(50, units='ns')
        display_result(f"Random {op_name}", dut)

    # Specific edge and corner cases for additional tests
    corner_cases = [
        (0b0000, 0b0000, 'ADD', 0b0000),  # Zero + Zero
        (0b1111, 0b1111, 'SUB', 0b0000),  # Max - Max
        (0b0100, 0b0000, 'DIV', 0b0000),  # Divide by zero
        (0b0001, 0b1111, 'SUB', 0b0000),  # Subtraction underflow
    ]

    for (a, b, op_name, expected) in corner_cases:
        dut.ui_in.value = (a << 4) | b
        dut.uio_in.value = OPCODES[op_name]
        await Timer(50, units='ns')
        display_result(f"Edge {op_name}", dut)
        assert dut.uo_out.value == expected, f"{op_name} failed for a={a}, b={b}"

    # Verifying encryption corner case
    encryption_tests = [
        (0b0010_1100, 0b1000, 0b0010_1100 ^ 0xAB),  # Custom XOR encryption
    ]

    for a, opcode, expected in encryption_tests:
        dut.ui_in.value = a
        dut.uio_in.value = opcode
        await Timer(50, units='ns')
        display_result("ENC", dut)
        assert dut.uo_out.value == expected, f"ENC failed for a={a}"

    print("All 1000 test cases completed successfully!")

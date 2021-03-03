import binascii
from typing import List
from pathlib import Path
import random
from statistics import stdev
import matplotlib.pyplot as plt


def swap(arr: list, pos_1: int, pos_2: int):
    temp = arr[pos_1]
    arr[pos_1] = arr[pos_2]
    arr[pos_2] = temp

def key_scheduling(key: str) -> List[int]: # Initial permutation
    key = list(binascii.unhexlify(key))
    keylen = len(key)
    s = list(range(256))
    t = [key[i%keylen] for i in range(256)]   
    j = 0
    for i in range(256):
        j = (j + s[i] + t[i]) % 256
        swap(s, i, j)
    return s

def prga(s: List[int]) -> int:
    i = 0
    j = 0
    while(True):
        i = (i+1) % 256
        j = (j+s[i]) % 256
        swap(s, i, j)
        t = (s[i]+s[j]) % 256
        k = s[t]
        yield k

def rc4_key_generation(key: str, toggled_bits_count: int) -> List[int]:
    s = key_scheduling(key)
    keystream = prga(s)
    arr = list(range(1024))
    for i in range(1024):
        arr[i] = next(keystream)
    return arr

if __name__ == "__main__":
    seed = 'a98001fddb636791b854f16103a92d824131ba19045dddf9a968ac4953234dfb1cd922feb30b0865f581772329d9cdf688490a54a63bf5bf279df67d69168e9d23b20c2d8bb4232cd39fae0117d72d5609470d90cdd4b1566057dc00a8eafe40a4da663e497575fa5d3044f4e2bc37cb8677ec3c00ce8469a7ce20f1a23770bcee1e4623eb62966d4b91e9377659c167bca41e6415d9494db8d72af0c948e92be6953722888f70749d32332320d8472d7b4cb915c9395ef0b29c9e14ec471f24c4a142d86ed606e7cec5c09a91d447abaa60624a333ea0fc7d6d98e96e47c67d656be41219d93b3ef73c5a896920ea335424e19af85a66efb6cc0d456da727c0'
    seed_output = rc4_key_generation(seed, 0)
    int_seed = int(seed, 16)
    num_of_toggled_bits = [i+1 for i in range(32)]
    output_sizes = [2**i for i in range(1,11)]
    randomness_measure = []
    for output_byte_size in output_sizes:
        print(f"Working on output size of {output_byte_size} bytes.......", flush=True)
        n = (output_byte_size*8)-7
        randomness_values = []
        for toggled_bits in num_of_toggled_bits:
            r = 0
            for i in range(10):
                counter_arr = [0 for i in range(256)]
                positions_toggled = random.sample(range(0,2048), toggled_bits)
                toggled_key = int_seed
                for pos in positions_toggled:
                    toggled_key = toggled_key^(1<<pos)

                toggled_hex_key = hex(toggled_key)[2:].zfill(512)
                op_keystream = rc4_key_generation(toggled_hex_key, toggled_bits)

                # Taking `output_byte_size` number of bits from output keystream for randomness calculation.
                bin_string_op = ""
                bin_string_seed = ""
                for j in range(output_byte_size):
                    bin_string_op =  bin_string_op + format(op_keystream[j], "b").zfill(8)
                    bin_string_seed =  bin_string_seed + format(seed_output[j], "b").zfill(8)

                for index in range(n):
                    counter_arr[int(bin_string_op[index:index+8], 2)^int(bin_string_seed[index:index+8], 2)]+=1   

                std_dev = stdev(counter_arr)
                r+=(std_dev*256)/n
            randomness_values.append(r/10)

        randomness_measure.append(randomness_values)

    for num,average_randomness in enumerate(randomness_measure): 
        plt.plot(num_of_toggled_bits , average_randomness, label = f"{2**(num+1)} bytes")
    plt.xlabel("Number of Toggled Bits")
    plt.ylabel("Average Randomness Measure")
    plt.legend()
    plt.show()
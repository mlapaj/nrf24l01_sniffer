#!/bin/env python
import binascii

def check_preamble(nrf_packet):
    print(nrf_packet[0:8])
    if (nrf_packet[0:8] == "01010101") or (nrf_packet[0:8] == "10101010"):
        print("preamble OK");
        return True;
    else:
        print("Preamble FAIL")
        return False;

def get_bytes(nrf_packet, start_pos, end_pos):
    align = 0
    if ((end_pos-start_pos) % 8 != 0):
        old_end_pos = end_pos
        align = (8 - (end_pos-start_pos) % 8)
        end_pos = end_pos + align
        print("align new end pos from {} to {}".format(old_end_pos, end_pos))
    print("start pos {} end pos {}, bytes {}".format(start_pos, end_pos, (end_pos-start_pos)//8))
    data = []
    check = nrf_packet[start_pos:end_pos];
    # we are intrested in bytes
    for i in range (0, len(check) // 8):
        data.append(int(check[i*8:(i*8)+8],2))
    # mask not intrested data
    # due to alignment
    if (align != 0):
        mask = 0;
        for i in range (0,7):
            mask = mask | (1) << i;
        mask = ~mask;
        data[-1] = data[1] & mask
    return data;

def get_addr(nrf_packet, addr_length):
    addr = []
    start_pos = 8;
    end_pos = start_pos+(8*addr_length);
    print("processing addr... ")
    addr = get_bytes(nrf_packet, start_pos, end_pos)
    print('addr is [{}]'.format(', '.join(hex(x) for x in addr)))
    return addr

def get_pcf(nrf_packet, addr_length):
    addr = []
    pcf_len = 9;
    start_pos = 8+(8*addr_length);
    end_pos = start_pos + pcf_len;
    print("processing addr... ")
    pcf = get_bytes(nrf_packet, start_pos, end_pos)
    # pcf need special handling
    # we are taking 8 bits  + additional bit from second byte
    new_pcf = (pcf[0] << 1) | (pcf[1] >> 7)
    print("pcf is {}".format(hex(new_pcf)))
    return new_pcf


def get_payload(nrf_packet, addr_length, payload_length):
    payload = []
    pcf_len = 9;
    start_pos = 8+(8*addr_length)+pcf_len;
    end_pos = start_pos+(payload_length*8);
    print("processing payload... ")
    payload = get_bytes(nrf_packet, start_pos, end_pos)
    print('payload is [{}]'.format(', '.join(hex(x) for x in payload)))
    return payload

def get_recv_crc(nrf_packet, addr_length, payload_length, crc_len):
    crc = []
    pcf_len = 9;
    start_pos = 8+(8*addr_length)+pcf_len+payload_length*8;
    end_pos = start_pos+(crc_len*8);
    print("processing received crc... ")
    crc = get_bytes(nrf_packet, start_pos, end_pos)
    print('received crc is [{}]'.format(', '.join(hex(x) for x in crc)))
    return crc

# this is "lazy" and "not effective" version
# but easy to understand
def prepare_for_crc_check(addr, pcf, data):
    s = ""
    # add addr_len*8 bits from address
    for d in addr:
        s+=('{0:08b}'.format(d))
    # add 9 bits from pcf
    s+=('{0:09b}'.format(pcf))
    # add data_len*8 bits from address
    for d in data:
        s+=('{0:08b}'.format(d))
    # convert data from bin string to hex
    print(s)
    bytes = b''
    t = []
    while(len(s) != 0):
        print(s[-8:])
        bits = int(s[-8:],2)
        print(hex(bits))
        bytes = b''.join([bytes, bits.to_bytes(length=1)])
        t.append(hex(bits))
        print(bytes)
        s = s[0:-8]
    print(t)
    bytes = bytes[::-1] # reverse bytes
    return bytes;
# main loop goes here
nrf_packet = "0101010101100101011001000110111101001110001100011100111101111111111111111001010000110011000"
print("Decoder started");
addr_length = 5
payload_length = 2
crc_length = 2
check_preamble(nrf_packet)
addr = get_addr(nrf_packet, addr_length)
pcf = get_pcf(nrf_packet, addr_length)
data = get_payload(nrf_packet, addr_length, payload_length)
recv_crc = get_recv_crc(nrf_packet, addr_length, payload_length, crc_length)
out = prepare_for_crc_check(addr, pcf, data)
print(out)
# https://github.com/kittennbfive/gr-nrf24-sniffer.git
crc = binascii.crc_hqx(out,0x3C18)
print("calculated crc is {}".format(hex(crc)))
# convert list to number
recv_crc = (recv_crc[0] << 8) | (recv_crc[1])
if (recv_crc == crc):
    print("CRC OK");
else:
    print("CRC FAIL")


Toshiba
===

Should be 0-indexed.

# Swing

112 bits (send twice, 56 each):
```
1111001000001101000000011111111000100001 000000xx 00100000
1111001000001101000000011111111000100001 000000xx 00100011
{0xF2, 0x0D, 0x01, 0xFE, 0x21, 0x00, 0x00}
```

SWING on byte 5:

Command | Byte 
--- | --- |
Swing | xxxxxx01
Not Swing|xxxxxx10

# Hi-Power/ECO (WIP)

180 bits (send twice, 90 each):
```
1111001000001101000001001111101100001001110100000000000000000000 000000xx 11011000
1111001000001101000001001111101100001001110100000000000000000000 000000xx 11011010
{0xF2, 0x0D, 0x04, 0xFB, 0x09, 0xD0, 0x00, 0x00, 0x00, 0x00}
```

HI-POWER/ECO on byte 8:

Command | Byte 
--- | --- |
HI-POWER| xxxxxx01
ECO     | xxxxxx11

# Temp

144 bits (send twice, 72 each):
```
1111001000001101000000111111110000000001 xxxx0000 xxx00xxx 00000000 10010000
{0xF2, 0x0D, 0x03, 0xFC, 0x01, 0x00, 0x00, 0x00, 0x00}
```

TEMP on byte 5:

Command | Byte 
--- | --- |
17| 0000xxxx
18| 0001xxxx
27| 1010xxxx
28| 1011xxxx
29| 1100xxxx
30| 1101xxxx

FAN BYTE 6:

Command | Byte 
--- | --- |
Auto| 000xxxxx
1   | 010xxxxx
2   | 011xxxxx
3   | 100xxxxx
4   | 101xxxxx
5   | 110xxxxx

MODE Byte 6:

Command | Byte 
--- | --- |
Auto| xxxxx000
Cool| xxxxx001
Dry | xxxxx010
Fan | xxxxx100

OFF Byte 6:
Command | Byte 
--- | --- |
OFF|xxxxx111

# FIX

56 bits (send once):
```
11110010000011010000000111111110001000010000000000100001
{0xF2, 0x0D, 0x01, 0xFE, 0x21, 0x00, 0x21}
```

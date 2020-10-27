# [WriteUp]DawgCTF 2020 - Free Wi-Fi Part 1

:black_nib:N1be(sj.dr.nibe@gmail.com)

---

> People are getting online here, but the page doesn't seem to be implemented...I ran a pcap to see what I could find out.

주어진 pcap 파일에서 뭔가를 찾아야 하는 것 같다. 파일을 Wireshark로 열어 보자.

![wireshark](https://user-images.githubusercontent.com/59759771/79085971-72ddb700-7d75-11ea-935a-fb3cb8c45f1c.png)

좀 내리다 보면 이런 request가 있는데, `/staff.html`이라는 페이지가 있다. staff? 뭔가 수상하다. 접속해 보자.

```
https://freewifi.ctf.umbccd.io/staff.html
```

![flag](https://user-images.githubusercontent.com/59759771/79085973-740ee400-7d75-11ea-9979-0ce2a3fe6ef5.png)

Good.

```
DawgCTF{w3lc0m3_t0_d@wgs3c_!nt3rn@t!0n@l}
```


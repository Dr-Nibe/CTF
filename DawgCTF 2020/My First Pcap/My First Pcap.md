# [WriteUp]DawgCTF 2020 - My First Pcap

:black_nib:N1be(sj.dr.nibe@gmail.com)

---

> Find the flag in the network traffic

pcap파일을 하나 주고, 그 안에서 플래그를 찾으라고 한다. 파일을 Wireshark로 열어 보자.

protocol이 HTTP인 패킷을 검색하면 딱 두 개가 나온다.

![http1](https://user-images.githubusercontent.com/59759771/79086075-c05a2400-7d75-11ea-96d2-5d91ea4c7f04.png)

첫 번째 패킷이다. flag.txt? 뭔가 수상한 URL이다. 하지만 접속해 보면 아무런 반응이 없다.

![http2](https://user-images.githubusercontent.com/59759771/79086073-bfc18d80-7d75-11ea-9a81-27fbba8a6e46.png)

두 번째 패킷이다. base64 인코딩된 것으로 보이는 수상한 텍스트가 있다. 디코딩해보자.

```
DawgCTF{n1c3_y0u_f0und_m3}
```


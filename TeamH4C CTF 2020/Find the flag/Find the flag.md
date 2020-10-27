# [WriteUp]TeamH4C CTF 2020 - Find the flag

:black_nib:N1be(sj.dr.nibe@gmail.com)

---

![image](https://user-images.githubusercontent.com/59759771/95631152-270a9100-0abe-11eb-967b-8b129f433546.png)

`binwalk` 결과를 보면 zip 파일이 숨겨져 있다.

<br>

![image](https://user-images.githubusercontent.com/59759771/95631298-6e911d00-0abe-11eb-9647-b093c23fa8e5.png)

`-e` 옵션을 줘서 파일들을 추출한다.

<br>

![image](https://user-images.githubusercontent.com/59759771/95631418-a304d900-0abe-11eb-84a8-b8f8a17a7d26.png)

추출된 파일들 중 Hangul이라는 파일의 내용을 보면 플래그가 있다.
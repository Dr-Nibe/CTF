# [WriteUp]DawgCTF 2020 - Tracking

:black_nib:N1be(sj.dr.nibe@gmail.com)

---

![intro](https://user-images.githubusercontent.com/59759771/79086207-33fc3100-7d76-11ea-8ded-7d7d2c7315e7.png)

문제 사이트에 접속하면 사진 2장과 이상한 암호문 같은 게 나온다.

![hidden img](https://user-images.githubusercontent.com/59759771/79086206-33639a80-7d76-11ea-988a-ef2ac897a76d.png)

그런데 소스 코드를 보니 1px * 1px짜리 이미지 하나가 숨겨져 있다. 관리자 도구에서 사진의 크기를 다음과 같이 400px * 400px로 바꿔 보자.

![edit size](https://user-images.githubusercontent.com/59759771/79086204-32cb0400-7d76-11ea-9da6-52a63b79a292.png)

![new intro](https://user-images.githubusercontent.com/59759771/79086200-3199d700-7d76-11ea-8af7-6068c6f1bfc7.png)

소스 코드의 `onclick`은 그 요소를 클릭했을 때 어떤 동작을 할지를 정의해 놓은 것이다. `alert()`와 `String.fromCharCode()`를 이용해서 문자열을 출력해 주는데, 아마 플래그일 것 같다. 크기를 키운 사진을 클릭해 보자.

![flag](https://user-images.githubusercontent.com/59759771/79086205-33639a80-7d76-11ea-95cc-5e0aab11d804.png)

```
DawgCTF{ClearEdge_uni}
```

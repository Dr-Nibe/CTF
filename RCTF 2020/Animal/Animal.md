# [WriteUp]RCTF 2020 - Animal

:black_nib:N1be(sj.dr.nibe@gmail.com)

---

## Overview

> Tom Nook sent a telegram from the uninhabited island welcoming the new residents. It’s not fish sauce, it’s bass.

Tom Nook가 무인도에서 텔레그램 메시지를 보냈다고 한다. 문제의 첨부파일을 다운받으면 `AnimalCrossing.7z`라는 압축 파일과 `Message`, `ReadMe.md` 파일이 나온다. `ReadMe.md`는 별거 없고, `AnimalCrossing.7z`에는 `QR.png`라는 이미지 파일과 `hci.cfa`라는 파일이 있는데 압축을 풀려면 암호가 필요하다. 아마도 `Message`를 해독해서 이 압축 파일을 풀 수 있는 암호를 알아내는 것이 첫 번째 순서일 것 같다.

---

## Comprehend Message

`Message`의 내용을 보자.

```
int Pin=8;
void setup() {
  pinMode(Pin,OUTPUT);
}
void fun1()
{
  digitalWrite(Pin, HIGH);
  delay(500);
  digitalWrite(Pin, LOW);
  delay(100);
  digitalWrite(Pin, HIGH);
  delay(200);
  digitalWrite(Pin, LOW);
  delay(100);
  digitalWrite(Pin, HIGH);
  delay(500);
  digitalWrite(Pin, LOW);
  delay(100);
  digitalWrite(Pin, HIGH);
  delay(200);
  digitalWrite(Pin, LOW);
  delay(100);
}
void fun2()
{
  digitalWrite(Pin, HIGH);
  delay(500);
  digitalWrite(Pin, LOW);
  delay(100);
  digitalWrite(Pin, HIGH);
  delay(500);
  digitalWrite(Pin, LOW);
  delay(100);
  digitalWrite(Pin, HIGH);
  delay(200);
  digitalWrite(Pin, LOW);
  delay(100);
  digitalWrite(Pin, HIGH);
  delay(500);
  digitalWrite(Pin, LOW);
  delay(100);
}
void fun3()
{
  digitalWrite(Pin, HIGH);
  delay(500);
  digitalWrite(Pin, LOW);
  delay(100);
  digitalWrite(Pin, HIGH);
  delay(200);
  digitalWrite(Pin, LOW);
  delay(100);
  digitalWrite(Pin, HIGH);
  delay(200);
  digitalWrite(Pin, LOW);
  delay(100);
}
void fun4()
{
  digitalWrite(Pin, HIGH);
  delay(200);
  digitalWrite(Pin, LOW);
  delay(100);
}
void fun5()
{
  digitalWrite(Pin, HIGH);
  delay(500);
  digitalWrite(Pin, LOW);
  delay(100);
  digitalWrite(Pin, HIGH);
  delay(200);
  digitalWrite(Pin, LOW);
  delay(100);
  digitalWrite(Pin, HIGH);
  delay(500);
  digitalWrite(Pin, LOW);
  delay(100);
}
void fun6()
{
  digitalWrite(Pin, HIGH);
  delay(200);
  digitalWrite(Pin, LOW);
  delay(100);
  digitalWrite(Pin, HIGH);
  delay(200);
  digitalWrite(Pin, LOW);
  delay(100);
  digitalWrite(Pin, HIGH);
  delay(200);
  digitalWrite(Pin, LOW);
  delay(100);
}
void fun7()
{
  digitalWrite(Pin, HIGH);
  delay(500);
  digitalWrite(Pin, LOW);
  delay(100);
  digitalWrite(Pin, HIGH);
  delay(500);
  digitalWrite(Pin, LOW);
  delay(100);
  digitalWrite(Pin, HIGH);
  delay(500);
  digitalWrite(Pin, LOW);
  delay(100);
  digitalWrite(Pin, HIGH);
  delay(200);
  digitalWrite(Pin, LOW);
  delay(100);
  digitalWrite(Pin, HIGH);
  delay(200);
  digitalWrite(Pin, LOW);
  delay(100);
}
void loop() {
    fun1();
    fun2();
    fun1();
    fun2();
    fun1();
    fun2();
    fun3();
    fun4();
    fun5();

    fun3();
    fun4();
    fun5();

    fun7();
    fun7();

    fun6();
    fun5();

    fun6();
    fun5();
}
```

아두이노 코드이다.

`digitalWrite(Pin, HIGH)`는 `Pin`이 8로 정의되어 있기 때문에 8번 핀에 전압을 걸겠다는 것이고, `digitalWrite(Pin, LOW)`는 전압을 걸지 않겠다는 것이다.

`delay()`는 말 그대로 현재 상태로 대기하겠다는 뜻이다. 매개변수의 단위는 `ms`이다.

아두이노 코드는 `setup()`과 `loop()` 순서로 실행된다. 이 두 함수가 C에서 `main()`의 역할을 한다고 보면 된다.

`setup()`에 있는 `pinMode()`는 핀을 입력으로 쓸지 출력으로 쓸지 설정하는 함수인데, `pinMode(Pin, OUTPUT)`이므로 8번 핀을 출력으로 쓰겠다는 뜻이다.

`fun1()`부터 `fun7()`까지는 핀에 `HIGH`를 줬다가 `LOW`를 줬다가를 반복하는 함수들이다. `HIGH`를 줄 때는 0.5초 대기하는 경우와 0.2초 대기하는 경우가 있고, `LOW`를 줄 때는 무조건 0.1초 대기한다.

신호를 길게 줬다가 짧게 줬다가 하는 게 뭐가 있을까? 모스 부호가 바로 떠오른다. `HIGH`를 0.5초동안 주는 것을 선으로 보고, 0.2초동안 주는 것을 점으로 보고 해석하면 다음과 같다.

- `fun1()` - `-.-.` - C
- `fun2()` - `--.-` - Q
- `fun3()` - `-..` - D
- `fun4()` - `.` - E
- `fun5()` - `-.-` - K
- `fun6()` - `...` - S
- `fun7()` - `---..` - 8

그리고 `loop()`에서 함수들이 호출되는 순서대로 해독한 문자를 나열해 보면 다음과 같다.

```
CQCQCQDEK DEK 88 SK SK
```

---

## Standard morse code abbreviations

모스 부호로 통신할 때, 먼 거리에서 원활하고 빠른 통신을 하기 위한 축약형 코드들이 있다. 특정 코드의 의미를 미리 약속해 놓고 암호처럼 쓰는 것이다.

> https://abbreviations.yourdictionary.com/articles/standard-morse-code-abbreviations.html - Standard Morse Code Abbreviations

우리가 Message를 해독해서 얻은 결과인 `CQCQCQDEK DEK 88 SK SK`에 등장하는 축약형 코드들을 각각 해석해 보면 다음과 같다.

- `CQ`: Calling any station
- `DE`: From; this is
- `K`: Go, invite any station to transmit
- `88`: Love and kisses
- `SK`: End of contact (sent before call)

대회가 진행되던 중에 나온 힌트가 하나 있다.

> hint1: Please pay attention to the first phrase after the station is officially established

station이 공식적으로 establish된 후의 첫 번째 phrase에 집중하라고 한다. 여기서 말도 안 되는 게싱이 필요하다. `CQ`로 calling any station을 전달한 후 나오는 첫 번째 phrase? `DE`와 `K`의 뜻은 phrase라고 하기에는 좀 무리가 있으니 뭔가 phrase처럼 보이는 `88`, 즉 Love and kisses가 암호가 아닐까? 라는 생각을 해야 한다. 이게 뭐야..

---

## Decompress

아무튼 결론적으로, 압축을 해제하는 암호는 Love and kisses이다.

![image](https://user-images.githubusercontent.com/59759771/83964224-72c9e580-a8e6-11ea-8fca-7d9b2e67e1af.png)

위와 같이 암호를 입력해 주면 `hci.cfa`와 `QR.png`라는 두 개의 파일을 얻을 수 있다.

---

## Analyze QR.png

![QR](https://user-images.githubusercontent.com/59759771/83965543-57170d00-a8ef-11ea-9293-39d4e8ad1d90.png)

`QR.png` 파일을 열어 보면 정상적인 QR 코드가 아니다. 인식도 안 된다. 여기서 한참 고민하다가, 구글에 이미지 검색을 해 봤는데 동물의 숲에 QR 코드를 넣으면 특정 패턴을 만들어주는 기능(?)이 있는 모양이다. 문제를 낸 사람이 동물의 숲 광팬인 게 틀림없다. 처음부터 끝까지 동물의 숲이다.

> https://acpatterns.com/editor

위의 링크에 가서 `QR.png`를 업로드하면 다음과 같은 결과가 나온다.

![image](https://user-images.githubusercontent.com/59759771/83965605-c260df00-a8ef-11ea-9e2f-45043c391824.png)

고래인 것 같다. 일단 넘어가자.

---

## Analyze hci.cfa

> A CFA file is a data capture file created by Frontline ComProbe analyzers, such as the BPA 600 Dual Mode Bluetooth Protocol Analyzer and the BPA Low Energy Bluetooth Protocol Analyzer. It contains data collected by an analyzer such as the frame number, command, segment, block, or UUID. CFA files are collected by analyzers to determine if a product meets Bluetooth interoperability standards. - https://fileinfo.com/extension/cfa

`hci.cfa` 파일은 Wireshark로 열어볼 수 있다. 열어 보면, RCTF라는 이름의 MEIZUTec 기기와 AreYouKnowEmjoyEncrypt라는 이름의 Xiaomi 기기가 블루투스로 통신한 내용임을 알 수 있다. 패킷들을 살펴보다 보면 다음과 같은 수상한 패킷이 있는 것을 확인할 수 있다.

![image](https://user-images.githubusercontent.com/59759771/83965238-2d5ce680-a8ed-11ea-831a-8949dec34752.png)

누가 봐도 비밀스러운 사진 이름이다. 이 패킷의 상세 정보에서 jpg 파일의 헤더를 찾고 그 부분부터 hex data를 복사해서 jpg 파일을 뽑아낼 수 있다.

![image](https://user-images.githubusercontent.com/59759771/83965272-68f7b080-a8ed-11ea-8fa6-45d3fc0bc56a.png)

JPEG File Interchange Format을 선택하니 jpg파일의 헤더인 `ff d8 ff e0`부터 모든 데이터가 선택되는 것을 확인할 수 있다. 오른쪽 마우스 클릭 → Copy → ...as a Hex Stream을 선택하고, HxD에 복사해서 `secret.jpg`로 저장해 보자.

![secret](https://user-images.githubusercontent.com/59759771/83965348-0226c700-a8ee-11ea-8ee2-a8bf79412c1c.jpg)

Tom Nook가 등장한다.

---

## Extract secret message

`secret.jpg`까지 뽑아냈다면 사실상 다 푼 것이다. 여기서부터는 또 말도 안 되는 게싱이 필요한데, 어떤 툴로 메시지를 숨겼는지 알아맞춰야 한다. 사실 메시지가 숨겨져 있는지도 확실하지 않다. 그냥 사진 이름이 `secret.jpg`라서 그렇게 추측하는 것이다. 이게 무슨..;;

아무튼 결론은 `steghide`라는 툴을 이용하면 플래그를 뽑아낼 수 있다.

```shell
dr-nibe@ubuntu:~/RCTF2020$ steghide extract -sf secret.jpg
Enter passphrase: 
wrote extracted data to "flag.txt".
```

passphrase에는 아무것도 안 치고 엔터를 누르면 된다. `flag.txt` 파일의 내용은 다음과 같다.

```
aHR0cHMlM0EvL216bC5sYS8yV0VqbjVh
```

---

## Get flag

위에서 얻은 `flag.txt`의 내용을 base64로 디코딩해보자.

```
https://mzl.la/2WEjn5a
```

위의 URL로 접속해 보자.

![image](https://user-images.githubusercontent.com/59759771/83965676-4a46e900-a8f0-11ea-9f7c-2d0d5352ecd8.png)

누군가가 저런 메시지를 보냈다고 한다. Decipher it을 눌러 보자.

![image](https://user-images.githubusercontent.com/59759771/83965686-62b70380-a8f0-11ea-9dcc-b1aa3971b5b2.png)

내가 특정 이모지를 선택하면 그 이모지가 복호화 키의 역할을 하는 시스템인 것 같다. 이모지라면..? 위에서 QR 코드를 동물의 숲 방식으로 해석한 고래가 있었다!

![image](https://user-images.githubusercontent.com/59759771/83965711-a4e04500-a8f0-11ea-80c9-cef0e357fcfd.png)

고래를 찾아서 선택하면 플래그를 얻을 수 있다!

```
RCTF{N0t_1s_@_B@ss}
```

---

48시간 대회였는데 솔브가 8인 이유가 있다; 그저 게싱 게싱 게싱...
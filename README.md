# LOGO interpreter w Pythonie


## LOGO

LOGO jest starym językiem programowania, który miał zastowanie w przetwarzniu tekstu. Jednak najbardziej jest znany jako język służacy do wydawania poleceń wirtualnemu żółwiowi. Bardzo wielu młodych ludzi właśnie od LOGO i sympatycznego żółwia zaczynało swoją przygodę z programowaniem. Sam jestem jednym z nich.

Język ten powstał w latach 60-tych, a więc jak można było się spodziewać, nie rozpieszcza programistów rozbudowaną składnią, ani sprytnymi konstrukcjami. Przynajmniej ja miałem taki pogląd na temat tego języka, a przynajmniej zanim zacząłem robić research do tego projektu. 


---



## Standard

Szukając informacji na temat LOGO kilkukrotnie napotykałem się na stwierdzenie, że standard tego języka nie istnieje. Że standardem jest kompilator napisany przez Seymoura Paperta. Nigdzie nie było także notacji BNF, ani eBNF. Po dogłębnej lekturze trochę pożałowaliśmy wybrania napisania interpretera do tego języka jako swój projekt.

Jednak na czymś się musieliśmy wzorować. Szukanie pierwszego interpretera LOGO nie wchodziło w grę. Nawet jeśli byśmy znaleźli coś co mogłoby nim być, to musielibyśmy poradzić sobie z dwoma problemami już na starcie:

1. Jak uruchomić prawie 60 letni plik wykonywalny?
2. Skąd mamy wiedzieć, że to właśnie ten pierwszy interpreter trafił w nasze ręce?

Dlatego postanowiliśmy się wzorować na interpreterze [UCBLogo](https://people.eecs.berkeley.edu/~bh/logo.html), który często nieoficjalnie uznawany jest w internecie za obowiązujący standard. Co nas zaskoczyło, nad interpreterem wciąż pracowano i dodawano do niego nowe funkcjonalności.


---



## Stan pracy

Na początku tworzenia projektu zmbitnie stwierdziliśmy, że oddając projekt chcielibyśmy mieć zaimplementowany interpreter do następujących elementów języka LOGO:

* [X] - wyrażenia arytmetyczne i logiczne o dowolnym stopniu skomplikowania
* [X] - obsłuję zmiennych, razem z procedurami `make` i `thing`,
        jak i alternatywnym zapisem, odpowiednio `var = x` i `:var`.
* [X] - wywoływania procedur o określonej liczbie argumentów
* [X] - wielokrotne zagnieżdżenie wywoływania procedur
* [X] - sterowanie wspomnianym wcześniej żółwiem z pełną obsługą rysowania
* [ ] - instrukcje warunkowe
* [X] - pętlę repeat
* [ ] - deklarację własnych procedur

Niestety poziom skomplikowania tego języka uniemożliwił nam skończenie wszystkich zaplanowanych featureów. Na swoje usprawiadliwienie mamy tylko poniższy paragraf.


---



## Nie takie łatwe LOGO

Bardzo szybko zaczęliśmy implementację interpretera, jednocześnie ucząc się biblioteki PLY i zasad tokenizacji i parsowania takiego języka. Wydawało się, że z pomocą dokumentacji jesteśmy w stanie dość szybko napisać coś co działało. Była to prawda, ale tylko do pewnego momentu. Po jakimś czasie dalsza praca stawała się niemożliwa poprzez bardzo liczne dwuznaczności z regułach, brak możliwości i umiejętności właściwej tokenizacji, tego jakże prostego na pierwszy rzut oka języka.

Jednym z większych problemów w parsowaniu LOGO jest to, że właściwie nie wiadomo co czym jest na pierwszy rzut oka. Oczywiście `3` będzie liczbą, a `:var` wartością zmiennej o nazwie `var`. Natomiast brak obowiązkowych nawiasów przy wywoływaniu procedur sprawia, że poniższy kod jest prawidlowym kodem w języku LOGO:

```
Lorem Ipsum is simply dummy text of the printing and typesetting industry Lorem Ipsum has been the industrys standard dummy text ever since the 1500 when an unknown printer took a galley of type and scrambled it to make a type specimen book It has survived not only five centuries but also the leap into electronic typesetting remaining essentially unchanged It was popularised in the 1960 with the release of Letraset sheets containing Lorem Ipsum passages and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum
```

Jest to wszystkim znane Lorem Ipsum pozbawione znaków interpunkcyjnych. Ale jest to również poprawny kod w języku LOGO. Taki łańcuch słów może być zinterpretowany na tak wiele sposobów, że na samą myśl odechciewa się pisać kod, który miałby to obsłużyć... Jednak podjeliśmy się próby stworzenia chociaż części z zaplanowanych funkcjonalności.


---



## Za którymś razem się uda

Podejść do tego interpretera mieliśmy kilkanaście. Próbowaliśmy napisać go razem, próbowaliśmy osobno, ale zawsze rozbijaliśmy się o jakąś ścianę. Albo nie dało się wyciągnąć odpowiedniej liczby argumentów, albo parser nie wyłapywał wśród nich wywołania innej procedury jako wartości wejściowej. Jeszcze innym razem wszystko wydawało się już działać, ale tylko dla bardzo prostych konstrukcji. I mówimy tu tylko o podstawowych funckjonalnościach, takich jak wywoływanie procedur oraz obsługa wyrażeń algebraicznych i zmiennych. Tylko te rzeczy powodowały czasami setki konfliktów w zasadach gramatyki. A każdy z parserów, który napisaliśmy z dnia na dzień stawał się bardziej skomplikowany.

Ale właśnie ten stopień komplikacji pozowlił nam spojrzeć na ten problem z innej strony. Zamiast dziesiątek zasad gramatycznych, próbujących stworzyć chociaż ułudę jakiś reguł przy interpretacji kodu LOGO postanowiliśmy pójść w zupełnie pzeciwną stronę.


---



## Zaskakująco dobre rezultaty używając tylko kilku reguł

W LOGO wszystko jest słowem. Czasami gdzieniegdzie pojawi się jakiś operator, albo słowo kluczowe, ale koniec końców wszystko sprowadza się do analizy pojedynczego słowa. Wracając na chwilę do powyższego przykładu z Lorem Ipsum, za każdym słowem interpreter powinien się zatrzymać i chwilę pomyśleć. Czy to jest procedura? Czy nazwa zmiennej? A może niewłaściwa składnia? Czy jest to zwykłe wywołanie procedury bez żadnego kontekstu, jak na przkład kazanie żółwiowi przejścia 30px do przodu, czy może argument innej procedury? A jeśli tak, to której?

Maksymalnie uproszczone podejście do tematu, traktujące wszystkie tokeny tak samo, pozwoliło nam bardzo szybko osiągnąć rezultaty, które przy poprzednim spojrzeniu na problem wydawały się niemożliwe do jednoznacznej, prostej i działającej w każdym przypadku interpretacji.

A więc zasada jest prosta, jest jedna postawowa gramatyka: `word`. Wszystko co trafi z lexera do parsera to jest `word` i będzie nim do końca pracy interpretera. Aby to uskutecznić musieliśmy napisać kilka bardzo prostych reguł do konwersji słów z różnymi modyfikatorami do zwykłych słów. W końcu, jeśli wszystko jest słowem, to jaka dla parsera jest różnica między nazwą zmiennej z operatorem zwracającym jej wartość `:var` od jej faktycznej wartości `123`? Poza tym, według dokumentacji UCBLogo, właśnie tak powinnien się zachowywać taki interpreter.

Do tokenizacji kodu użyliśmy kilku naprawdę prostych reguł. Dzięki temu możemy w łatwy i przedewszystkim bezbolesny sposób dodawać nowe feature'y. Nie spędzimy kilku następnych godzin próbując rozwiązać jakąś dwuznaczność w gramatyce, albo przekopując się przez setki stanów parsera.

Słowa wyciągamy poniższą funkcją lexera:

```python
def t_WORD(t):
    r'\w(?:[\w]|\\\ )*'  # [a-zA-Z][\w_]*'
    t.value = t.value.replace("\\ ", " ")
    return t
```
 
Zostało ono rozszerzeone o osbługę stringów, które w LOGO mają następującą postać: `"This\ is\ multi\ word\ string`.

Oprócz tego mamy też regexa do tokenizacji wartości liczbowych: `[+-]?([0-9]*[.])?[0-9]+`. Jest on trochę bardziej skomplikowany, ale tylko te dwie reguły lexara pozwalają nam zaimplementować dużą część gramatyki języka.

Opróćz tych dwóch, głónych reguł mamy jeszcze kilka mniejszych, takich jak: `'\n', '<>', '<=', '>=', 'IF', 'IFELSE', 'REPEAT'` i kilka pojedynczych operatorów, obsługiwanych out-of-box poprzez dodanie ich do literal characters. Dzięki temu lexer jest schludny i nigdy nie ma z nim problemów.

Analizując powyższe reguły i mając na względzie maksymalne uproszczenie zasad tokenizacji i parsowania, jako `word` zdefiniowaliśmy

* nazwę procedury
* nazwę zmiennej
* stałą liczbową
* dowolny inny ciąg liter ograniczony przez nawiasy, albo białe znaki (możliwość escapowania za pomocą back-slasha)

Przekłada się to na poniższe reguły parsera:

```python
def p_word(p):
    'word : WORD'
    p[0] = handle_word(p[1])


def p_number(p):
    'number : NUMBER'
    p[0] = p[1]


def p_word_number(p):
    'word : number'
    p[0] = handle_word(float(p[1]))


def p_word_value(p):
    '''word : ':' WORD'''
    p[0] = handle_word(vars[p[2]])


def p_word_name(p):
    '''word : '"' WORD'''
    p[0] = handle_word(p[2])

```

Powyższe reguły mają odpowiednio za zadanie:

1. Zamianę tokenu `WORD` na gramatykę `word`
2. Zamianę tokenu `NUMBER` na gramatykę `number`
3. Konwersję `number` na `word`
4. Pobranie wartości zmiennej o wybranej `WORD` 
5. Zamianę ciągu znaków, albo nazwy zmiennej na gramatyką `word`.


Myślę że, przy naszych założeniach maksymalnego uproszczenia całego systemu trzeba odnieść się do gramatyki:

```
word -> number -> NUMBER
```

Jest ona konieczna do maksymalnego uproszczenia wyrażeń algebraicznych w pierwszej kolejności. Pozwala nam to już na samym początku zredukować liczbę słów, a co za tym idzie stopień skomplikowania kodu. Ze względu na charakter pracy takiego interpretera warto zrobić to jak najszybciej. Dzięki temu po zredukowaniu gramatyki `word -> number` operujemy juz tylko na słowach.


Jak widać każde słowo jest najpierw obsługiwane specjalnym handlerem `handle_word`. Obsługuje on wszystkie słowa składające się na proste wyrażenia w kodzie, takie jak:

* zagnieżdżone wywołania procedur
* operacje na zmiennych
* obsługę końca linii


Szczególnie ten ostatni podpunkt jest ważny. Koniec linii oznacza koniec łańcucha wywołań, a więc zdjęcie ze swosu wszystkich pozostałych argumentów i procedur i wywołanie ich jeśli to tylko możliwe. Jeśli jakakolwiek funckja pozostanie na stosie to możemy zwróćić błąd parsera `StackCorruption` oznaczający niewystarczającą liczbę argumentów w ostatnio obsługiwanej linii kodu.



---


## Obsługa słów

Handler słów najpierw musi zdecydować czy dane słowo to procedura czy wartość. To znowu dzięki wczesnemu wciąganiu danych do skryptu możemy mieć taki prosty podział. W przypadku procedury (słowo znajduje się na liście procedur) pobierana jest ilość arugmentów danej procedury i jest ona wrzucana na górę stosu razem z meta danymi potrzebnymi później do jej wywołania. Każda struktura na stosie ma spacjalną listę do któej są dodawane kolejne obsłużone słowa. Ostatnie wymagane słowo wyzwala wywołanie procedury i ściąga procedurę ze stosu wrzucając jego wynik na listę argumentów kolejnej (czyli poprzedniej) procedury.




---


## Instrukcje warunkowe
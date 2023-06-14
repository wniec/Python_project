## Podsumowanie projektu
#### Bartosz Hanc

W projekcie byłem odpowiedzialny w całości za warstwę graficzną aplikacji i interfejs użytkownika
oraz w części za silnik gry. Uważam, iż w przypadku warstwy graficznej udało mi się całkiem dobrze
zamknąć poszczególne komponenty GUI w osobnych modułach/klasach i uniezależnić je od siebie
umożliwiając łatwą ich zmianę bez konieczności wprowadzania zmian w całym kodzie. Jednocześnie muszę
stwierdzić, iż ręczne tworzenie typowych elementów GUI (button, checkbox, context menu) w
menu/widoku gry było raczej niepotrzebne, gdyż mogłem wykorzystać istniejące biblioteki np.
[`pygame_gui`](https://github.com/MyreMylar/pygame_gui), co z pewnością znacznie ułatwiłoby i
przyspieszyło proces ich tworzenia. W przypadku silnika gry niestety nie udało się w pełni
zrealizować początkowej koncepcji w ramach której stan gry (tj. położenie figur na planszy, zbite
figury, czas) mógłby być kontrolowany poprzez "publiczne" (bez __) metody wywoływane **jedynie** w
reakcji na interakcję użytkownika (np. przesunięcie figury na inne pole). Ze względu na
implementację bota potrzebne były metody, które niezależnie modyfikują stan gry, aby znaleźć kolejny
ruch bota, a następnie cofają tę modyfikację. Nie jest to rozwiązanie idealne, gdyż może prowadzić
do runtime errors, które ciężko wychwycić.

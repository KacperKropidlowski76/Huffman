class Wezel:
    def __init__(self, znak, czestotliwosc):
        self.znak = znak
        self.czestotliwosc = czestotliwosc
        self.lewy = None
        self.prawy = None

def porownaj_wezly(wezel1, wezel2):
    return wezel1.czestotliwosc < wezel2.czestotliwosc

class KolejkaPriorytetowa:
    def __init__(self):
        self.kopiec = []

    def dodaj(self, wezel):
        self.kopiec.append(wezel)
        self.buildheap()

    def pobierz(self):
        if len(self.kopiec) == 1:
            return self.kopiec.pop()

        korzen = self.kopiec[0]
        self.kopiec[0] = self.kopiec.pop()
        self.przesun_w_gore(0)
        return korzen

    def __len__(self):
        return len(self.kopiec)

    def buildheap(self):
        n = len(self.kopiec)
        for i in range(n-1, -1, -1):
            self.przesun_w_gore(i, n)

    def przesun_w_gore(self, i, n=None):
        if n is None:
            n = len(self.kopiec)

        lewy = (2 * i) + 1
        prawy = (2 * i) + 2
        najmniejszy = i

        while True:
            if lewy < n and self.kopiec[lewy].czestotliwosc < self.kopiec[najmniejszy].czestotliwosc:
                najmniejszy = lewy

            if prawy < n and self.kopiec[prawy].czestotliwosc < self.kopiec[najmniejszy].czestotliwosc:
                najmniejszy = prawy

            if najmniejszy != i:
                temp = self.kopiec[i]
                self.kopiec[i] = self.kopiec[najmniejszy]
                self.kopiec[najmniejszy] = temp
                i = najmniejszy
                lewy = (2 * i) + 1
                prawy = (2 * i) + 2
            else:
                break

def policzCzestotliwosci(tekst):
    czestotliwosci = {}
    for znak in tekst:
        if znak in czestotliwosci:
            czestotliwosci[znak] += 1
        else:
            czestotliwosci[znak] = 1
    return czestotliwosci


def zbudujDrzewo(czestotliwosci):
    kolejka = KolejkaPriorytetowa()
    for znak, czest in czestotliwosci.items():
        wezel = Wezel(znak, czest)
        kolejka.dodaj(wezel)

    while len(kolejka) > 1:
        lewy = kolejka.pobierz()
        prawy = kolejka.pobierz()

        nowyWezel = Wezel(None, lewy.czestotliwosc + prawy.czestotliwosc)
        nowyWezel.lewy = lewy
        nowyWezel.prawy = prawy

        kolejka.dodaj(nowyWezel)

    return kolejka.pobierz()


def generujKody(korzen):
    stos = [(korzen, "")]
    kody = {}

    while len(stos) > 0:
        wezel, aktualnyKod = stos.pop()

        if wezel.znak is not None:
            kody[wezel.znak] = aktualnyKod

        if wezel.prawy is not None:
            stos.append((wezel.prawy, aktualnyKod + "1"))#na prawo sa 1

        if wezel.lewy is not None:
            stos.append((wezel.lewy, aktualnyKod + "0"))#na lewo są 0

    return kody


def kodowanie(tekst):
    czestotliwosci = policzCzestotliwosci(tekst)
    korzen = zbudujDrzewo(czestotliwosci)
    kody = generujKody(korzen)

    zakodowanyTekst = "".join(kody[znak] for znak in tekst)

    return zakodowanyTekst, kody


def dekodowanie(zakodowanyTekst, kody):
    odwrotneKody = {}
    for klucz, wartosc in kody.items():
        odwrotneKody[wartosc] = klucz

    odkodowanyTekst = ""
    aktualnyKod = ""
    for bit in zakodowanyTekst:
        aktualnyKod += bit
        if aktualnyKod in odwrotneKody:
            odkodowanyTekst += odwrotneKody[aktualnyKod]
            aktualnyKod = ""

    return odkodowanyTekst


def zapiszDoPliku(nazwaPliku, naglowek, zakodowanyTekst):
    with open(nazwaPliku, "wb") as plik:
        naglowekBajtowy = naglowek.encode("utf-8")
        plik.write(len(naglowekBajtowy).to_bytes(4, byteorder="big"))
        plik.write(naglowekBajtowy)
        dlugoscZakodowanego = len(zakodowanyTekst)
        plik.write(dlugoscZakodowanego.to_bytes(4, byteorder="big"))
        zakodowanyBajty = int(zakodowanyTekst, 2).to_bytes((dlugoscZakodowanego + 7) // 8, byteorder="big")
        plik.write(zakodowanyBajty)


def wczytajZPliku(nazwaPliku):
    with open(nazwaPliku, "rb") as plik:
        rozmiarNaglowka = int.from_bytes(plik.read(4), byteorder="big")
        naglowek = plik.read(rozmiarNaglowka).decode("utf-8")
        dlugoscZakodowanego = int.from_bytes(plik.read(4), byteorder="big")
        zakodowanyBajty = plik.read()
        zakodowanyTekst = bin(int.from_bytes(zakodowanyBajty, byteorder="big"))[2:]
        zakodowanyTekst = zakodowanyTekst.zfill(dlugoscZakodowanego)#0
        return naglowek, zakodowanyTekst


if __name__ == "__main__":
    opcja = input("Wybierz opcję: [1] Kodowanie, [2] Dekodowanie: ")

    if opcja == "1":
        while True:
            nazwaPliku = input("Podaj nazwę pliku do zakodowania: ")
            try:
                with open(nazwaPliku, "r") as plik:
                    tekst = plik.read().rstrip("\n")
                break
            except FileNotFoundError:
                print("Brak pliku")

        zakodowanyTekst, kody = kodowanie(tekst)

        naglowek = ""
        for znak in kody:
            kod = kody[znak]
            element_naglowka = f"{repr(znak)}:{kod}"
            if naglowek:
                naglowek += "|"
            naglowek += element_naglowka

        plikWyjscie = input("Podaj nazwę pliku wyjściowego: ")
        zapiszDoPliku(plikWyjscie, naglowek, zakodowanyTekst)

        print("Zakodowano i zapisano do pliku")

    elif opcja == "2":
        while True:
            nazwaPliku = input("Podaj nazwę pliku do odkodowania: ")
            try:
                naglowek, zakodowanyTekst = wczytajZPliku(nazwaPliku)
                break
            except FileNotFoundError:
                print("Brak pliku")

        kody = {}
        podzielony_naglowek = naglowek.split("|")
        for element in podzielony_naglowek:
            if ":" in element:
                podzielony_element = element.split(":")
                znak = podzielony_element[0]
                kod = podzielony_element[1]
                znak = znak.strip("'\"")
                kody[znak] = kod

        odkodowanyTekst = dekodowanie(zakodowanyTekst, kody)

        plikWyjscie = input("Podaj nazwę pliku wyjściowego: ")
        with open(plikWyjscie, "w") as plik:
            plik.write(odkodowanyTekst)

        print("Odkodowano i zapisano")
    else:
        print("Nieprawidłowy wybór.")


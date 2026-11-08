import os 
import re 
import pandas as pd 
import requests
from bs4 import BeautifulSoup
import unicodedata

# URL adresa pro Maxa ligu na Hokej.cz
url = "https://www.hokej.cz/maxa-liga/zapasy?matchList-view-displayAll=1&t=7r1isgajus1e1qxb7s39llv0y74mgqobmeemcg95s2iu1f3ep7mtewq..%2F..%2F..%2FKR-ELH-2020-21-treneri-rozhodci-divaci-2020-09-15.pdf&matchList-filter-season=2026&matchList-filter-competition=7563"

print("Stahuji data z webu Hokej.cz...")

try:
    response = requests.get(url)
    response.raise_for_status()
except Exception as e:
    print(f"Chyba při stahování stránky: {e}")
    exit()

soup = BeautifulSoup(response.text,"html.parser")
zapasy_list = []
aktualni_kolo = None 

# funkce, ktera nam z nazvu odstrani diakritiku 
def odstran_diakritiku(text):
    if not text:
        return ""
    nfkd_form = unicodedata.normalize('NFKD',text)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

# nyni budeme prvek po prvku prochazet stranku 
vsechny_prvky = soup.find_all(["h2","tr","td"])
print(f"Nalezeno {len(vsechny_prvky)} prvku k analyze.")

for prvek in vsechny_prvky:
    # sledovani cisla kola, trida <h2> 
    if prvek.name == "h2":
        text_kola = prvek.text.strip()
        cisla_v_nadpisu = re.findall(r"\d+", text_kola)
        if cisla_v_nadpisu:
            aktualni_kolo = int(cisla_v_nadpisu[0])
        continue

    # vytahovani dat z jednotlivych radku reprezentujici utkani 
    if prvek.name == "tr" and prvek.has_attr("class"):
        tr_classes = " ".join(prvek["class"])
        if "js-preview__link" in tr_classes:
            try:
                # --- EXTRAKCE NAZVU TYMU ---
                # extrakce nazvu tymu z bunek s <td> a prislusnou tridou preview__name         
                tymy_td = prvek.find_all("td",class_=re.compile(r"preview__name"))
                if len(tymy_td) < 2:
                    continue 

                # vytahneme ze <span> plny nazev 
                domaci_span = tymy_td[0].find("span",class_=re.compile(r"preview__name--long"))
                hoste_span = tymy_td[1].find("span",class_=re.compile(r"preview__name--long"))

                domaci_raw = (
                    domaci_span.text.strip()
                    if domaci_span
                    else tymy_td[0].text.strip()
                )
                hoste_raw = (
                    hoste_span.text.strip()
                    if hoste_span
                    else tymy_td[1].text.strip()
                )

                # tady zavolame funkci na odstraneni diakritiky 
                domaci = odstran_diakritiku(domaci_raw)
                hoste = odstran_diakritiku(hoste_raw)

                score_domaci_td = prvek.find("td",class_="preview__score")
                score_hoste_td = prvek.find("td",class_="preview__score--right")

                goly_domaci_celkem = None 
                goly_hoste_celkem = None 

                # Domaci skore 
                if score_domaci_td:
                    blue_span_d = score_domaci_td.find("span",class_="blue")
                    if blue_span_d:
                        goly_domaci_raw = blue_span_d.text.strip()
                        if goly_domaci_raw.isdigit():
                            goly_domaci_celkem = int(goly_domaci_raw)

                # Hoste skore 
                if score_hoste_td:
                    blue_span_h = score_hoste_td.find("span",class_="blue")
                    if blue_span_h:
                        goly_hoste_raw = blue_span_h.text.strip()
                        if goly_hoste_raw.isdigit():
                            goly_hoste_celkem = int(goly_hoste_raw)
                
                # --- EXTRAKCE TRETIN ---
                # extrakce vysledku jednnotlivych tretin <td>/<span> s tridou preview_period 
                period_td = prvek.find("td",class_=re.compile(r"preview__period"))

                t1_d = t1_h = t2_d = t2_h = t3_d = t3_h = None 
                prodlouzeni_hrano = 0
                najezdy_hrano = 0
                goly_domaci_navic = None 
                goly_hoste_navic = None
                stav = "neodehrano"

                # tady identifikujeme prvek <span>, ktery je vnoreny do <td> a snazime se najit ten, ktery obsahuje vysledek utkani po tretinach 
                if period_td:
                    spany = period_td.find_all("span")
                    detail_text = ""
                    for s in spany:
                        if "(" in s.text and ")" in s.text:
                            detail_text = s.text.strip()
                            stav = "odehrano"
                            break 

                    if stav == "odehrano" and detail_text: 
                        try:
                            # jdeme cistit vysledky od zavorek 
                            detail_clean = detail_text.replace("(","").replace(")","").strip()
                            
                            # ted to rozdelime podle pomlcek 
                            casti = [c.strip() for c in detail_clean.split("-") if c.strip()]

                            if casti:
                                # Rozbor podle toho, jestli zapas skoncil po zakladni casti nebo jestli sel do prodlouzeni nebo najezdu 
                                tretiny = [t.strip() for t in casti[0].split(",") if t.strip()]
                                if len(tretiny) >= 3:
                                    t1_d, t1_h = map(int, tretiny[0].split(":"))
                                    t2_d, t2_h = map(int, tretiny[1].split(":"))
                                    t3_d, t3_h = map(int, tretiny[2].split(":"))

                                # ted jdeme resit prodlouzeni 
                                if len(casti) == 2:
                                    prodlouzeni_hrano = 1
                                    najezdy_hrano = 0
                                    goly_domaci_navic, goly_hoste_navic = map(int, casti[1].split(":"))
                                
                                elif len(casti) == 3:
                                    prodlouzeni_hrano = 1
                                    najezdy_hrano = 1
                                    goly_domaci_navic, goly_hoste_navic = map(int, casti[2].split(":"))

                        except Exception as e_period:
                            print("varovani u parsovani tretin")

                if goly_domaci_celkem is not None and stav == "neodehrano":
                    stav = "odehrano" 
            
                # pridame radek do seznamu 
                zapasy_list.append({
                    "kolo":aktualni_kolo,
                    "domaci":domaci,
                    "hoste":hoste,
                    "goly_domaci_zaklad":goly_domaci_celkem,
                    "goly_hoste_zaklad":goly_hoste_celkem, 
                    "1tretina_domaci":t1_d, 
                    "1tretina_hoste":t1_h, 
                    "2tretina_domaci":t2_d,
                    "2tretina_hoste":t2_h,
                    "3tretina_domaci":t3_d,
                    "3tretina_hoste":t3_h,
                    "prodlouzeni":prodlouzeni_hrano,
                    "najezdy":najezdy_hrano,
                    "goly_domaci_nadstavba":goly_domaci_navic,
                    "goly_hoste_nadstavba":goly_hoste_navic,
                    "stav":stav,
                })
            
            except Exception as e:
                continue 
            
# ulozeni dat do Pandas Dataframe
df = pd.DataFrame(zapasy_list)

# sloupce, ve kterych jsou ciselne hodnoty prevedeme na typ Int64 (cislo tolerujici null/NaN values ve sloupci)
numeric_cols = [
    "kolo", "goly_domaci_zaklad", "goly_hoste_zaklad", 
    "1tretina_domaci", "1tretina_hoste", "2tretina_domaci", "2tretina_hoste", 
    "3tretina_domaci", "3tretina_hoste", "prodlouzeni", "najezdy", 
    "goly_domaci_nadstavba", "goly_hoste_nadstavba"
]

for col in numeric_cols:
    if col in df.columns:
        df[col] = df[col].astype("Int64")
            
# pridame jeste index utkani (+1 aby zacinal od 1, python standardne cisluje od 0)
df.index = df.index + 1 
df.index.name = "id_zapasu"
            
# ulozeni tabulky
df.to_csv("C:/Users/Ruda/Documents/dat_analyza/maxa_liga_2026_zapasy.csv",index=True)
print("Data stazena a ulozena.")
print(df.head())

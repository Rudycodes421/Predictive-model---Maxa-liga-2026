import unicodedata 
from bs4 import BeautifulSoup
import pandas as pd 
import requests 

# odstranime diakritiku, aby s tim CSV file nemel problem 
def odstran_diakritiku(text):
    if not text:
        return ""
    nfkd_form = unicodedata.normalize("NFKD",str(text))
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

# odkaz na stranku s tabulkou 
url = "https://www.hokej.cz/maxa-liga/table"

try:
    response = requests.get(url)
    response.raise_for_status()
except Exception as e:
    print(f"Chyba při stahování stránky: {e}")
    exit()

soup = BeautifulSoup(response.text,'html.parser')
table = soup.find("table",{"class":"table-soupiska"})

if table:
  # Ruční parsování tabulky přes BeautifulSoup (bez nutnosti lxml/html5lib)
  data = []
  for row in table.find_all("tr"):
    cols = row.find_all(["th", "td"])
    cols = [ele.text.strip() for ele in cols]
    data.append(cols)

  df = pd.DataFrame(data)
  if not df.empty:
    df.columns = df.iloc[0]
    df = df[1:].reset_index(drop=True)

    # rozdelime sloupec "SKORE" na dva 
    # 1. Důkladně očistíme názvy sloupců od skrytých mezer a neviditelných znaků
    df.columns = df.columns.str.strip()

    # 2. Najdeme sloupec, který v sobě obsahuje "SKÓRE" (bez ohledu na skryté detaily)
    skore_col = next(
          (col for col in df.columns if "SKÓRE" in str(col).upper()), None
    )

    if skore_col is not None:
        idx = df.columns.get_loc(skore_col)

        # 3. Rozdělíme řetězec typu "68:30" podle dvojtečky na dvě čísla
        skore_rozdelene = (
            df[skore_col]
            .astype(str)
            .str.strip()
            .str.split(":", expand=True)
            .astype(int)
        )

    # 4. Vložíme nové sloupce na pozici původního skóre a původní smažeme, inkasovane goly chceme az jako dalsi sloupec, proto idx + 1 
    df.insert(idx, "vstrelene_goly", skore_rozdelene[0])
    df.insert(idx + 1, "inkasovane_goly", skore_rozdelene[1])
    df = df.drop(columns=[skore_col])

    # Teď už má tabulka správný počet sloupců, přiřadíme definitivní názvy
    # (musíme vynechat "skore" z našeho seznamu a rozdělit na vstrelene_goly a inkasovane_goly)
    nove_nazvy = [
        "poradi",
        "tym",
        "odehrane_zapasy",
        "vyhrane",
        "vyhrane_nastaveni",
        "prohrane_nastaveni",
        "prohrane",
        "vstrelene_goly",
        "inkasovane_goly",
        "body",
        "strely_na_branku_avg",
        "strely_na_branku_proti_avg",
        "presilovky_pocet",
        "presilovky_goly",
        "presilovky_vyuziti",
        "oslabeni_pocet",
        "oslabeni_inkasovane_goly",
        "oslabeni_ubraneni_usp",
        "oslabeni_vstrelene_goly",
        "vhazovani_uspesnost",
        "hity",
        "trestne_minuty",
    ]

    # zkontrolujeme delky sloupcu z puvodni tabulky a s novymi nazvy 
    if len(nove_nazvy) == len(df.columns):
        df.columns = nove_nazvy
    else: 
        print(f"Pocet novych sloupcu ({len(nove_nazvy)}) nesouhlasi s" 
              f"poctem sloupcu v puvodni tabulce: ({len(df.columns)}).")

    # zavolame funkci na odstraneni diakritiky 
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].apply(odstran_diakritiku)

    # ulozeni dat do CSV souboru, oddelovac carka 
    output_file = "C:/Users/Ruda/Documents/dat_analyza/maxa_liga_2026_tabulka.csv"
    df.to_csv(output_file, index=False, encoding="utf-8-sig",sep=",")
    print(df.head())
    print(f"Data byla ulozena do souboru {output_file}.")

else:
    print("Vyskytla se chyba.")


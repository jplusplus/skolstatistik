# Operation: Rädda skolstatistiken

Den 1 september 2020 tvingas Skolverket avpublicera all skolstatistik som inte är på riksnivå. Vi kan därefter med andra ord inte veta något om hur behörighetsnivån i personalen skiljer sig åt i olika delar av landet eller vilka betyg elever snittar i olika skolor.  

För att rädda det som räddas kan försöker vi hämta hem så mycket av de nu tillgängliga statistiken som möjligt och göra den publikt tillgänglig för forskare, journalister, politiker och allmänhet också efter den 1 september 2020.

Det här repot samlar [_länkar_](https://github.com/jplusplus/skolstatistik/blob/master/datasets.csv) till nedladdade dataset, samt Python-kod för att själv göra om nerladdningen (eller se hur vi gjorde). Filerna ligger på Amazon molntjänst AWS S3.

## Dataset

Du hittar en förteckning över [samtliga i dataset här](https://github.com/jplusplus/skolstatistik/blob/master/datasets.csv).

### Från Siris-databasen

Från [Siris sökgränssnitt](https://siris.skolverket.se/siris/ris.export_stat.form) har vi hämtat all statistik aggregerad per skola, kommun eller huvudman. En fil består av uppgifter för alla huvudmän, skolor, eller kommuner för ett givet läsår. Till exempel lärarbehörigheten per kommun i grundskolan ett visst läsår.

Filerna finns i tre format: csv, Excel och XML. De sparas till en mappstruktur som följer följande mönster:

- `siris/[Skolnivå]/[Statistikområde]/[CSV|EXCEL|XML]/[År]-[uttag].[csv|xlsx|csv]`

Vi hämtar endast filer som aggregerar statistik för flera skolor, huvudmän eller kommuner till en fil. Sammanställningar av typen "all statistik för Bjuvs kommun" saknas med andra ord.

### Från Jämförelsetal (Artisan)

Från http://www.jmftal.artisan.se/ har vi hämtat all data för alla kommuner, län och kommungrupper i csv-format. Länkar till datan finns i `./artisan.csv`.

### Från Skolenhetsregistret

Det översiktliga Excelarket finns i [/data](/data)-mappen

Detaljerad data om varje skolenhet, den första januari, april, juli och oktober varje år, finns i json-filer på följande format:
`https://skolverket-statistik.s3.eu-north-1.amazonaws.com/skolenhet/{SKOLENHETS-ID}/{ÅÅÅÅMMDD}.json`, till exempel [https://skolverket-statistik.s3.eu-north-1.amazonaws.com/skolenhet/10110104/20200101.json](https://skolverket-statistik.s3.eu-north-1.amazonaws.com/skolenhet/10110104/20200101.json)

### Skolverkets API (Swagger)

Alla enkäter till elever och vårdnadshavare (Skolinspektionens skolenkät), som json-filer. Dessa ligger som json-filer på Amazon AWS S3.

Länkar till filerna finns i `./swagger.csv`.

## Ladda ner data själv

Du kan själv ladda ner motsvarande data med Python-skripten.

### `download_siris.py`
Installera först de paket som behövs med `pip install -r requirements/python2.txt`.

`download_siris.py` måste köras med Python 2.7 på grund av beroende av paketet [siris_scraper](https://pypi.org/project/siris-scraper/), som vi själva utvecklat tidigare för att skrapa data från Skolverket.

### `download_skolenhetsregistret.py`
Installera först de paket som behövs med `pip3 install -r requirements/python3.txt`.

Ange en S3-bucket i `settings.py`, och kör `./download_skolenhetsregistret.py`

### `download_artisan.py`
Installera först de paket som behövs med `pip3 install -r requirements/python3.txt`.

Den här skrejpern använder Selenium, och kräver en [https://selenium-python.readthedocs.io/installation.html#drivers](webbläsar-driver) installerad. På Ubuntu kan du installera Gecko med `sudo apt-get install firefox-geckodriver`.

(Om du vill använda en annan driver kommer du behöva modifiera nerladdningsinställningarna, så att alla filer hamnar där vi hittar dem.)

Kör sedan `./download_artisan.py`

## Vem ligger bakom insamlingen?

Vi som gör insamlingen är datajournalister på [J++ Stockholm](https://jplusplus.org/sv/) och [Newsworthy](https://www.newsworthy.se/sv).

## Andra projekt

Vi är många journalister, forskare och andra som laddar ner data från Skolverket just nu. Förhoppningsvis finns det en komplett samling där ute i månadsskiftet, även om någon missat något. Här är länkar till andra projekt vi känner till:

<dl>
<dt><a href="https://tankesmedjanbalans.se/skolverkets-statistik-for-skolaret-2019-2020/">Tankesmedjan Balans</a>
<dd>Sammanställd statistik för utvalda huvudmän, skolor och kommuner (ingen rådata, men lättläst för den som inte programmerar)

<dt><a href="https://drive.google.com/drive/folders/1OXALrZKW2HmyVbUjv-WR5jNiwu97pykr?usp=sharing">Staffan Betnér, statistiker</a>
<dd>Zip-arkiv med Excel-, CSV- och XML-filer i överskådlig mappstruktur
</dl>

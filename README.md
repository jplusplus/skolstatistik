# Operation: Rädda skolstatistiken

Den 1 september 2020 tvingas Skolverket avpublicera all skolstatistik som inte är på riksnivå. Vi kan därefter med andra ord inte veta något om hur behörighetsnivån i personalen skiljer sig åt i olika delar av landet eller vilka betyg elever snittar i olika skolor.  

För att rädda det som räddas kan försöker vi hämta hem så mycket av de nu tillgängliga statistiken som möjligt och göra den publikt tillgänglig för forskare, journalister, politiker och allmänhet också efter den 1 september 2020.

Det här repot samlar länkar till nedladdningsbara dataset, samt Python-kod för att ladda ner data från Skolverket.

## Dataset

Du hittar en förteckning över samtliga i dataset här (eller här i csv-format).

### Från Siris-databasen

Från [https://siris.skolverket.se/siris/ris.export_stat.form](Siris sökgränssnitt) har vi hämtat all statistik aggregerad per skola, kommun eller huvudman. En fil består av uppgifter för alla huvudmän, skolor, eller kommuner för ett givet läsår. Till exempel lärarbehörigheten per kommun i grundskolan ett visst läsår.

Filerna finns i tre format: csv, Excel och XML. De sparas till en mappstruktur som följer följande mönster:

- `siris/[Skolnivå]/[Statistikområde]/[CSV|EXCEL|XML]/[År]-[uttag].[csv|xlsx|csv]`

Vi hämtar endast filer som aggregerar statistik för flera skolor, huvdmän eller kommuner till en fil. Sammanställningar av typen "all statistik för Bjuvs kommun" saknas med andra ord.

### Från Jämförelsetal

TODO: Hämta data från http://www.jmftal.artisan.se/


## Ladda ner data själv

Du kan själv ladda ner motsvarande data med Python-skriptet `download_siris.py`.

`download_siris.py` måste köras med Python 2.7 på grund av beroende av paketet [https://pypi.org/project/siris-scraper/](siris_scraper), som vi själva utvecklat tidigare för att skrapa data från Skolverket.

## Vem ligger bakom insamlingen?

Vi som gör insamlingen är datajournalister på [https://jplusplus.org/sv/](J++ Stockholm) och [https://www.newsworthy.se/sv](Newsworthy).

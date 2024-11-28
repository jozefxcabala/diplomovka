# AnomalyCLIP - NOTES (https://github.com/lucazanella/AnomalyCLIP)
- "manipulating the laten CLIP feature space to identify the normal event subspace...." - CLIP obsahuje priestor tzv. "latentny priestor" ktory vyuziva na to aby si vytvaral suvislosi medzi napr textovymi a obrazovimi informaciami, v AnomalyCLIP sa snazia tento priestor zmanipulovat tak, aby identifikovali ten priestor, ktory zahrna normalne udalosti a tak by vedeli vsetky abnormalne udalosti dat na kraj tychto
- "when anomalous frames are projecte onto these directions, they exhibit a large feature magnitude if they belong to a particular class." - cize ak nejaka udalost patri do nejakej triedy anomalie tak ukazuju "large feature magnitude" prave pri triede do ktorej patria
- "We also introduce a computionally effecient Transformer architecture to model short and long term temporal dependecies between frames, ultimately producing the final anomaly score and class prediction probabilieties." - vyvinuli Transformer, ktory vlastne pozoruje kratkodobe a dlhodobe vztahy medzi frames a na zaklade nich sa snazi urcit vysledne skore anomalie a vytvori pravdepodobnosti prislusnosti danej anomalie do danej triedy
- VAD - Video Anomaly Detection - toto zvladali doterajsie weakly-supervised VAD
- VAR - Video Anomaly Recognition - na toto sa zamerali 
- hovoria tu o vysokom vyuziti Large Language and Vision Models alebo Foundation Models (CLIP patri pod obe - a vsetky LLVM patri pod Foundation) (tieto modely su volne dostupne - teda aspon CLIP)
- tvrdia, ze vyuzitim LLVM modelov vieme ziskat lepsie informacie, pomocou ktorych vieme lepsie rozlisit abnormalne spravanie
- diskriminativne vlastnosti - vlasntosti ktore pomocou ktorych rozlisujeme prislusnost do tried
- vyuzivaju CLIP model (priradovanie video reprezentacie k jej textovemu popisu , vyuzvivanie tohto prepojenia na zhlukovanie okolo nejakeho bodu normality)
- Selector model - prompt learning a projection operator - ??? selector model s prompt learningom sa uci lepsie prisposbovat textovy opise aby lepsie dokazali identifikovat relevantne casti videa -  ten projection operator sa pravdepodobne snazi vo videu najst frames, ktore najlepsie odpovedaju popisu textovemu
- predikcie tohto Selector modelu vyuzivaju na implementaciu semantically-guided Multiple Instance Learning (MIL) - je technika strojoveho ucenia kedy sa model uci zo skupiny instancii (napr. videosekvencii alebo snimok) a rozhoduje sa na zaklade celej skupiny a nie len na zaklade jednotlivych instancii
- Temporal Model - implementovany ako Axial Transfromer - tento model sa vyuziva na spracovanie kratkodobych a dlhodobych vztahov
- MIL - bolo tam kratke vysvetlenie z povodneho paper
- vravia, ze podla ich vedomosti ziadne z doterajsich rieseni nepreskumavalo pouzitie Foundation Models k VAR
- LLVm - aj napriek ich jednoduchosti, dosahuju vynikajuce vysledky pri "zero shot generaliztion capabilities"
- VideoCLIP - priklad toho ako sa to vyuziva a odkaz na clanok
- ActionCLIP - popisuju, ze vyuzitie na vyhladavanie anomalii zlyhavalo (pre mna to ale znie ako zaujimavy model) - presne preto je jednym z hlavnych cielov tejto prace modifikovat CLIP feature space tak aby dokazal detekovat tie anomalie a rozpoznat ich
- potom je tam vysvetlene ako vlastne dany AnomalyCLIP funguje 
  - MIL - vypocitava pravdepodobnost kazdeho frame na kolko je anomalny a nasledne vybertie tie najviac anomalne a maximalizuje rozdiel v predikcii pravdepodobnost medzi tymi normalnymi frames a tymi ktore boli vybrate za tie najviac anomalne
  - popisuju co vlastne dokaze ich CLIP (detekovat anomalie, rozpoznat ich typ a zaroven vravia ze je to mozne len po modifikacia CLIP Feature Space)
  - ich metoda sa sklada z dvoch modelov Selector Model a Temporal Model
  - Selector Model -  produkuje pravdepodobnost s akou patri nejaky frame do do triedy danej anomalie 
  - popisuju tu CoOp Promt Learning approach
  - Temporal Model - vyuziva temporal information na zlepsenie predikcii, vyuziva sa Transformer network
  - tieto predikcie su potom agregovane (spojene dokopy) na to aby sme urcili ci je frame abnormalny alebo normalny a do akej triedy patri
  - dalej je tu popisane ako vlastne vytvorili Normality Prototype ako priemer zo vsetkych vlastnosti, ktore Image Encoder extrahoval z videy oznacenych ako normalne
  - dalej sa tam pise o tom ako sa jednotlive predikcie zo Selector a Temporal Modelu agreguju

TO DO 
- work with this model

TO ASK
- ITS OKEY

TO LEARN
- Transformery
- CLIP ako funguje
- Large Language and Vision models
- MIL - Multiple Instance Learning
- Prompt learning
- Axial Transformer
- ActionCLIP

WHAT THIS MEAN FOR ME?
- skusit v diplomovej praci fakt vyuzit CLIP
- potrebujem nieco co bude urcovat pravdepodobnost
- chcem hladat anomalie? co ak by som hladal:
  - to ci sa stane nieco zaujimave v nejakom vyreze (to je to iste)
  - co ak by som hladal nieco co sa podoba situacii ktoru zadam ja? (stalo by zato precitat ActionCLIP, zistit ako funguje XCLIP na detekovanie napr cerveneho pana a aky kvalitny zaznam potrebujem)
- otestovat AnomalyCLIP, ActionCLIP, XCLIP

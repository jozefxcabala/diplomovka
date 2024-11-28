# Surveillacne video search (poznamky z bakalarskej prace - 22439.pdf)
- 3 piliere systemu, ktory sluzi na vyhladavanie v bezpecnostnych zaznamoch 
    - databaza (uchovava info)
    - analyzator videa (algoritmus na detekciu objektov + ich nasledne trackovanie)
    - uzivatelske rozhranie (specifikovanie kde sa ma objekt vyskytnut (pomocu kreslenia ciar), alebo popis objektu pomcou jeho popisu s vyuzitim prirodzeneho jazyka)
- tento system konkretne vyuziva skladanie vyhladavacich blokov (na zlozenie toho aky objekt sa ma najst)
- tento system je vytvoreny tak aby sa postupne dal obohacovat o dalsie vyhladavacie bloky 
- NAPAD: detekovanie objektu, ktory sa dostal z bodu A do bodu B, specifikacia vyzoru cloveka - specifikovat kde sa nachadzal a ktorym smerom sa vidal
- je rozdiel ci mam zabery z dialnice, ci z nakupneho strediska (ten system je potom rozny)  --- TODO - to si treba urcit
- ked si to predstavim ja tak to funguje asi tak, ze ja video hodim do analyzatora, ten ho spracuje - ulozi veci do db a nasledne cez uzivatelkse prostredie vyhladava v DB a vracia ti na obraz konkretne sekvencie videa (tipujem ze si zaznaci aj nejaky timestamp z toho videa)
- systemy, ktore analyzuju v realnom case vs. systemy ktore potrebuju viac casu na analyzu (asi sa priklanam k tomu 2. typu)
- video databaza - uklada dany usek kde sa nachadza ta extrahovana vlastnost, ktora bola analyzovana a ulozena do DB
- TODO - potrebujem sa zamerat na existujuce open source nastroje - vyskusat ich, popisat ich +- (v com by sa moj odlisoval od ich)
- nastroj Axxonsoft - funguje asi tak ze zadas sipku, popises co to je za udalost a ak nejaky objekt tu udalost splni tak sa zaznamena (DA SA TO SPRAVIT AJ INAK???)
- NAPAD: sprav system (user interface), ktory je intuitivny a nie je potrebne sa ucit ako funguje
- nastroj CAMIO  - funguje tak ze uzivatel zada len vetu a z nej sa extrahuju podstatne znaky
- je tu popisanych viacero sposobov, ako ulozit detekovane eventy do tabuliek 
- je tu popisanych viacero sposobov ako detekovat objekty, ako hodnotit uspesnost
- TODO - pochopit HYPERPLANE pri SVM (vyuziva sa tu na detekciu objektvo HOG)
- HOG - problem pri roznych uhloch - to riesi SIFT (Scale Invariant Feature Transform)
- TODO - pochopit SIFT
- poouzite CNN pre Object Detection, YOLO ako zastupca CNN pre Object Detection (zvysuje rychlsot oproti ostatnym pristupom - lebo sa na obrazok pozrie ako na celok raz)
- YOLO ma vraj problem s detekciou malych objektov (TO BY SOM ALE JA ASI NEMAL RIESIT V SVOJEJ DIPLOMOVKE)
- NAPAD (detekcia ludi v aute, kolko ich tam je --- to ale asi na kamere nebude vidno)
- TODO - co je Homography matrix - je matematicka transformacia, ktora umozni mapovat jeden obrazok z jednej roviny na obrazok do druhej roviny tak aby sa zachovala perspektiva = UZITOCNE PRI TRACKOVANI OBJEKTOV - TODO pochopit ako sa vypocitava Homography Matrix
- TODO - nastudovat Object tracking v ramci jedneho snimku (kamery) vs. Object tracking medzi kamerami
- vysvetlenie Deep Sort algoritmu - TODO pochopit - Kalman Filter (viem pomocou toho predikovat smer pohybu), Mahalanobis distance (tam kde nestaci euklidova vzdialenost vzhladom na normal distribution), Cosine similarity (ako su si vektory podobne)
- trackovanie objektov: DeepSort a GOTURN
- je rozdiel pri trackovani online a offline - lebo pri trackovani offline viem vyuzit aj frames, ktore su po tom aktualnom frames pricom pri online vyuzivam len tie z minulosti
## Implementacia
- urcil si ze sa zamera na offline vyhladavanie
- ide o webovu aplikaciu - pricom vypocty prebiehaju na servery a len sa pristupuje k vysledkom (dobre riesenie)
- urcil si nejake predefinovane bloky, na zaklade ktorych sa da vyhladavat (ZAUJIMAVE - vie preratat vzdialenost od objektu)
- zvolil si Python a Flask (Django je asi tiez dobre)
- vyuziva InfluxDB (logicke ved pracuje s casom)
- vyuziva OpenCV klasika
- ma tu vysvetlenie ako vlastne su jednotlive bloky definovane
- mal tu popisane ako testoval aplikaciu (zaujimave bolo ze testoval ako rychlo sa ju naucia uzivatelia pouzivat) 
- TODO - vedel by mi to poslat ten co to spravil? 

- POZRI ZDROJE: [5], [33], [26] (trackovanie objektov?), [8] (vypocet homography matrix)

# Analyza zaznamov bezpecnostnych kamier  (poznamky z bakalarskej prace - 22442.pdf)
- rozpisane co je to vlastne homografia a preco je dolezita
- rozpisane co je to vlastne perspektivna projekcia a preco je dolezita (meranie vzdialenosti a taketo srandy)

# Rozpoznavanie osob a jejich cinnosti vo videu z bezpecnostnych kamer (poznamky z bakalarskej prace - 23868.pdf)
- rozpisane ake technologie su pouzite na analyzu cinnosti cloveka vo videu: sledovanie trajektorie ludi, pozorovanie pohybu ich klbov, rozpoznavanie akcii pomocou extrakcie modelu cloveka
- taktiez rozlisuje rozpoznavanie akcii a ich predpovedanie
- vytvorit system, ktory je dostatocne vseobecny a bol by schopny rozpoznavat vsetky alebo aspon viacere druhy akcii je takmer nemozne (TODO: preto na ake akcie sa chcem zamerat ja?)
- popisuje konvolucnu operaciu 
- popisuje metodu SlowFast (Slow Pathway vs Fast Pathway)
- rozpoznavanie cinnosti na zaklade spajania informacii (konkretne v tejto praci ide o tieto: vzdialenost medzi objektami, porovnavanie uhla medzi objektami, vyskyt objektu v polygone, porovnavanie trajektorie)
- priklady clankov, kde sa riesi prave rozpoznavanie akcii
- popis ako vyzera vlastne objekt, ktory drzi vsetky tieto informacie 
- rozprava tu strednom bode objektu, smeru pohybu, rychlost pohybu (riesi vypocet)
- ukazuje moznost zadat miesto kade ma nejaky objekt prejst, alebo kde sa ma vyskytnut

# Co idem robit dalej na zaklade tychto informacii? 
- v prvom polroku sa chcem zamerat na vytvorenie riesenia - ktore bude schopne detekovat objekt (zrejme pomocou YOLO), trackovat dany objekt (pomocou DeepSort - zrejme) a analyzou cinnosti (pomocou spajania informacii ako to je vyssie - ZAROVEN SKUMAT MOZNOST VYUZITIA CLIPu)
- chcem sa zamerat na offline analyzu videy
- chcel by som aby tato analyza bezala na nejakom servery, nie priamo u uzivatela
- v druhom polroku by som sa chcel zamerat na vytvorenie uzivatelskeho prostredia
- zacinam studovat moznost vyuzitia X-Clip na analyzu cinnosti (detekovanie objektov - to by mohlo zjednodusit trenovanie na jednotlive situacie, treba to ale otestovat co to vsetko dokaze)
- AKTUALNE:
    - studujem toto [Action Clip](https://github.com/sallymmx/ActionCLIP)
    - studujem toto [Adapting CLIP for Action Recognition with Motion Prompts Learning](https://arxiv.org/abs/2308.04828)
    - studujem toto [ActionCLIP: A New Paradigm for Video Action Recognition](https://arxiv.org/abs/2109.08472)
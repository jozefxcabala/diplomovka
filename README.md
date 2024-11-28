# Rozpoznávání osob a jejich činnosti ve videu z bezpečnostních kamer

# Teraz pracujem na:
1. stáhnout existující datové sady do adresáře projektu, shromáždit hotová řešení (např. odkazovaná v článcích, pracující s konkrétními datovými sadami, z githubu, ...), zprovoznit je na stažených datových sadách a zkontrolovat, že výsledky (zhruba) odpovídají tomu, co píší autoři. Vyzkoušet také identifikaci lidí, případně i rozpoznání akcí chodců na videu v adresáři projektu.
2. Popsat omezení daného typu rozpoznávání vzhledem k velikosti osoby v obraze - např. určení identity na základě zadané fotky je možné, jen když je velikost obličeje osoby v obraze alespoň Y pixelů, naopak pro identifikaci skupin a akcí chodců ve videu (např. matka s dítětem přebíhají na červenou, aby stihli tramvaj) stačí velikost Z pixelů.
3. Zpracovat přehled dalších datových sad (pro reidentifikaci lidí ve videu, rozpoznávání jejich činnosti, případně kombinace rozpoznávání lidí s dalšími objekty a identifikaci "událostí" - typicky odložení zavazadla a vzdálení se od něj dále než o X metrů).

# Úlohy
- Seznámit se s moderními metodami rozpoznávání a využití předtrénovaných modelů CNN (konvolučních neuronových sítí), případně vizuálních transformerů. K tomu lze využít buď materiály z magisterského kurzu SUI, nebo, lépe, kurzy na Coursera a dalších platformách.
- Podívat se na možnosti propojení základní detekce (třeba systémem https://github.com/Deci-AI/super-gradients/blob/master/YOLONAS.md) s vyhledáváním a la X-CLIP (https://github.com/microsoft/VideoX/tree/master/X-CLIP).
- Podívat se také na výsledky předchozích absolventských prací blízkých tématu, např.
https://www.fit.vut.cz/study/thesis/23868
https://www.fit.vut.cz/study/thesis/22442
https://www.fit.vut.cz/study/thesis/22439,
a na zdroje odkazované v nich.
- Na wiki stránku projektu začít sepisovat přehled relevantních článků a dalších zdrojů, který později vytvoří základ pro kapitolu Rozbor řešené problematiky, jež se objeví v závěrečné technické zprávě. U každého zdroje napsat, čím je relevantní. Odborné články vyhledávat například na Google Scholar či Semantic Scholar.
- Během prvních 2 týdnů se rozhodnout, jakému konkrétnímu zaměření v rámci tématu se chcete věnovat (lze samozřejmě i v rámci konzultace). (DEADLINE 17.10.2024)   

# Nápady
- Nabízí se například propojení základní detekce (třeba systémem https://ultralytics.com/yolov8), sledování objektů ve scéně (viz např. https://viso.ai/deep-learning/object-tracking/) a vyhledávání (https://github.com/yzhuoning/Awesome-CLIP).
- Důraz může být také kladen na uživatelské rozhraní pro vyhledávání v částech videa, uspořádaných podle relevance - např. na dotaz "kdy v rámci těchto 2 hodin přehledového videa na náměstí projela 6letá holčička na koloběžce" lze rychle vyhledat 100 možných případů na 4 obrazovkách je "očima" rychle projít.

# Poznámky
- existuje [yolov11](https://github.com/ultralytics/ultralytics)

# Užitočné odkazy
- [KNOT](https://knot.fit.vutbr.cz/wiki/index.php/Aisee4)
# The Thing (1982) — forenzná analýza: záverečná správa

> Stav: **hotové, revidované** (2026-11-22). Nezávislá analýza → externé zdroje → adversariálna kontrola →
> verdikt → druhé kolo: námietky dvoch ďalších modelov, overené na obraze a v scenári z roku 1981 (hypotheses.md §7).

## 1. Materiál

| Položka | Hodnota | Ako overené |
| --- | --- | --- |
| Zdroj | Kinová verzia z Blu-ray, kontajner MKV | metadáta kontajnera |
| Video | H.264 High, 1920×816 (2,35:1, SAR 1:1), 23,976 fps konštantne (24000/1001) | ffprobe |
| Dĺžka | 01:48:34.091, 156 182 snímok; dej končí 01:42:07.163, potom titulky | ffprobe + celé dekódovanie (počet snímok sedí) |
| Zvuk | AAC LC 5.0, 48 kHz, angličtina (bez LFE kanála) | ffprobe |
| Titulky | angličtina pre nepočujúcich (`.en.hi.srt`, 814 titulkov, synchrónne), čeština (`.cs.srt`) | kontrola proti obrazu a nezávislému prepisu |
| Verzia | Kinová verzia (109 min pri 23,976 fps, bez PAL zrýchlenia; neobsahuje rozprávača ani alternatívne zábery TV verzie) | dĺžka + obsah |
| Nezávislý prepis | faster-whisper large-v3-turbo zo stredového (dialógového) kanála, 523 segmentov | `work/whisper_fc.json` |

Časové značky v správe sú prezentačné časy dekódovaných snímok, `HH:MM:SS.mmm`.
Číslo snímky: `f = round(t × 24000/1001)`, snímka 0 je v t = 0.

## 2. Metóda

- 1 103 automaticky detegovaných záberov (`work/shots.csv`), kontaktné hárky „1 snímka na záber“.
- Päť nezávislých chronologických priechodov úsekmi filmu, záverečná scéna samostatne.
- Celofilmový priechod tvárí na analytickom VM: detekcia tvárí (YuNet), identity (SFace embeddingy)
  a meranie odleskov v očiach (catchlight) pre každú snímku.
- Zvuk: prepis dialógov, nezávislý od titulkov, a hľadanie hudobných motívov.
- Externé zdroje sa čítajú až po nezávislej analýze (`sources.md`).

## 3. Päť najsilnejších indícií

Poradie podľa toho, ako veľmi indícia **rozlišuje** medzi hypotézami. Žiadna z nich nerozhoduje sama.

1. **Reťaz MacReadyho šatstva v strede filmu** (R2-001–003, S4-023, S4-051–053, S4-068;
   hypotheses.md L). Nauls nájde v kuchynskom koši roztrhané zafúľané spodky (00:41:04), MacReady ich
   má sám v izbe pri ústach a nose (00:43:43–47), na páske ich pripíše Windowsovi a hlási, že menovka
   chýba (01:03:41). Potom sa nájdu dva roztrhané odevy s nápisom „R.J. MacREADY“ (01:06:09 a v peci
   jeho chatrče 01:11:15) a MacReady o peci vie, hoci mu to na obraze nikto nepovie (01:14:41).
   Podľa pravidla, ktoré vysloví sám MacReady („it rips through your clothes when it takes you over“),
   to ukazuje na neho. → Najsilnejšie pre H3. Dej však ponúka aj falšovanie (svetlo v chatrči, veci
   v sklade) a scenár z roku 1981 používa spodky ako dôkaz, ktorý MacReady vyšetruje.
2. **Testy oboch preživších sú jediné neoveriteľné** (R2-004, R2-005, S5-014). Z ôsmich testov na
   obraze nevidno len pôvod MacReadyho vzorky a obsah Childsovej misky. MacReadyho test si robí sám
   a odber, ktorý scenár výslovne má („He cuts himself with the scalpel…“), film nahradí detailom
   Childsa. → MacReadyho test nie je dôkaz jeho ľudskosti; celý vzorec podporuje H5 ako zámer.
3. **Príležitosť: Childsovo okno a voľná imitácia** (S5-023, S5-027, S6-001, R2-006, R2-008).
   Childs je sám od 01:27:08 na stráži a mimo obrazu až do 01:39:53 (≈12 min 45 s filmu, v príbehu
   hodiny), kým sa Blair-Vec pohybuje tunelom aj stanicou. Naulsov pohľad na postavu pri vchode
   (01:29:50) neoverí, či bol Childs ešte človek. Pri Benningsovi film rovnakú situáciu (sám → vonku
   ako on) ukáže celú, pri Childsovi útok vynechá. → Umožňuje H2, nedokazuje ju.
4. **Childsovo alibi je hodnoverné, ale nepotvrdené** (S6-010, S5-027, R2-007). Z okna šatne pri
   stráži vidno prístup k budove (01:10:41, 01:26:48), takže „Thought I saw Blair“ sedí s tým, čo film
   ukazuje. Blaira však videl len Childs; Nauls potvrdzuje iba postavu vonku. → Nerozlišuje.
5. **MacReadyho konanie** (hypotheses.md R). Vymyslí test, odhalí Palmer-Vec, spáli Norris-Vec,
   Palmer-Vec aj Blair-Vec, zničí jej loď a celú stanicu. → Najsilnejší argument proti H3. Film však
   nikde neukáže, že by Veci spolupracovali, takže je to vzorec správania, nie logický rozpor.

**Zdanlivé indície, ktoré nerozlišujú** (hypotheses.md §5):
- **Para z úst:** imitácia dýcha viditeľne (Bennings-Vec, S3-020); v závere ju určuje protisvetlo.
- **Svetlo v očiach:** lokálny Cundeyho prostriedok len pre Palmera v krvnom teste (bez odlesku
  01:21:08 a 01:22:43, s odleskom 01:19:19); v závere sú odlesky slabé u oboch (FP-001, FP-002).
- **Fľaša:** whisky so svetlou etiketou, bez knôtu, nie Molotovov koktail (S6-007, S6-008). Ako
  prenos „malou čiastočkou“ dáva zmysel len pri H3 (O).
- **Náušnica:** spojitá od 00:11:57 po 01:40:32.777 (S1-030, S6-003).
- **Svetlá parka:** tá istá tmavomodrá parka pod námrazou (S6-004, S6-013, §3 hypotheses.md).
- **Úsmev:** až po napití.
- **Hudba:** basový „tlkot“, ktorý sprevádza psa-Vec (AU-001), v závere chýba (AU-003).

## 4. Tri najlepšie alternatívne vysvetlenia

(k tomu, že film pôsobí, akoby odpoveď obsahoval)

1. **Zámerná nejednoznačnosť.** Carpenter (Guardian 2024: „left up in the air… that's the way I wanted
   to end it“), Cundey (2016: „John very deliberately wanted to leave the question…“) a komentár z roku 1998
   („We just didn't know“). Do tohto výkladu zapadá aj to, že film necháva neoveriteľné práve testy
   oboch preživších.
2. **Náhoda strihu a natáčania.** Záver bol podľa Cohena mnohokrát prestrihávaný a herci hrali tri
   varianty (Keith David). Aj časť reťaze šatstva môže byť vedľajší produkt: na páske „Windows found“,
   hoci scenár aj obraz majú Naulsa, a vynechaný odber MacReadyho krvi mohol vypadnúť pre tempo, keď
   sa scéna testu prestavala (v scenári žije Copper a drží stráž).
3. **Indícia existuje a je v strede filmu.** Carpenter od 2025 hovorí o „giant hint in the middle of
   the film“. Najlepší kandidát z tejto analýzy je reťaz MacReadyho šatstva (00:41–01:14) spolu
   s Fuchsovým pravidlom (01:04:50). Carpenter ju nikdy nepomenoval a v roku 2022 teórie „napil sa,
   takže je nakazený“ zosmiešnil.

## 5. Najsilnejší argument proti vlastnému záveru

**Proti H5 hovorí Carpenter sám.** Od roku 2022 opakuje, že odpoveď pozná, a od roku 2023, že sa dá
pozorným sledovaním vyčítať z filmu („Yes, you can.“; „There is a big clue. No one has guessed it.“).
Prvé kolo tejto analýzy indíciu v strede filmu prehliadlo, a to práve preto, že hodnotilo riadky po
jednom. Ak Carpenter myslí reťaz šatstva vážne, film rozhodnutie obsahuje a H5 je príliš opatrná.

**Proti sklonu k H3 hovorí scenár a dej.** V scenári z roku 1981 MacReady spodky vyšetruje („examines
the label. Size large.“), odev v peci slúži ako Vec, ktorá ho očierňuje, a dej to vo filme zopakuje
(svetlo v chatrči, „anybody could've gotten some of my clothes“). MacReady celý film Veci ničí. Ak je
reťaz len zápletkou o falšovaní, ukazuje na MacReadyho len preto, že ho tak chcela ukázať Vec.

## 6. Vylúčené a otvorené hypotézy

- **Nedá sa vylúčiť žiadna** s istotou: testy oboch preživších sú neoveriteľné a po teste nemá film
  okamih, ktorý by niekoho dokázateľne overil.
- **H3 (MacReady Vec): nízka až stredná dôvera**, pôvodne nízka. Stratila protidôkaz (vlastný test)
  a získala reťaz šatstva.
- **H1 a H2: nízka až stredná dôvera, približne vyrovnané.** H1 oslabila, lebo MacReadyho test už
  nepodporuje jeho ľudskosť a Childsovo alibi nie je potvrdené.
- **H4 (obaja Vec): nízka.** Bola by pokračovaním H3, ak by fľaša v závere bola prenos.

## 7. Verdikt

- **H5: film neposkytuje dosť informácií na jednoznačné rozhodnutie** — dôvera **vysoká** pre tvrdenie
  „film nedokazuje“. Posilňuje ju zistenie, že film necháva neoveriteľné práve testy oboch preživších.
- **MacReady: otvorené** (pôvodne „človek, stredná dôvera“). Ak film niekoho naznačuje, najviac
  konkrétnych záberov ukazuje na MacReadyho. **Reťaz MacReadyho šatstva je najlepšie podložený kandidát
  na Carpenterovu „indíciu v strede filmu“**, dôvera nízka až stredná.
- **Childs:** **H1 a H2 sú otvorené a približne vyrovnané.** Proti nemu stojí len príležitosť
  (≈13 min bez dozoru od 01:27:08 s voľnou Blair-Vecou); jeho alibi je hodnoverné, no nepotvrdené.
- **Pracovná hypotéza zo zadania** („Carpenter naznačil, že vo filme je indícia“): **ako tvrdenie overená**
  (Carpenter 2023, 2025, 2026, overené v origináli). **Ako fakt nepotvrdená, ale s kandidátom:** reťaz
  šatstva je v strede filmu a ukazuje na jedného muža, no Carpenter indíciu nikdy nepomenoval.
- **Ako sa verdikt vyvíjal:** nezávislá verzia sa mierne prikláňala k H2 pre svetlú parku. Externé zdroje
  a nové testy ukázali námrazu a verdikt sa posunul k H5 s MacReadym ako pravdepodobným človekom.
  Druhé kolo (dva ďalšie modely) odhalilo kruhový „pevný bod“ MacReadyho testu, chybné okno pre H2
  a nespojenú reťaz šatstva; MacReady sa presunul medzi otvorené (hypotheses.md §7).

## 8. Nápady na vizualizácie celého filmu

> Požiadavka operátora (2026-11-21). Pri každom nápade je uvedené, či dáta **už sú** zozbierané
> (✅), alebo by sa museli doplniť (➕).

| # | vizualizácia | čo ukáže | dáta |
| --- | --- | --- | --- |
| 1 | **Stanica zhora s bodkami postáv v čase** (návrh operátora). Schematický pôdorys (hlavná budova, šatňa, psinec, kôlňa s tunelom, MacReadyho chatrč na lane, podzemie s generátorom); bodka = postava, posuvník = čas filmu. Plná bodka: v zábere; bledá: miesto uvádza dialóg; rozmazaná zóna s „?“: neznámo; obrys sa mení od najskoršieho možného a od potvrdeného okamihu asimilácie; osamotená postava pulzuje. | kto mohol byť s kým sám, kde vznikajú okná (Childs 01:27–01:39, hodina tmy, chatrč) | ✅ `work/segments/seg*_presence.csv` (88 scén × 12 postáv, stav, miesto), ✅ `frames/facepass/presence.csv` (presné časy v zábere z face passu), ✅ schéma v `timeline.md` §5; ➕ súradnice uzlov mapy (ručne, ~15 miest) |
| 2 | **Plavecké dráhy (swimlanes)** — pás na postavu: v zábere / známe miesto / neznáme / mŕtvy / odhalená Vec, s vyznačenými oknami bez dozoru a krvným testom | celý príbeh na jednej obrazovke, kde sa skrývajú medzery | ✅ presence CSV + ✅ face pass |
| 3 | **Kostýmový pás** — pre každú postavu farebný pruh vrchného odevu v čase (vzorkovaný z tela pod tvárou) | ako svetlo a námraza menia vnímanú farbu (Childsova tmavomodrá parka v závere „svetlá“), Benningsova vesta → cudzia parka | ✅ detekcie tvárí s polohou (`/data/clust/detections.csv` na VM, treba stiahnuť); ➕ vzorkovanie farby trupu |
| 4 | **Sieť „kto bol s kým“** — graf postáv, hrana = čas spolu v zábere (z face passu) a čas vo dvojici bez svedkov (z presence) | sociálna štruktúra, možné reťaze nákazy | ✅ face pass (spoločný výskyt v snímke), ✅ presence |
| 5 | **Strom možných nákaz** — pre každú imitáciu časovo možné zdroje a okná, konzistentné reťaze | prečo Norris/Palmer zostávajú záhadou, kde vstupuje Childs | ✅ `timeline.md` §2, `rules.md` |
| 6 | **Čas na plátne podľa postáv** — skladaný plošný graf po minútach | kto film nesie a kto mizne | ✅ face pass (137 831 detekcií, 1 967 stôp) |
| 7 | **Test svetla v očiach** — bodka na každý detail tváre: odlesk áno/nie, farba podľa stavu (človek/Vec); zvýraznená scéna krvného testu | že teória neobstojí (Palmer-Vec má odlesky) | ✅ `frames/facepass/catch_tracks.csv` |
| 8 | **Dych v závere** — časová os záverečnej scény po záberoch: para MacReady/Childs a jas pozadia za ústami; kontrola Bennings-Vec | že para závisí od protisvetla | ✅ hárky v `work/scratch/lead/breath/`; ➕ automatické meranie jasu pred ústami |
| 9 | **Farebný barcode filmu** — priemerná farba každej sekundy s vyznačenými odhaleniami | dramaturgia svetla: modrá noc, oranžový oheň, záverečný purpur | ✅ `work/framestats.npz` |
| 10 | **Rytmus strihu** — dĺžka záberov v čase | napätie pred odhaleniami | ✅ `work/shots.csv` (1 103 záberov) |
| 11 | **Zvuková mapa** — hlasitosť dialógu (stredový kanál) a hudby (L/R), hudobný „tlkot“ vs. prítomnosť Veci | pulz pri psovi (00:14:42), ticho v závere | ✅ `frames/facepass/audio_profile_per_second.csv` |
| 12 | **Sieť obvinení a dôvery** — kto koho obviňuje, kto komu velí, v čase | paranoja ako graf | ✅ titulky + Whisper; ➕ označenie hovoriaceho pri každej replike |
| 13 | **Hodiny pochybností** — kumulatívny čas bez dozoru pre každú postavu | prečo Childs po teste vyčnieva | ✅ presence CSV |
| 14 | **Prieskumník dôkazov** — interaktívna časová os 318 indícií z `evidence.csv` s filtrom H1–H5 a spoľahlivosti, náhľad snímky po kliknutí | celé vyšetrovanie na preklik | ✅ `evidence.csv` + `frames/` |

Najväčší účinok s najmenšou prácou: **1 (stanica zhora)**, **3 (kostýmový pás)** a **14 (prieskumník
dôkazov)** — dáta sú takmer celé hotové.

## 9. Porovnanie s externými zdrojmi

Podrobná tabuľka je v `sources.md`. Zhrnutie:

- **Zhoda s overenými vyjadreniami štábu:** svetlo v očiach len pre Palmera v krvnom teste (Cundey) —
  potvrdené meraním aj vizuálne; dych závisí od ohňa a svetla (Keith David, Cohen, Ager) — potvrdené
  kontrolou Bennings-Vec; fľaša nie je Molotov (Keith David, Ager) — potvrdené etiketou.
- **Oprava vlastného záveru:** svetlá parka je pravdepodobne námraza (Ager 2017, Cohen) — potvrdené
  novými testami obrazu; pôvodný farebný argument bol chybný.
- **Nové a overiteľné:** chýbajúca tmavomodrá parka na vešiaku (Ager 2017) — v obraze potvrdené,
  význam nepreukázaný.
- **Rozpory medzi zdrojmi:** Carpenter 1998 („we just didn't know“) vs. 2022–2026 („I know… big clue“);
  Ramsay vs. Cohen o vystrihnutom zábere zachráneného MacReadyho; Cohen vs. Carpenter o Lancasterovom
  pôvodnom konci.
- **Scenár (2. verzia, 4. 3. 1981, imsdb) oproti filmu:** MacReady si v scenári krv odoberie na obraze,
  vo filme nie (R2-004); v scenári spodky našiel Nauls a MacReady to na páske aj povie, vo filme hovorí
  „Windows“ (R2-003); súkromná scéna so spodkami v MacReadyho izbe (00:43) v scenári nie je (R2-002);
  Fuchsovo pravidlo je v scenári odvodené z psov, ktorí „swallowed parts“ (rules 1.7).
- **Nedohľadané:** fáma, že Carpenter povedal „Keith David nedýcha“ (tretia ruka); Carpenterovo „all the
  rumors are untrue“ (len cez Cohena); akékoľvek vyjadrenie Bottina alebo Morriconeho k identite.

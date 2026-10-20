# Rasmdan aniq o'lcham olish usuli

Maqsad: rasmga qarab "taxminan" emas, **tekshiriladigan** o'lcham olish. Uch manba, ustunlik tartibida:

1. **Foydalanuvchi bergan aniq o'lcham** — hech qachon o'zgartirilmaydi, model shu bilan quriladi.
2. **Standart o'lcham** (`data/standard_sizes.json`) — ob'ekt turi aniqlangach, rasmdan olingan taxminiy qiymat eng yaqin standart qatorga **yaxlitlanadi** (DN, G rezba, panel radiator H/L, bak hajmi...). Yaxlitlashni foydalanuvchiga aytib o'ting.
3. **Rasmdan o'lchash** — faqat etalon (ma'lum o'lcham) bo'lsa ishonchli. Etalon yo'q bo'lsa — nisbatlar olinadi, mutlaq o'lcham foydalanuvchidan so'raladi yoki standartdan taxmin qilinib **belgilanadi**.

## Bosqichlar

### 1. Rasmni o'qish va ob'ektni aniqlash
- Rasmni `Read` bilan ko'ring. Yozing: ob'ekt turi, asosiy primitivlar (quti, silindr, quvur, flanets, panel...), simmetriya, ko'rinish turi (foto/perspektiva, orto chizma, eskiz, 3D render), ko'rinishlar soni (old/yon/ust).
- Chizmada **o'lcham chiziqlari va raqamlar** bo'lsa — ularni o'qing, bu 1-darajali manba. Raqamlar kichik bo'lsa `measure_image.py crop ... --zoom 3` bilan kattalashtiring.

### 2. Etalonni tanlash
- Rasmdagi ma'lum o'lchamli narsa: A4 qog'oz, bank kartasi, g'isht, plitka, rozetka, eshik, radiator ulanishi G1/2 (20.955 mm), DN quvur... — ro'yxat `standard_sizes.py show reference_objects`.
- Etalon o'lchanadigan narsa bilan **bir tekislikda** va kameraga **bir masofada** bo'lishi kerak. Aks holda xato 10 %+.

### 3. Piksellarni aniq o'qish
```
measure_image.py info  rasm.jpg                         # o'lchami
measure_image.py grid  rasm.jpg g.png --step 50         # setka bilan ko'rib, nuqtalarni taxminan toping
measure_image.py crop  rasm.jpg c.png x0 y0 x1 y1 --zoom 3   # chekkani 3x kattalashtirib aniq piksel
measure_image.py edges rasm.jpg e.png                   # kontur — chekkalar qayerda
measure_image.py profile rasm.jpg x0 y0 x1 y1           # chiziq bo'ylab yorqinlik sakrashi = chekka pikseli
measure_image.py mark  rasm.jpg m.png 550,100,A 750,200,B   # tanlagan nuqtalarni belgilab qayta ko'rish
```
Har nuqtani `mark` bilan tekshirib, keyin hisoblang. Chekka pikseli `profile` dagi eng katta sakrash.

### 4. Piksel -> mm
- Tekis (perpendikulyar) ko'rinish: `scale_from_image.py linear --ref x0,y0 x1,y1 --ref-mm 297 --measure ...`
- Perspektiva bor: etalon to'rtburchakning 4 burchagi bilan gomografiya:
  `scale_from_image.py homography --quad TL TR BR BL --quad-mm 210 297 --measure ... --points ...`
  `self_check_mm` etalon burchaklarini (0,0),(W,0),(W,H),(0,H) ga qaytarishi shart.
- Ko'p o'lcham bo'lsa `spec.json` yozib `scale_from_image.py json spec.json` — natija JSON ni to'g'ridan-to'g'ri `model_template.py --json` ga bering.

### 5. Standartga yaxlitlash va chuqurlik
- Olingan qiymatni `standard_sizes.py nearest <jadval> <ustun> <qiymat> [up|down]` bilan yaxlitlang; farq 3 % dan katta bo'lsa foydalanuvchiga ayting.
- Bitta rasmdan **chuqurlik** (kameraga qarab yo'nalish) olinmaydi: ikkinchi ko'rinish, standart (masalan panel radiator tip 22 -> 100 mm) yoki foydalanuvchi.

### 6. Aniqlik va belgilash
| Manba | Kutilgan aniqlik |
|---|---|
| Chizmadagi raqam | ±0 (aniq) |
| Standart jadval (approx: false) | ±0 |
| Standart jadval (approx: true) | ±5 % (ishlab chiqaruvchi) |
| Foto + etalon bir tekislikda, gomografiya | ±1-2 % |
| Foto + etalon, chiziqli masshtab, perspektiva bor | ±3-8 % |
| Etalonsiz, faqat nisbat | mutlaq o'lcham noma'lum — so'rang |

Yakuniy hisobotda har o'lcham uchun manbasini yozing: `L=1000 (foydalanuvchi)`, `D=100 (standart: tip 22)`, `H=497->500 (rasm, standartga yaxlitlandi)`.

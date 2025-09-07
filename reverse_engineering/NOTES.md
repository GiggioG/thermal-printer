MAGIC VALUE: 0x51 78
```js
function getHex(){return Array.from(new Uint8Array(arguments)).map(e=>e.toString(16).padStart(2, '0').toUpperCase()).join(' ');}
```

0. Inspo (cat printer) i motivaciq
1. Sniff s ESP32 i nrF connect
2. TestGen.py, Gledane samo na dannite
    - 0x5178 100% e magic value kato header
    - packetitie zavurshvat na 0xFF
    - `ggVGgJ:%s/5178/^V^M5178/g^MggddG:s/0*$/^M:%s/\(\w\w\)\(\w\w\)/\1 \2/g^M:%&g^M` for data parsing
    - 2ta scripta za visualizirane, ne bqh zabelqzal, che e B/W dithered, a ne grayscale, ochakvah da pop outne kartinkata
    - dataToBin.py, da go gledam s hex editor => do nikude
3. zabivane v PrintPreviewActivity.java
    - printBtn
    - printData
    - nedecompiliraniq handler, emptyMessage-5 => emptyMessage-4
4. Zabivane v activityType (LABEL, OFFICE, ...)
    - predpolagam label, produljavam
5. PrintModelUtils i PrinterModel => x6.java, izvadq argumentite
    - legendarno vim macro:
        `0f(l"ddt,xxj0f(ldw"edt,xxjvi{:s/<C-R>e;/<C-R>d;<CR>?{k0`
6. naj-nakraq v pravilnata posoka: `BitmapToData()` v `PrintDataUtils.java`
7. status byte-ovete rediscovernati: 0x`51 78 A3 00 01 00 00 00 FF` obratno v PrintData (PrintPreviewActivity)
8. v BitmapToData se vika eachLinePixTo...B, no to ne e decomp, zatova gledam eachLine...Gray, sigurno e sushtoto
    - zashto tf raw byte-ovete na dithera se zavirat direktno v packeta, bez packet (0x`51 78 ... FF`).
9. bluskam si glavata, no vednaga vijdam, che v `eachLineP...B` ne e sushtoto, oshte v purvite redove se getva
    width / 8, ochevidno e razlichno.
10. buildvame packeta:
    - enerAgy packet 0x`51 78 AF 00 02 00 <nrg_low> <nrg_high> <crc> FF`
    - printType packet 0x`51 78 BE 00 01 00 <type> <crc> FF`
        Type: `00` - image, `01` - text, `02` - tattoo, `03` - label
    - feedPaper packet 0x`51 78 BD 00 01 00 <textSpeed> <crc> FF` 
11. obratno v BitmapToData:
    - blackeningPacket 0x`51 78 A4 00 01 00 33 99 FF` (quality 3 (51) (0x33) - vinagi za moq printer e tova quality)
        te sa ot 1 do 5 (ot 49 do 53)
    - feedPaper 0x`51 78 BD 00 01 00 0F <crc> FF` - feedPaper(15)
12. obratno v `eachLinePixToCmdB`: polzvam nqkolko regexa, ne pomagat osobeno mn
    - zagrqvam, che DataTrim() vzima (runLenght, byte, arrayList), i byte-a legit e 0x00 ili 0x01
        vseki byte, kojto pravi e `<1b: stojnost na byte-a, 0 ili 1><7b: duljina na run-length(do 127)>`
    - run-length encoding, ako e po-zle ot bitpacking, togava bit-packvame
    - L_0x02fb dataTrim-vame 0, ako izobshto nishto ne sme imali
    - v L_0x0328: stranni kriterii dali sme kompresirali:
        ne sme kompresirali, ako: 1. purviq byte e 0xFF, 2. byte-ovete ne sa width/8 + 1
    - 0x`51 78` + -94(0x`A2`) ako ne sme kompresirali, -65(0x`BF`), ako sme kompresirali
    - 0x`51 78 <A2 | BF> 0 <datalen_low> <datalen_high | 00> <dannite, run-lenghtnati ili bitpack-nati> <crc> FF`
        - da se izfukam, che kompresiqta q nqma v originalniq writeup
12. naj-nakraq q svurshih, obratno v BitmapToData
    - paper packet, ot BluetoothOrder 0x`51 78 A1 00 02 00 30 00 F9 FF`, sled vseki PrintBean, kojto ima .isAddWhite()
    - maj nqma takiva
13. finalna naredba na komandite
14. decode.py, bachka s probite (primeri)
15. kakvo e energy-to?
    - gledam v koda: (concentration-a - Code.DEFCONCENTRATION(4))\*0.15\*d + d, trqbva da e 0x7B2A(=10875), zashtoto tova poluchavam
    - osuznavam, che concentration sigurno e print depth, zashtoto defaulta e 4 ot 1 do 7 (DEF _\[ault\]_ CONCENTRATION = 4)
    - az polzvam 7, znachi (7-4)*0.15.d+d = 10875 => d = 7500, no moderateConcentration-a na X6 e 8000.....
    - moqt printer e x6_n or PrinterModelUtils.java, vse pak ne obqsnqva zashto isCanPrintLabel qvno e false
    - hipoteza: energy = (printDepth - 4)\*0.15\*7500 + 7500, shte testvam
    - hipoteza 2: textEnergy=> energy da e =0 pri textov rejim
16. kakuv e print type-a
    - probvam da send-na snimka kato text, image; text kato text,image; opitam se da dokaram label
17. textSpeed-a e model.textSpeed(10) za text(0x`01`), model.imgSpeed(30) za image(0x`00`) i label(0x`03`)
    - probvajki prednoto, sledq feedPaper-a
18. Da probvam:
    1. da dokaram print type: label
    2. da dokaram print type: text
        - vidq dali energy == 0
    3. probvam pone 2 drugi energy-ta, da vidq dali scale-va pravilno
    4. probvam da sendna snimka kato text, obratnoto, sledq feedPaper-a
19. Findings:
    - kogato printiram document, type: img, printType-a se meni, no nikoga nqma energy i textSpeed = 10
    - energyto naistina e po onazi formula
    - tova s documenta e izkluchenie, sus image i text:
        1. pri image ima energy po formulata, BD=00, textSpeed=30
        2. pri text nqma energy, BD=01, textSpeed=10
    - label-a se durji tochno kato chist image, samo BD=03; nezavisimo dali type-a e setnat na Text ili Image
    - kato mu dam poveche kopiq apparently ne sa otdelni bean-ove, poneje ima blackening pred vsqko i dopulnitelen
    feedPaper(25) sled vsqko => probvam s multiple beans
20. Recreate in script
    - crc-to, deleted59 => gledam lipsvashtoto sus xor na vsichki ostanali, razbiram che e `0x3d`
    - printImage.py -> uspeshno generira commandi
21. Make script actually send BLE packets
    - reading what printer sends back, the 4th byte is 0x00 if phone->printer and 0x01 if printer->phone
21. status (0x`A3`) response (length 3)
    1. status, ends with:
        - =0: ok,
        - 0b1: out of paper, 
        - 0b10: compartment open,
        - 0b100: overheated,
        - 0b1000: low battery,
        - 0b10000: currently charging,
        - 0b10000000: currently printing
    2. labelNum, kakvoto i da e tova
    3. battery level, po nqkakva skala?
22. Bachka
23. Kakvo ostana?
    - kakvo pravi 0xBD FeedPaper?
24. Look back
    - ako imah akul i bqh zabelqzal, che e cherno-bql, mojeshe samo ot protocol capturi-te
no nqmashe da imam compressiq, da znam za type-ove, za energy i t.n.



# Vim commands for easier decompiling
1. `:v/L_0x....:/norm A;^[`
2. `:%s/\(\d\+\)(0x.*)/\1/g`

3. `:%s/\(.* \)\?r\(\d\+\) = \(.*\);$\n\t\(.* \)r\2 = \(.*\);$/\=("\t".submatch(4)."r".submatch(2)." = ".substitute(submatch(5),"r".submatch(2),submatch(3),"")."; \/\/ rule 1")/g`
4. `:%s/\(.* \)\?r\(\d\+\) = \(.*\);$\n\tr\2 = \(.*\);$/\=("\t".submatch(1)."r".submatch(2)." = ".substitute(submatch(4),"r".submatch(2),submatch(3),"")."; \/\/ rule 2")/g`
5. `:%s/int r\(\d\+\) = r\1 \([+-\*\/]\) \(.\+\);/r\1 \2= \3; \/\/ rule 3/g`
6. `:v/r\(\d\+\) = \(\-\?\d\+\);\n.*r\1 \?=.*/ s/r\(\d\+\) = \(\-\?\d\+\);$\n\t\(.*[ (]\)r\1\(.*\)/r\1 = \2;^M\t\3\2\4 \/\/ rule 4/g`
7. `:%s/boolean r\(\d\+\) = \(.*\);\n\tif (r\1\(.*\)$/if ((r\1 = \2\)\3 \/\/ rule XXX/g`
8. `:%s/if (\(.*\)) goto \(L_0x....\);\n\tif (\(.*\)) goto \2;/if ((\1) || (\3)) goto \2; \/\/ rule 6/g`

- broken but still cool: `:%s/if \(.*\) goto \(L_0x....\);$\n\(^\t.*$\n\)\+\tgoto \(L_0x....\);\n\2:$\n\(^\t.*$\n\)\+\4:/if \1 { \/\/ rule 5^M\5\t} else {^M\3\t}/g`

# command order

1. blackening /// ne za vseki bean
2. vsichkite komandi ot EachLinePixToCmdB
    1. enerAgy
    2. printType
    3. feedPaper(textSpeed)
    4. draw
3. paper (ako bean-a ima addWhite)
4. feedPaper(25)
5. paper x2
    bi trqbvalo da gi nqma, poneje X6 e isCanPrintLabel.
6. feedPaper(25) /// ne za vseki bean
7. ne poluchavam devInfo (0x`51 78 A8 00 01 00 00 00 FF`), nz zashto
    i tuk i pri dvata `paper`-a se durji, sqkash X6 ne e isCanPrintLabel

# todo
- [ ] napisha property-ta na X6_n (ot file)
- [ ] writeup
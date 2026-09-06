"""Physical board illustration based on the Super Mini photo and E07 mechanical drawing."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
parts=['''<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="1600" viewBox="0 0 1400 1600">
<title>BZP Airbridge physical wiring</title>
<defs>
<radialGradient id="bg" cx="50%" cy="0%" r="100%"><stop stop-color="#28343b"/><stop offset=".4" stop-color="#0b1013"/><stop offset="1" stop-color="#000"/></radialGradient>
<linearGradient id="panel" x2="1" y2="1"><stop stop-color="#20272b"/><stop offset=".58" stop-color="#070a0c"/><stop offset="1" stop-color="#141a1e"/></linearGradient>
<linearGradient id="metal" x2="1" y2="1"><stop stop-color="#fff"/><stop offset=".35" stop-color="#7c858b"/><stop offset=".65" stop-color="#eef1f2"/><stop offset="1" stop-color="#6e777d"/></linearGradient>
<pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="#173640" opacity=".35"/></pattern>
</defs><rect width="1400" height="1600" fill="url(#bg)"/><rect width="1400" height="1600" fill="url(#grid)"/>
<g font-family="Arial,Helvetica,sans-serif">
<text x="700" y="65" text-anchor="middle" fill="#9beaff" font-size="34" font-weight="700" letter-spacing="3">BZP AIRBRIDGE · PHYSICAL WIRING</text>
<text x="700" y="108" text-anchor="middle" fill="#a9b7bd" font-size="19">COMPONENT SIDE FACING YOU · USB-C UP · SMA DOWN</text>
<text x="700" y="146" text-anchor="middle" fill="#28cfff" font-size="17">3.3 V POWER · TWO SEPARATE BOARDS · EIGHT CONNECTIONS</text>
<!-- Radio board: 15 by 28 mm outline, four columns of two header pads -->
<rect x="130" y="440" width="270" height="504" rx="7" fill="#103e59" stroke="url(#metal)" stroke-width="3"/>
<text x="265" y="620" text-anchor="middle" fill="#c9e7f4" font-size="19" font-weight="700">433M V2.0</text>
<rect x="217" y="640" width="96" height="96" rx="4" fill="#080c10" stroke="#697b83" stroke-width="2"/>
<text x="265" y="696" text-anchor="middle" fill="#9aa8b0" font-size="15">CC1101</text>
<path d="M192 632h-18v88h27M328 650h31v105h-33M236 751v58h28v82" fill="none" stroke="#3e7890" stroke-width="4"/>
<g fill="#c4c8c7"><rect x="185" y="750" width="25" height="13"/><rect x="320" y="610" width="13" height="28"/><rect x="300" y="778" width="25" height="13"/></g>
<circle cx="198" cy="764" r="27" fill="#aeb8b9"/><circle cx="198" cy="764" r="17" fill="#040709"/>
<circle cx="333" cy="764" r="27" fill="#aeb8b9"/><circle cx="333" cy="764" r="17" fill="#040709"/>
<rect x="215" y="851" width="76" height="42" rx="5" fill="#aab2b4"/><text x="253" y="878" text-anchor="middle" fill="#233039" font-size="14">26 MHz</text>
<rect x="227" y="918" width="76" height="53" fill="#bf9944" stroke="#eed99b" stroke-width="2"/>
<rect x="238" y="966" width="54" height="135" rx="8" fill="#b79753" stroke="#efd99c" stroke-width="2"/>
<path d="M238 979h54m-54 12h54m-54 12h54m-54 12h54m-54 12h54m-54 12h54m-54 12h54m-54 12h54" stroke="#79602d" stroke-width="3"/>
<text x="265" y="1140" text-anchor="middle" fill="#9beaff" font-size="18">SMA → included antenna</text>
<!-- ESP32-C3, 18 by 22.5 mm outline, USB upward -->
<rect x="890" y="460" width="324" height="405" rx="10" fill="#12191d" stroke="url(#metal)" stroke-width="3"/>
<rect x="973" y="432" width="155" height="94" rx="13" fill="url(#metal)" stroke="#e7ecef" stroke-width="2"/><rect x="990" y="439" width="121" height="18" rx="8" fill="#10171b"/>
<text x="1052" y="408" text-anchor="middle" fill="#9beaff" font-size="20">USB-C</text>
<rect x="973" y="545" width="59" height="55" rx="4" fill="#b9c2c6"/><circle cx="1003" cy="572" r="17" fill="#333b40"/>
<rect x="1069" y="545" width="59" height="55" rx="4" fill="#b9c2c6"/><circle cx="1098" cy="572" r="17" fill="#333b40"/>
<text x="1003" y="617" text-anchor="middle" fill="#a1b1b9" font-size="12">BOOT</text><text x="1098" y="617" text-anchor="middle" fill="#a1b1b9" font-size="12">RESET</text>
<rect x="1008" y="652" width="89" height="89" rx="4" transform="rotate(45 1052 697)" fill="#090e12" stroke="#53646d" stroke-width="2"/>
<text x="1052" y="693" text-anchor="middle" fill="#91a8b4" font-size="13">ESP32</text><text x="1052" y="712" text-anchor="middle" fill="#91a8b4" font-size="13">C3</text>
<rect x="976" y="753" width="57" height="29" rx="4" fill="#b9c2c6"/>
<rect x="1000" y="815" width="106" height="35" rx="4" fill="#a94b42" stroke="#d6bfb9" stroke-width="2"/><text x="1053" y="839" text-anchor="middle" fill="#f1e7e1" font-size="17">ANTENNA</text>
<text x="1052" y="911" text-anchor="middle" fill="#f1f5f7" font-size="25" font-weight="700">ESP32-C3 SUPER MINI</text>
<text x="1052" y="944" text-anchor="middle" fill="#8ca1ad" font-size="17">SATUY · B0GGB1L8N5</text>
<text x="604" y="860" text-anchor="middle" fill="#f1f5f7" font-size="24" font-weight="700">CC1101 RADIO</text>
<text x="604" y="890" text-anchor="middle" fill="#8ca1ad" font-size="17">AOICRIE · B0D2TM5RY2</text>
''']
# USB-up pin rows from the actual board photograph.
left=['5','6','7','8','9','10','20','21']
right=['5V','GND','3V3','4','3','2','1','0']
esp={}
for x,names in [(900,left),(1204,right)]:
 for i,name in enumerate(names):
  y=500+44*i; esp[name]=(x,y)
  parts.append(f'<circle cx="{x}" cy="{y}" r="12" fill="#080e12" stroke="#a3afb4" stroke-width="4"/><text x="{x+22 if x==900 else x-22}" y="{y+6}" text-anchor="{"start" if x==900 else "end"}" fill="#b6c4cb" font-size="17">{name}</text>')
# Component-side CC1101: square pad 1 upper right, SMA at bottom.
pins={7:(196,474),5:(242,474),3:(288,474),1:(334,474),8:(196,520),6:(242,520),4:(288,520),2:(334,520)}
signals={1:('GND','GND','#dce4e7'),2:('VCC','3V3','#ff5e69'),3:('GDO0','1','#ff7b32'),4:('CSN','7','#45ed72'),5:('SCK','4','#ffd34b'),6:('MOSI','6','#b28aff'),7:('MISO','5','#28cfff'),8:('GDO2','3','#f293c3')}
# Top-row leads route above the boards; bottom-row leads route through separate lower lanes.
routes={
7:'M196 474V240H790V500H900',
5:'M242 474V275H1270V632H1204',
3:'M288 474V310H1305V764H1204',
1:'M334 474V345H1240V544H1204',
8:'M196 520V558H98V1160H1338V676H1204',
6:'M242 520V573H70V1195H780V544H900',
4:'M288 520V588H42V1230H820V588H900',
2:'M334 520V550H430V1120H1238V588H1204'}
for pin,path in routes.items():
 color=signals[pin][2]
 parts.append(f'<path d="{path}" fill="none" stroke="#020607" stroke-width="13" stroke-linejoin="round"/><path d="{path}" fill="none" stroke="{color}" stroke-width="6" stroke-linejoin="round" stroke-linecap="round"/>')
for pin,(x,y) in pins.items():
 name,target,color=signals[pin];ex,ey=esp[target]
 shape=f'<rect x="{x-12}" y="{y-12}" width="24" height="24" fill="#05090c" stroke="{color}" stroke-width="4"/>' if pin==1 else f'<circle cx="{x}" cy="{y}" r="12" fill="#05090c" stroke="{color}" stroke-width="4"/>'
 parts.append(shape+f'<text x="{x}" y="{y+5}" text-anchor="middle" fill="#fff" font-size="13">{pin}</text><circle cx="{ex}" cy="{ey}" r="12" fill="#05090c" stroke="{color}" stroke-width="5"/>')
parts.append('<rect x="65" y="1280" width="1270" height="230" rx="20" fill="url(#panel)" stroke="url(#metal)" stroke-width="2"/><text x="95" y="1320" fill="#9beaff" font-size="21" font-weight="700">CC1101 HEADER PIN → ESP32 PAD</text>')
for i,(pin,(name,target,color)) in enumerate(signals.items()):
 x=95+(i%4)*310;y=1370+(i//4)*65
 parts.append(f'<circle cx="{x}" cy="{y-6}" r="6" fill="{color}"/><text x="{x+17}" y="{y}" fill="{color}" font-size="19">{pin} {name} → {target if target in ("GND","3V3") else "GPIO"+target}</text>')
parts.append('<text x="700" y="1550" text-anchor="middle" fill="#ffbd22" font-size="18">POWER OFF TO WIRE · VCC TO 3V3 · NO DOT AT CROSSINGS = NO CONNECTION</text><text x="700" y="1580" text-anchor="middle" fill="#83949e" font-size="15">Illustrated component-side layout. Check pin 1 and the PCB labels before connecting a module revision.</text></g></svg>')
(root/'assets/wiring.svg').write_text(''.join(parts))

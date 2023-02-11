<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE eagle SYSTEM "eagle.dtd">
<eagle version="9.7.0">
<drawing>
<settings>
<setting alwaysvectorfont="yes"/>
<setting verticaltext="up"/>
</settings>
<grid distance="0.1" unitdist="inch" unit="inch" style="lines" multiple="1" display="yes" altdistance="0.01" altunitdist="inch" altunit="inch"/>
<layers>
<layer number="1" name="Top" color="4" fill="1" visible="no" active="no"/>
<layer number="2" name="Route2" color="16" fill="1" visible="no" active="no"/>
<layer number="3" name="Route3" color="17" fill="1" visible="no" active="no"/>
<layer number="4" name="Route4" color="18" fill="1" visible="no" active="no"/>
<layer number="5" name="Route5" color="19" fill="1" visible="no" active="no"/>
<layer number="6" name="Route6" color="25" fill="1" visible="no" active="no"/>
<layer number="7" name="Route7" color="26" fill="1" visible="no" active="no"/>
<layer number="8" name="Route8" color="27" fill="1" visible="no" active="no"/>
<layer number="9" name="Route9" color="28" fill="1" visible="no" active="no"/>
<layer number="10" name="Route10" color="29" fill="1" visible="no" active="no"/>
<layer number="11" name="Route11" color="30" fill="1" visible="no" active="no"/>
<layer number="12" name="Route12" color="20" fill="1" visible="no" active="no"/>
<layer number="13" name="Route13" color="21" fill="1" visible="no" active="no"/>
<layer number="14" name="Route14" color="22" fill="1" visible="no" active="no"/>
<layer number="15" name="Route15" color="23" fill="1" visible="no" active="no"/>
<layer number="16" name="Bottom" color="1" fill="1" visible="no" active="no"/>
<layer number="17" name="Pads" color="2" fill="1" visible="no" active="no"/>
<layer number="18" name="Vias" color="2" fill="1" visible="no" active="no"/>
<layer number="19" name="Unrouted" color="6" fill="1" visible="no" active="no"/>
<layer number="20" name="Dimension" color="24" fill="1" visible="no" active="no"/>
<layer number="21" name="tPlace" color="7" fill="1" visible="no" active="no"/>
<layer number="22" name="bPlace" color="7" fill="1" visible="no" active="no"/>
<layer number="23" name="tOrigins" color="15" fill="1" visible="no" active="no"/>
<layer number="24" name="bOrigins" color="15" fill="1" visible="no" active="no"/>
<layer number="25" name="tNames" color="7" fill="1" visible="no" active="no"/>
<layer number="26" name="bNames" color="7" fill="1" visible="no" active="no"/>
<layer number="27" name="tValues" color="7" fill="1" visible="no" active="no"/>
<layer number="28" name="bValues" color="7" fill="1" visible="no" active="no"/>
<layer number="29" name="tStop" color="7" fill="5" visible="no" active="no"/>
<layer number="30" name="bStop" color="7" fill="5" visible="no" active="no"/>
<layer number="31" name="tCream" color="7" fill="4" visible="no" active="no"/>
<layer number="32" name="bCream" color="7" fill="5" visible="no" active="no"/>
<layer number="33" name="tFinish" color="6" fill="3" visible="no" active="no"/>
<layer number="34" name="bFinish" color="6" fill="6" visible="no" active="no"/>
<layer number="35" name="tGlue" color="7" fill="4" visible="no" active="no"/>
<layer number="36" name="bGlue" color="7" fill="5" visible="no" active="no"/>
<layer number="37" name="tTest" color="7" fill="1" visible="no" active="no"/>
<layer number="38" name="bTest" color="7" fill="1" visible="no" active="no"/>
<layer number="39" name="tKeepout" color="4" fill="11" visible="no" active="no"/>
<layer number="40" name="bKeepout" color="1" fill="11" visible="no" active="no"/>
<layer number="41" name="tRestrict" color="4" fill="10" visible="no" active="no"/>
<layer number="42" name="bRestrict" color="1" fill="10" visible="no" active="no"/>
<layer number="43" name="vRestrict" color="2" fill="10" visible="no" active="no"/>
<layer number="44" name="Drills" color="7" fill="1" visible="no" active="no"/>
<layer number="45" name="Holes" color="7" fill="1" visible="no" active="no"/>
<layer number="46" name="Milling" color="3" fill="1" visible="no" active="no"/>
<layer number="47" name="Measures" color="7" fill="1" visible="no" active="no"/>
<layer number="48" name="Document" color="7" fill="1" visible="no" active="no"/>
<layer number="49" name="Reference" color="7" fill="1" visible="no" active="no"/>
<layer number="51" name="tDocu" color="7" fill="1" visible="no" active="no"/>
<layer number="52" name="bDocu" color="7" fill="1" visible="no" active="no"/>
<layer number="88" name="SimResults" color="9" fill="1" visible="yes" active="yes"/>
<layer number="89" name="SimProbes" color="9" fill="1" visible="yes" active="yes"/>
<layer number="90" name="Modules" color="5" fill="1" visible="yes" active="yes"/>
<layer number="91" name="Nets" color="2" fill="1" visible="yes" active="yes"/>
<layer number="92" name="Busses" color="1" fill="1" visible="yes" active="yes"/>
<layer number="93" name="Pins" color="2" fill="1" visible="no" active="yes"/>
<layer number="94" name="Symbols" color="4" fill="1" visible="yes" active="yes"/>
<layer number="95" name="Names" color="7" fill="1" visible="yes" active="yes"/>
<layer number="96" name="Values" color="7" fill="1" visible="yes" active="yes"/>
<layer number="97" name="Info" color="7" fill="1" visible="yes" active="yes"/>
<layer number="98" name="Guide" color="6" fill="1" visible="yes" active="yes"/>
</layers>
<schematic xreflabel="%F%N/%S.%C%R" xrefpart="/%S.%C%R">
<libraries>
<library name="VOSTOK_MISC_LIB" urn="urn:adsk.wipprod:fs.file:vf.2QirG-pvTuembVHon_9QUw">
<packages>
<package name="LS05-13BXXR3" library_version="5">
<pad name="P$1" x="0" y="0" drill="1.4" slotLength="2" shape="slot"/>
<pad name="P$2" x="4" y="0" drill="1.4" slotLength="2" shape="slot"/>
<pad name="P$3" x="8" y="0" drill="1.4" slotLength="2" shape="slot"/>
<pad name="P$4" x="12" y="0" drill="1.4" slotLength="2" shape="slot"/>
<pad name="P$5" x="20" y="0" drill="1.4" slotLength="2" shape="slot"/>
<pad name="P$6" x="24" y="0" drill="1.4" slotLength="2" shape="slot"/>
<wire x1="-2.54" y1="5.08" x2="-2.54" y2="-5.08" width="0.1524" layer="39"/>
<wire x1="-2.54" y1="-5.08" x2="2.54" y2="-5.08" width="0.1524" layer="39"/>
<wire x1="2.54" y1="-5.08" x2="2.54" y2="-12.7" width="0.1524" layer="39"/>
<wire x1="2.54" y1="-12.7" x2="22.86" y2="-12.7" width="0.1524" layer="39"/>
<wire x1="22.86" y1="-12.7" x2="22.86" y2="-2.54" width="0.1524" layer="39"/>
<wire x1="22.86" y1="-2.54" x2="27.94" y2="-2.54" width="0.1524" layer="39"/>
<wire x1="27.94" y1="-2.54" x2="27.94" y2="5.08" width="0.1524" layer="39"/>
<wire x1="27.94" y1="5.08" x2="-2.54" y2="5.08" width="0.1524" layer="39"/>
<text x="0" y="2.54" size="1" layer="25" align="center">&gt;NAME</text>
</package>
<package name="SC0915" library_version="9">
<pad name="P$1" x="-8.89" y="22.86" drill="1"/>
<pad name="P$2" x="-8.89" y="20.32" drill="1"/>
<pad name="P$3" x="-8.89" y="17.78" drill="1"/>
<pad name="P$4" x="-8.89" y="15.24" drill="1"/>
<pad name="P$5" x="-8.89" y="12.7" drill="1"/>
<pad name="P$6" x="-8.89" y="10.16" drill="1"/>
<pad name="P$7" x="-8.89" y="7.62" drill="1"/>
<pad name="P$8" x="-8.89" y="5.08" drill="1"/>
<pad name="P$9" x="-8.89" y="2.54" drill="1"/>
<pad name="P$10" x="-8.89" y="0" drill="1"/>
<pad name="P$11" x="-8.89" y="-2.54" drill="1"/>
<pad name="P$12" x="-8.89" y="-5.08" drill="1"/>
<pad name="P$13" x="-8.89" y="-7.62" drill="1"/>
<pad name="P$14" x="-8.89" y="-10.16" drill="1"/>
<pad name="P$15" x="-8.89" y="-12.7" drill="1"/>
<pad name="P$16" x="-8.89" y="-15.24" drill="1"/>
<pad name="P$17" x="-8.89" y="-17.78" drill="1"/>
<pad name="P$18" x="-8.89" y="-20.32" drill="1"/>
<pad name="P$19" x="-8.89" y="-22.86" drill="1"/>
<pad name="P$20" x="-8.89" y="-25.4" drill="1"/>
<pad name="P$21" x="8.89" y="-25.4" drill="1"/>
<pad name="P$22" x="8.89" y="-22.86" drill="1"/>
<pad name="P$23" x="8.89" y="-20.32" drill="1"/>
<pad name="P$24" x="8.89" y="-17.78" drill="1"/>
<pad name="P$25" x="8.89" y="-15.24" drill="1"/>
<pad name="P$26" x="8.89" y="-12.7" drill="1"/>
<pad name="P$27" x="8.89" y="-10.16" drill="1"/>
<pad name="P$28" x="8.89" y="-7.62" drill="1"/>
<pad name="P$29" x="8.89" y="-5.08" drill="1"/>
<pad name="P$30" x="8.89" y="-2.54" drill="1"/>
<pad name="P$31" x="8.89" y="0" drill="1"/>
<pad name="P$32" x="8.89" y="2.54" drill="1"/>
<pad name="P$33" x="8.89" y="5.08" drill="1"/>
<pad name="P$34" x="8.89" y="7.62" drill="1"/>
<pad name="P$35" x="8.89" y="10.16" drill="1"/>
<pad name="P$36" x="8.89" y="12.7" drill="1"/>
<pad name="P$37" x="8.89" y="15.24" drill="1"/>
<pad name="P$38" x="8.89" y="17.78" drill="1"/>
<pad name="P$39" x="8.89" y="20.32" drill="1"/>
<pad name="P$40" x="8.89" y="22.86" drill="1"/>
<wire x1="-11" y1="-27" x2="11" y2="-27" width="0.1524" layer="39"/>
<wire x1="11" y1="-27" x2="11" y2="25" width="0.1524" layer="39"/>
<wire x1="11" y1="25" x2="-11" y2="25" width="0.1524" layer="39"/>
<wire x1="-11" y1="25" x2="-11" y2="-27" width="0.1524" layer="39"/>
<wire x1="-3" y1="24" x2="3" y2="24" width="0.1524" layer="21"/>
<wire x1="3" y1="24" x2="3" y2="27" width="0.1524" layer="21"/>
<wire x1="3" y1="27" x2="-3" y2="27" width="0.1524" layer="21"/>
<wire x1="-3" y1="27" x2="-3" y2="24" width="0.1524" layer="21"/>
<circle x="-11.5" y="25.5" radius="0.25" width="0.508" layer="21"/>
</package>
<package name="SMW312RJT" library_version="14">
<smd name="P$1" x="-5" y="0" dx="3.2" dy="3" layer="1" roundness="5"/>
<smd name="P$2" x="5" y="0" dx="3.2" dy="3" layer="1" roundness="5"/>
<wire x1="-7" y1="4" x2="7" y2="4" width="0.1524" layer="39"/>
<wire x1="7" y1="4" x2="7" y2="-4" width="0.1524" layer="39"/>
<wire x1="7" y1="-4" x2="-7" y2="-4" width="0.1524" layer="39"/>
<wire x1="-7" y1="-4" x2="-7" y2="4" width="0.1524" layer="39"/>
<text x="0" y="5" size="1.778" layer="25" align="center">&gt;NAME</text>
</package>
<package name="GBJ2510" library_version="20">
<pad name="P$1" x="0" y="0" drill="1.3"/>
<pad name="P$2" x="10" y="0" drill="1.3"/>
<pad name="P$3" x="17.5" y="0" drill="1.3"/>
<pad name="P$4" x="25" y="0" drill="1.3"/>
<wire x1="-3" y1="3" x2="-3" y2="-3" width="0.1524" layer="39"/>
<wire x1="-3" y1="-3" x2="28" y2="-3" width="0.1524" layer="39"/>
<wire x1="28" y1="-3" x2="28" y2="3" width="0.1524" layer="39"/>
<wire x1="28" y1="3" x2="-3" y2="3" width="0.1524" layer="39"/>
<text x="12.5" y="4" size="1.27" layer="25" align="center">&gt;NAME</text>
</package>
<package name="DISP-1743" library_version="26">
<pad name="P$1" x="0" y="0" drill="1.05"/>
<pad name="P$2" x="0" y="-2.54" drill="1.05"/>
<pad name="P$3" x="0" y="-5.08" drill="1.05"/>
<pad name="P$4" x="0" y="-7.62" drill="1.05"/>
<pad name="P$5" x="0" y="-10.16" drill="1.05"/>
<pad name="P$6" x="0" y="-12.7" drill="1.05"/>
<pad name="P$7" x="0" y="-15.24" drill="1.05"/>
<pad name="P$8" x="0" y="-17.78" drill="1.05"/>
<pad name="P$9" x="0" y="-20.32" drill="1.05"/>
<pad name="P$10" x="0" y="-22.86" drill="1.05"/>
<pad name="P$11" x="0" y="-25.4" drill="1.05"/>
<pad name="P$12" x="0" y="-27.94" drill="1.05"/>
<pad name="P$13" x="0" y="-30.48" drill="1.05"/>
<pad name="P$14" x="0" y="-33.02" drill="1.05"/>
<pad name="P$15" x="0" y="-35.56" drill="1.05"/>
<pad name="P$16" x="0" y="-38.1" drill="1.05"/>
<pad name="P$17" x="0" y="-40.64" drill="1.05"/>
<pad name="P$18" x="0" y="-43.18" drill="1.05"/>
<pad name="P$19" x="0" y="-45.72" drill="1.05"/>
<pad name="P$20" x="0" y="-48.26" drill="1.05"/>
<pad name="P$21" x="76.2" y="-48.26" drill="1.05" rot="R180"/>
<pad name="P$22" x="76.2" y="-45.72" drill="1.05" rot="R180"/>
<pad name="P$23" x="76.2" y="-43.18" drill="1.05" rot="R180"/>
<pad name="P$24" x="76.2" y="-40.64" drill="1.05" rot="R180"/>
<pad name="P$25" x="76.2" y="-38.1" drill="1.05" rot="R180"/>
<pad name="P$26" x="76.2" y="-35.56" drill="1.05" rot="R180"/>
<pad name="P$27" x="76.2" y="-33.02" drill="1.05" rot="R180"/>
<pad name="P$28" x="76.2" y="-30.48" drill="1.05" rot="R180"/>
<pad name="P$29" x="76.2" y="-27.94" drill="1.05" rot="R180"/>
<pad name="P$30" x="76.2" y="-25.4" drill="1.05" rot="R180"/>
<pad name="P$31" x="76.2" y="-22.86" drill="1.05" rot="R180"/>
<pad name="P$32" x="76.2" y="-20.32" drill="1.05" rot="R180"/>
<pad name="P$33" x="76.2" y="-17.78" drill="1.05" rot="R180"/>
<pad name="P$34" x="76.2" y="-15.24" drill="1.05" rot="R180"/>
<pad name="P$35" x="76.2" y="-12.7" drill="1.05" rot="R180"/>
<pad name="P$36" x="76.2" y="-10.16" drill="1.05" rot="R180"/>
<pad name="P$37" x="76.2" y="-7.62" drill="1.05" rot="R180"/>
<pad name="P$38" x="76.2" y="-5.08" drill="1.05" rot="R180"/>
<pad name="P$39" x="76.2" y="-2.54" drill="1.05" rot="R180"/>
<pad name="P$40" x="76.2" y="0" drill="1.05" rot="R180"/>
<wire x1="-2.54" y1="2.54" x2="-2.54" y2="-50.8" width="0.1524" layer="39"/>
<wire x1="-2.54" y1="-50.8" x2="2.54" y2="-50.8" width="0.1524" layer="39"/>
<wire x1="2.54" y1="-50.8" x2="2.54" y2="2.54" width="0.1524" layer="39"/>
<wire x1="2.54" y1="2.54" x2="-2.54" y2="2.54" width="0.1524" layer="39"/>
<wire x1="73.66" y1="2.54" x2="73.66" y2="-50.8" width="0.1524" layer="39"/>
<wire x1="73.66" y1="-50.8" x2="78.74" y2="-50.8" width="0.1524" layer="39"/>
<wire x1="78.74" y1="-50.8" x2="78.74" y2="2.54" width="0.1524" layer="39"/>
<wire x1="78.74" y1="2.54" x2="73.66" y2="2.54" width="0.1524" layer="39"/>
<wire x1="-2.54" y1="2.54" x2="78.74" y2="2.54" width="0.1524" layer="40"/>
<wire x1="78.74" y1="2.54" x2="78.74" y2="-50.8" width="0.1524" layer="40"/>
<wire x1="78.74" y1="-50.8" x2="-2.54" y2="-50.8" width="0.1524" layer="40"/>
<wire x1="-2.54" y1="-50.8" x2="-2.54" y2="2.54" width="0.1524" layer="40"/>
<text x="-5.08" y="-48.26" size="1.5" layer="21" align="center">GND</text>
<text x="81.28" y="-48.26" size="1.5" layer="21" align="center">GND</text>
</package>
<package name="TB008A-508-02BE" library_version="29">
<pad name="P$1" x="0" y="0" drill="1.6"/>
<pad name="P$2" x="5.08" y="0" drill="1.6"/>
<wire x1="-3" y1="8" x2="8" y2="8" width="0.1524" layer="39"/>
<wire x1="8" y1="8" x2="8" y2="-6" width="0.1524" layer="39"/>
<wire x1="8" y1="-6" x2="-3" y2="-6" width="0.1524" layer="39"/>
<wire x1="-3" y1="-6" x2="-3" y2="8" width="0.1524" layer="39"/>
<wire x1="-3.25" y1="8.25" x2="8.25" y2="8.25" width="0.1524" layer="21"/>
<wire x1="8.25" y1="8.25" x2="8.25" y2="-6.25" width="0.1524" layer="21"/>
<wire x1="8.25" y1="-6.25" x2="-3.25" y2="-6.25" width="0.1524" layer="21"/>
<wire x1="-3.25" y1="-6.25" x2="-3.25" y2="8.25" width="0.1524" layer="21"/>
<text x="2.25" y="9.75" size="1.778" layer="25" align="center">&gt;NAME</text>
</package>
<package name="JST-PH-2POS" library_version="34">
<pad name="P$1" x="-1" y="0" drill="0.8"/>
<pad name="P$2" x="1" y="0" drill="0.8"/>
<wire x1="-3" y1="-1.75" x2="3" y2="-1.75" width="0.1524" layer="21"/>
<wire x1="3" y1="-1.75" x2="3" y2="2.5" width="0.1524" layer="21"/>
<wire x1="3" y1="2.5" x2="-3" y2="2.5" width="0.1524" layer="21"/>
<wire x1="-3" y1="2.5" x2="-3" y2="-1.75" width="0.1524" layer="21"/>
<text x="0" y="3.75" size="1.778" layer="25" align="center">&gt;NAME</text>
<wire x1="-3" y1="-1.75" x2="3" y2="-1.75" width="0.1524" layer="39"/>
<wire x1="3" y1="-1.75" x2="3" y2="2.5" width="0.1524" layer="39"/>
<wire x1="3" y1="2.5" x2="-3" y2="2.5" width="0.1524" layer="39"/>
<wire x1="-3" y1="2.5" x2="-3" y2="-1.75" width="0.1524" layer="39"/>
</package>
</packages>
<symbols>
<symbol name="LS05-13BXXR3" library_version="5">
<pin name="AC(L)" x="-12.7" y="5.08" visible="pin" length="short"/>
<pin name="AC(N)" x="-12.7" y="2.54" visible="pin" length="short"/>
<pin name="C+" x="-12.7" y="-2.54" visible="pin" length="short"/>
<pin name="C-" x="-12.7" y="-5.08" visible="pin" length="short"/>
<pin name="VOUT" x="12.7" y="5.08" visible="pin" length="short" rot="R180"/>
<pin name="GND" x="12.7" y="-5.08" visible="pin" length="short" rot="R180"/>
<wire x1="-10.16" y1="7.62" x2="10.16" y2="7.62" width="0.1524" layer="94"/>
<wire x1="10.16" y1="7.62" x2="10.16" y2="-7.62" width="0.1524" layer="94"/>
<wire x1="10.16" y1="-7.62" x2="-10.16" y2="-7.62" width="0.1524" layer="94"/>
<wire x1="-10.16" y1="-7.62" x2="-10.16" y2="7.62" width="0.1524" layer="94"/>
<text x="0" y="-10.16" size="1.778" layer="96" align="center">&gt;VALUE</text>
<text x="0" y="10.16" size="1.778" layer="95" align="center">&gt;NAME</text>
</symbol>
<symbol name="SC0915" library_version="9">
<pin name="VBUS" x="-15.24" y="20.32" length="middle"/>
<pin name="VSYS" x="-15.24" y="17.78" length="middle"/>
<pin name="3V3_EN" x="-15.24" y="7.62" length="middle"/>
<pin name="3V3_OUT" x="-15.24" y="2.54" length="middle"/>
<pin name="RUN" x="-15.24" y="5.08" length="middle"/>
<pin name="26" x="15.24" y="0" length="middle" rot="R180"/>
<pin name="1" x="-15.24" y="-2.54" length="middle"/>
<pin name="2" x="-15.24" y="-5.08" length="middle"/>
<pin name="4" x="-15.24" y="-7.62" length="middle"/>
<pin name="5" x="-15.24" y="-12.7" length="middle"/>
<pin name="6" x="-15.24" y="-15.24" length="middle"/>
<pin name="7" x="-15.24" y="-17.78" length="middle"/>
<pin name="9" x="-15.24" y="-22.86" length="middle"/>
<pin name="10" x="-15.24" y="-25.4" length="middle"/>
<pin name="11" x="-15.24" y="-27.94" length="middle"/>
<pin name="12" x="-15.24" y="-30.48" length="middle"/>
<pin name="14" x="15.24" y="-30.48" length="middle" rot="R180"/>
<pin name="15" x="15.24" y="-27.94" length="middle" rot="R180"/>
<pin name="GND" x="-15.24" y="15.24" length="middle"/>
<pin name="16" x="15.24" y="-25.4" length="middle" rot="R180"/>
<pin name="17" x="15.24" y="-22.86" length="middle" rot="R180"/>
<pin name="19" x="15.24" y="-17.78" length="middle" rot="R180"/>
<pin name="20" x="15.24" y="-15.24" length="middle" rot="R180"/>
<pin name="21" x="15.24" y="-12.7" length="middle" rot="R180"/>
<pin name="22" x="15.24" y="-10.16" length="middle" rot="R180"/>
<pin name="24" x="15.24" y="-5.08" length="middle" rot="R180"/>
<pin name="25" x="15.24" y="-2.54" length="middle" rot="R180"/>
<pin name="AGND" x="-15.24" y="12.7" length="middle"/>
<pin name="27" x="15.24" y="2.54" length="middle" rot="R180"/>
<pin name="29" x="15.24" y="7.62" length="middle" rot="R180"/>
<pin name="31" x="15.24" y="10.16" length="middle" rot="R180"/>
<pin name="32" x="15.24" y="12.7" length="middle" rot="R180"/>
<pin name="34" x="15.24" y="15.24" length="middle" rot="R180"/>
<wire x1="-10.16" y1="22.86" x2="-10.16" y2="-33.02" width="0.1524" layer="94"/>
<wire x1="-10.16" y1="-33.02" x2="10.16" y2="-33.02" width="0.1524" layer="94"/>
<wire x1="10.16" y1="-33.02" x2="10.16" y2="22.86" width="0.1524" layer="94"/>
<wire x1="10.16" y1="22.86" x2="-10.16" y2="22.86" width="0.1524" layer="94"/>
<text x="0" y="25.4" size="1.778" layer="95" align="center">&gt;NAME</text>
<text x="0" y="-35.56" size="1.778" layer="96" align="center">&gt;VALUE</text>
<pin name="VREF" x="15.24" y="20.32" length="middle" rot="R180"/>
</symbol>
<symbol name="SMW312RJT" library_version="14">
<pin name="P$3" x="7.62" y="0" visible="off" length="short" rot="R180"/>
<pin name="P$4" x="-7.62" y="0" visible="off" length="short"/>
<wire x1="-5.08" y1="1.27" x2="-5.08" y2="-1.27" width="0.254" layer="94"/>
<wire x1="-5.08" y1="-1.27" x2="5.08" y2="-1.27" width="0.254" layer="94"/>
<wire x1="5.08" y1="-1.27" x2="5.08" y2="1.27" width="0.254" layer="94"/>
<wire x1="5.08" y1="1.27" x2="-5.08" y2="1.27" width="0.254" layer="94"/>
<text x="0" y="2.54" size="1.778" layer="95" align="center">&gt;NAME</text>
<text x="0" y="-2.54" size="1.778" layer="96" align="center">&gt;VALUE</text>
</symbol>
<symbol name="GBJ2510" library_version="20">
<pin name="AC(L)" x="-10.16" y="2.54" visible="pin" length="short"/>
<pin name="AC(N)" x="-10.16" y="-2.54" visible="pin" length="short"/>
<pin name="VOUT" x="10.16" y="2.54" visible="pin" length="short" rot="R180"/>
<pin name="GND" x="10.16" y="-2.54" visible="pin" length="short" rot="R180"/>
<wire x1="-7.62" y1="5.08" x2="-7.62" y2="-5.08" width="0.1524" layer="94"/>
<wire x1="-7.62" y1="-5.08" x2="7.62" y2="-5.08" width="0.1524" layer="94"/>
<wire x1="7.62" y1="-5.08" x2="7.62" y2="5.08" width="0.1524" layer="94"/>
<wire x1="7.62" y1="5.08" x2="-7.62" y2="5.08" width="0.1524" layer="94"/>
<text x="0" y="7.62" size="1.778" layer="95" align="center">&gt;NAME</text>
<text x="0" y="-7.62" size="1.778" layer="96" align="center">&gt;VALUE</text>
</symbol>
<symbol name="DISP-1743">
<pin name="CRD_DET" x="-15.24" y="22.86" visible="pin" length="short"/>
<pin name="CRD_CS" x="-15.24" y="20.32" visible="pin" length="short"/>
<pin name="IM0" x="-15.24" y="17.78" visible="pin" length="short"/>
<pin name="IM1" x="-15.24" y="15.24" visible="pin" length="short"/>
<pin name="IM2" x="-15.24" y="12.7" visible="pin" length="short"/>
<pin name="IM3" x="-15.24" y="10.16" visible="pin" length="short"/>
<pin name="X-" x="-15.24" y="7.62" visible="pin" length="short"/>
<pin name="Y-" x="-15.24" y="5.08" visible="pin" length="short"/>
<pin name="X+" x="-15.24" y="2.54" visible="pin" length="short"/>
<pin name="Y+" x="-15.24" y="0" visible="pin" length="short"/>
<pin name="BK_LT" x="-15.24" y="-2.54" visible="pin" length="short"/>
<pin name="RST" x="-15.24" y="-5.08" visible="pin" length="short"/>
<pin name="D/C" x="-15.24" y="-7.62" visible="pin" length="short"/>
<pin name="CS" x="-15.24" y="-10.16" visible="pin" length="short"/>
<pin name="MOSI" x="-15.24" y="-12.7" visible="pin" length="short"/>
<pin name="MISO" x="-15.24" y="-15.24" visible="pin" length="short"/>
<pin name="CLK" x="-15.24" y="-17.78" visible="pin" length="short"/>
<pin name="3V3" x="-15.24" y="-20.32" visible="pin" length="short"/>
<pin name="3-5V" x="-15.24" y="-22.86" visible="pin" length="short"/>
<pin name="GND" x="-15.24" y="-25.4" visible="pin" length="short"/>
<pin name="NC$9" x="15.24" y="-25.4" visible="pin" length="short" rot="R180"/>
<pin name="NC$8" x="15.24" y="-22.86" visible="pin" length="short" rot="R180"/>
<pin name="NC$7" x="15.24" y="-20.32" visible="pin" length="short" rot="R180"/>
<pin name="NC$6" x="15.24" y="-17.78" visible="pin" length="short" rot="R180"/>
<pin name="C/D" x="15.24" y="-15.24" visible="pin" length="short" rot="R180"/>
<pin name="WR" x="15.24" y="-12.7" visible="pin" length="short" rot="R180"/>
<pin name="RD" x="15.24" y="-10.16" visible="pin" length="short" rot="R180"/>
<pin name="NC$5" x="15.24" y="-7.62" visible="pin" length="short" rot="R180"/>
<pin name="NC$4" x="15.24" y="-5.08" visible="pin" length="short" rot="R180"/>
<pin name="NC$3" x="15.24" y="-2.54" visible="pin" length="short" rot="R180"/>
<pin name="NC$2" x="15.24" y="0" visible="pin" length="short" rot="R180"/>
<pin name="NC$1" x="15.24" y="2.54" visible="pin" length="short" rot="R180"/>
<pin name="D0" x="15.24" y="5.08" visible="pin" length="short" rot="R180"/>
<pin name="D1" x="15.24" y="7.62" visible="pin" length="short" rot="R180"/>
<pin name="D2" x="15.24" y="10.16" visible="pin" length="short" rot="R180"/>
<pin name="D3" x="15.24" y="12.7" visible="pin" length="short" rot="R180"/>
<pin name="D4" x="15.24" y="15.24" visible="pin" length="short" rot="R180"/>
<pin name="D5" x="15.24" y="17.78" visible="pin" length="short" rot="R180"/>
<pin name="D6" x="15.24" y="20.32" visible="pin" length="short" rot="R180"/>
<pin name="D7" x="15.24" y="22.86" visible="pin" length="short" rot="R180"/>
<wire x1="-12.7" y1="25.4" x2="12.7" y2="25.4" width="0.1524" layer="94"/>
<wire x1="12.7" y1="25.4" x2="12.7" y2="-27.94" width="0.1524" layer="94"/>
<wire x1="12.7" y1="-27.94" x2="-12.7" y2="-27.94" width="0.1524" layer="94"/>
<wire x1="-12.7" y1="-27.94" x2="-12.7" y2="22.86" width="0.1524" layer="94"/>
<wire x1="-12.7" y1="22.86" x2="-12.7" y2="25.4" width="0.1524" layer="94"/>
<wire x1="-12.7" y1="22.86" x2="-12.065" y2="22.86" width="0.1524" layer="94"/>
<wire x1="-12.065" y1="22.86" x2="-10.795" y2="22.86" width="0.254" layer="94"/>
<wire x1="-12.7" y1="20.32" x2="-12.065" y2="20.32" width="0.1524" layer="94"/>
<wire x1="-12.065" y1="20.32" x2="-10.795" y2="20.32" width="0.254" layer="94"/>
<wire x1="-12.7" y1="17.78" x2="-12.065" y2="17.78" width="0.1524" layer="94"/>
<wire x1="-12.065" y1="17.78" x2="-10.795" y2="17.78" width="0.254" layer="94"/>
<wire x1="-12.7" y1="15.24" x2="-12.065" y2="15.24" width="0.1524" layer="94"/>
<wire x1="-12.065" y1="15.24" x2="-10.795" y2="15.24" width="0.254" layer="94"/>
<wire x1="-12.7" y1="12.7" x2="-12.065" y2="12.7" width="0.1524" layer="94"/>
<wire x1="-12.065" y1="12.7" x2="-10.795" y2="12.7" width="0.254" layer="94"/>
<wire x1="-12.7" y1="10.16" x2="-12.065" y2="10.16" width="0.1524" layer="94"/>
<wire x1="-12.065" y1="10.16" x2="-10.795" y2="10.16" width="0.254" layer="94"/>
<wire x1="-12.7" y1="7.62" x2="-12.065" y2="7.62" width="0.1524" layer="94"/>
<wire x1="-12.065" y1="7.62" x2="-10.795" y2="7.62" width="0.254" layer="94"/>
<wire x1="-12.7" y1="5.08" x2="-12.065" y2="5.08" width="0.1524" layer="94"/>
<wire x1="-12.065" y1="5.08" x2="-10.795" y2="5.08" width="0.254" layer="94"/>
<wire x1="-12.7" y1="2.54" x2="-12.065" y2="2.54" width="0.1524" layer="94"/>
<wire x1="-12.065" y1="2.54" x2="-10.795" y2="2.54" width="0.254" layer="94"/>
<wire x1="-12.7" y1="0" x2="-12.065" y2="0" width="0.1524" layer="94"/>
<wire x1="-12.065" y1="0" x2="-10.795" y2="0" width="0.254" layer="94"/>
<wire x1="-12.7" y1="-2.54" x2="-12.065" y2="-2.54" width="0.1524" layer="94"/>
<wire x1="-12.065" y1="-2.54" x2="-10.795" y2="-2.54" width="0.254" layer="94"/>
<wire x1="-12.7" y1="-5.08" x2="-12.065" y2="-5.08" width="0.1524" layer="94"/>
<wire x1="-12.065" y1="-5.08" x2="-10.795" y2="-5.08" width="0.254" layer="94"/>
<wire x1="-12.7" y1="-7.62" x2="-12.065" y2="-7.62" width="0.1524" layer="94"/>
<wire x1="-12.065" y1="-7.62" x2="-10.795" y2="-7.62" width="0.254" layer="94"/>
<wire x1="-12.7" y1="-10.16" x2="-12.065" y2="-10.16" width="0.1524" layer="94"/>
<wire x1="-12.065" y1="-10.16" x2="-10.795" y2="-10.16" width="0.254" layer="94"/>
<wire x1="-12.7" y1="-12.7" x2="-12.065" y2="-12.7" width="0.1524" layer="94"/>
<wire x1="-12.065" y1="-12.7" x2="-10.795" y2="-12.7" width="0.254" layer="94"/>
<wire x1="-12.7" y1="-15.24" x2="-12.065" y2="-15.24" width="0.1524" layer="94"/>
<wire x1="-12.065" y1="-15.24" x2="-10.795" y2="-15.24" width="0.254" layer="94"/>
<wire x1="-12.7" y1="-17.78" x2="-12.065" y2="-17.78" width="0.1524" layer="94"/>
<wire x1="-12.065" y1="-17.78" x2="-10.795" y2="-17.78" width="0.254" layer="94"/>
<wire x1="-12.7" y1="-20.32" x2="-12.065" y2="-20.32" width="0.1524" layer="94"/>
<wire x1="-12.065" y1="-20.32" x2="-10.795" y2="-20.32" width="0.254" layer="94"/>
<wire x1="-12.7" y1="-22.86" x2="-12.065" y2="-22.86" width="0.1524" layer="94"/>
<wire x1="-12.065" y1="-22.86" x2="-10.795" y2="-22.86" width="0.254" layer="94"/>
<wire x1="-12.7" y1="-25.4" x2="-12.065" y2="-25.4" width="0.1524" layer="94"/>
<wire x1="-12.065" y1="-25.4" x2="-10.795" y2="-25.4" width="0.254" layer="94"/>
<wire x1="12.7" y1="-25.4" x2="12.065" y2="-25.4" width="0.1524" layer="94"/>
<wire x1="12.065" y1="-25.4" x2="10.795" y2="-25.4" width="0.254" layer="94"/>
<wire x1="12.7" y1="-22.86" x2="12.065" y2="-22.86" width="0.1524" layer="94"/>
<wire x1="12.065" y1="-22.86" x2="10.795" y2="-22.86" width="0.254" layer="94"/>
<wire x1="12.7" y1="-20.32" x2="12.065" y2="-20.32" width="0.1524" layer="94"/>
<wire x1="12.065" y1="-20.32" x2="10.795" y2="-20.32" width="0.254" layer="94"/>
<wire x1="12.7" y1="-17.78" x2="12.065" y2="-17.78" width="0.1524" layer="94"/>
<wire x1="12.065" y1="-17.78" x2="10.795" y2="-17.78" width="0.254" layer="94"/>
<wire x1="12.7" y1="-15.24" x2="12.065" y2="-15.24" width="0.1524" layer="94"/>
<wire x1="12.065" y1="-15.24" x2="10.795" y2="-15.24" width="0.254" layer="94"/>
<wire x1="12.7" y1="-12.7" x2="12.065" y2="-12.7" width="0.1524" layer="94"/>
<wire x1="12.065" y1="-12.7" x2="10.795" y2="-12.7" width="0.254" layer="94"/>
<wire x1="12.7" y1="-10.16" x2="12.065" y2="-10.16" width="0.1524" layer="94"/>
<wire x1="12.065" y1="-10.16" x2="10.795" y2="-10.16" width="0.254" layer="94"/>
<wire x1="12.7" y1="-7.62" x2="12.065" y2="-7.62" width="0.1524" layer="94"/>
<wire x1="12.065" y1="-7.62" x2="10.795" y2="-7.62" width="0.254" layer="94"/>
<wire x1="12.7" y1="-5.08" x2="12.065" y2="-5.08" width="0.1524" layer="94"/>
<wire x1="12.065" y1="-5.08" x2="10.795" y2="-5.08" width="0.254" layer="94"/>
<wire x1="12.7" y1="-2.54" x2="12.065" y2="-2.54" width="0.1524" layer="94"/>
<wire x1="12.065" y1="-2.54" x2="10.795" y2="-2.54" width="0.254" layer="94"/>
<wire x1="12.7" y1="0" x2="12.065" y2="0" width="0.1524" layer="94"/>
<wire x1="12.065" y1="0" x2="10.795" y2="0" width="0.254" layer="94"/>
<wire x1="12.7" y1="2.54" x2="12.065" y2="2.54" width="0.1524" layer="94"/>
<wire x1="12.065" y1="2.54" x2="10.795" y2="2.54" width="0.254" layer="94"/>
<wire x1="12.7" y1="5.08" x2="12.065" y2="5.08" width="0.1524" layer="94"/>
<wire x1="12.065" y1="5.08" x2="10.795" y2="5.08" width="0.254" layer="94"/>
<wire x1="12.7" y1="7.62" x2="12.065" y2="7.62" width="0.1524" layer="94"/>
<wire x1="12.065" y1="7.62" x2="10.795" y2="7.62" width="0.254" layer="94"/>
<wire x1="12.7" y1="10.16" x2="12.065" y2="10.16" width="0.1524" layer="94"/>
<wire x1="12.065" y1="10.16" x2="10.795" y2="10.16" width="0.254" layer="94"/>
<wire x1="12.7" y1="12.7" x2="12.065" y2="12.7" width="0.1524" layer="94"/>
<wire x1="12.065" y1="12.7" x2="10.795" y2="12.7" width="0.254" layer="94"/>
<wire x1="12.7" y1="15.24" x2="12.065" y2="15.24" width="0.1524" layer="94"/>
<wire x1="12.065" y1="15.24" x2="10.795" y2="15.24" width="0.254" layer="94"/>
<wire x1="12.7" y1="17.78" x2="12.065" y2="17.78" width="0.1524" layer="94"/>
<wire x1="12.065" y1="17.78" x2="10.795" y2="17.78" width="0.254" layer="94"/>
<wire x1="12.7" y1="20.32" x2="12.065" y2="20.32" width="0.1524" layer="94"/>
<wire x1="12.065" y1="20.32" x2="10.795" y2="20.32" width="0.254" layer="94"/>
<wire x1="12.7" y1="22.86" x2="12.065" y2="22.86" width="0.1524" layer="94"/>
<wire x1="12.065" y1="22.86" x2="10.795" y2="22.86" width="0.254" layer="94"/>
<text x="0" y="26.67" size="1.778" layer="95" align="center">&gt;NAME</text>
<text x="0" y="-29.21" size="1.778" layer="96" align="center">&gt;VALUE</text>
</symbol>
<symbol name="TB008A-508-02BE" library_version="29">
<pin name="1" x="-5.08" y="2.54" visible="pin" length="short"/>
<pin name="2" x="-5.08" y="-2.54" visible="pin" length="short"/>
<wire x1="-2.54" y1="5.08" x2="-2.54" y2="2.54" width="0.1524" layer="94"/>
<wire x1="-2.54" y1="2.54" x2="-2.54" y2="-2.54" width="0.1524" layer="94"/>
<wire x1="-2.54" y1="-2.54" x2="-2.54" y2="-5.08" width="0.1524" layer="94"/>
<wire x1="-2.54" y1="-5.08" x2="5.08" y2="-5.08" width="0.1524" layer="94"/>
<wire x1="5.08" y1="-5.08" x2="5.08" y2="5.08" width="0.1524" layer="94"/>
<wire x1="5.08" y1="5.08" x2="-2.54" y2="5.08" width="0.1524" layer="94"/>
<wire x1="-2.54" y1="2.54" x2="-1.905" y2="2.54" width="0.1524" layer="94"/>
<wire x1="-2.54" y1="-2.54" x2="-1.905" y2="-2.54" width="0.1524" layer="94"/>
<wire x1="-1.905" y1="2.54" x2="-0.635" y2="2.54" width="0.254" layer="94"/>
<wire x1="-1.905" y1="-2.54" x2="-0.635" y2="-2.54" width="0.254" layer="94"/>
<text x="3.81" y="0" size="1.778" layer="95" rot="R90" align="center">&gt;NAME</text>
<text x="6.35" y="0" size="1.778" layer="96" rot="R90" align="center">&gt;VALUE</text>
</symbol>
<symbol name="JST-PH-2POS" library_version="34">
<pin name="1" x="-5.08" y="2.54" visible="pin" length="short"/>
<pin name="2" x="-5.08" y="-2.54" visible="pin" length="short"/>
<wire x1="-2.54" y1="5.08" x2="-2.54" y2="2.54" width="0.1524" layer="94"/>
<wire x1="-2.54" y1="2.54" x2="-2.54" y2="-2.54" width="0.1524" layer="94"/>
<wire x1="-2.54" y1="-2.54" x2="-2.54" y2="-5.08" width="0.1524" layer="94"/>
<wire x1="-2.54" y1="-5.08" x2="5.08" y2="-5.08" width="0.1524" layer="94"/>
<wire x1="5.08" y1="-5.08" x2="5.08" y2="5.08" width="0.1524" layer="94"/>
<wire x1="5.08" y1="5.08" x2="-2.54" y2="5.08" width="0.1524" layer="94"/>
<wire x1="-2.54" y1="2.54" x2="-1.905" y2="2.54" width="0.1524" layer="94"/>
<wire x1="-2.54" y1="-2.54" x2="-1.905" y2="-2.54" width="0.1524" layer="94"/>
<wire x1="-1.905" y1="2.54" x2="-0.635" y2="2.54" width="0.254" layer="94"/>
<wire x1="-1.905" y1="-2.54" x2="-0.635" y2="-2.54" width="0.254" layer="94"/>
<text x="3.81" y="0" size="1.778" layer="95" rot="R90" align="center">&gt;NAME</text>
<text x="6.35" y="0" size="1.778" layer="95" rot="R90" align="center">&gt;VALUE</text>
</symbol>
</symbols>
<devicesets>
<deviceset name="LS05-13BXXR3" prefix="BR" library_version="5">
<gates>
<gate name="G$1" symbol="LS05-13BXXR3" x="0" y="0"/>
</gates>
<devices>
<device name="" package="LS05-13BXXR3">
<connects>
<connect gate="G$1" pin="AC(L)" pad="P$1"/>
<connect gate="G$1" pin="AC(N)" pad="P$2"/>
<connect gate="G$1" pin="C+" pad="P$3"/>
<connect gate="G$1" pin="C-" pad="P$4"/>
<connect gate="G$1" pin="GND" pad="P$5"/>
<connect gate="G$1" pin="VOUT" pad="P$6"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
</devices>
</deviceset>
<deviceset name="SC0915" library_version="9">
<gates>
<gate name="G$1" symbol="SC0915" x="0" y="0"/>
</gates>
<devices>
<device name="" package="SC0915">
<connects>
<connect gate="G$1" pin="1" pad="P$1"/>
<connect gate="G$1" pin="10" pad="P$10"/>
<connect gate="G$1" pin="11" pad="P$11"/>
<connect gate="G$1" pin="12" pad="P$12"/>
<connect gate="G$1" pin="14" pad="P$14"/>
<connect gate="G$1" pin="15" pad="P$15"/>
<connect gate="G$1" pin="16" pad="P$16"/>
<connect gate="G$1" pin="17" pad="P$17"/>
<connect gate="G$1" pin="19" pad="P$19"/>
<connect gate="G$1" pin="2" pad="P$2"/>
<connect gate="G$1" pin="20" pad="P$20"/>
<connect gate="G$1" pin="21" pad="P$21"/>
<connect gate="G$1" pin="22" pad="P$22"/>
<connect gate="G$1" pin="24" pad="P$24"/>
<connect gate="G$1" pin="25" pad="P$25"/>
<connect gate="G$1" pin="26" pad="P$26"/>
<connect gate="G$1" pin="27" pad="P$27"/>
<connect gate="G$1" pin="29" pad="P$29"/>
<connect gate="G$1" pin="31" pad="P$31"/>
<connect gate="G$1" pin="32" pad="P$32"/>
<connect gate="G$1" pin="34" pad="P$34"/>
<connect gate="G$1" pin="3V3_EN" pad="P$37"/>
<connect gate="G$1" pin="3V3_OUT" pad="P$36"/>
<connect gate="G$1" pin="4" pad="P$4"/>
<connect gate="G$1" pin="5" pad="P$5"/>
<connect gate="G$1" pin="6" pad="P$6"/>
<connect gate="G$1" pin="7" pad="P$7"/>
<connect gate="G$1" pin="9" pad="P$9"/>
<connect gate="G$1" pin="AGND" pad="P$33"/>
<connect gate="G$1" pin="GND" pad="P$3 P$8 P$13 P$18 P$23 P$28 P$38" route="any"/>
<connect gate="G$1" pin="RUN" pad="P$30"/>
<connect gate="G$1" pin="VBUS" pad="P$40"/>
<connect gate="G$1" pin="VREF" pad="P$35"/>
<connect gate="G$1" pin="VSYS" pad="P$39"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
</devices>
</deviceset>
<deviceset name="SMW312RJT" library_version="14">
<gates>
<gate name="G$1" symbol="SMW312RJT" x="0" y="0"/>
</gates>
<devices>
<device name="" package="SMW312RJT">
<connects>
<connect gate="G$1" pin="P$3" pad="P$1"/>
<connect gate="G$1" pin="P$4" pad="P$2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
</devices>
</deviceset>
<deviceset name="GBJ2510" library_version="20">
<gates>
<gate name="G$1" symbol="GBJ2510" x="0" y="0"/>
</gates>
<devices>
<device name="" package="GBJ2510">
<connects>
<connect gate="G$1" pin="AC(L)" pad="P$2"/>
<connect gate="G$1" pin="AC(N)" pad="P$3"/>
<connect gate="G$1" pin="GND" pad="P$4"/>
<connect gate="G$1" pin="VOUT" pad="P$1"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
</devices>
</deviceset>
<deviceset name="DISP-1743">
<gates>
<gate name="G$1" symbol="DISP-1743" x="0" y="0"/>
</gates>
<devices>
<device name="" package="DISP-1743">
<connects>
<connect gate="G$1" pin="3-5V" pad="P$19"/>
<connect gate="G$1" pin="3V3" pad="P$18"/>
<connect gate="G$1" pin="BK_LT" pad="P$11"/>
<connect gate="G$1" pin="C/D" pad="P$25"/>
<connect gate="G$1" pin="CLK" pad="P$17"/>
<connect gate="G$1" pin="CRD_CS" pad="P$2"/>
<connect gate="G$1" pin="CRD_DET" pad="P$1"/>
<connect gate="G$1" pin="CS" pad="P$14"/>
<connect gate="G$1" pin="D/C" pad="P$13"/>
<connect gate="G$1" pin="D0" pad="P$33"/>
<connect gate="G$1" pin="D1" pad="P$34"/>
<connect gate="G$1" pin="D2" pad="P$35"/>
<connect gate="G$1" pin="D3" pad="P$36"/>
<connect gate="G$1" pin="D4" pad="P$37"/>
<connect gate="G$1" pin="D5" pad="P$38"/>
<connect gate="G$1" pin="D6" pad="P$39"/>
<connect gate="G$1" pin="D7" pad="P$40"/>
<connect gate="G$1" pin="GND" pad="P$20"/>
<connect gate="G$1" pin="IM0" pad="P$3"/>
<connect gate="G$1" pin="IM1" pad="P$4"/>
<connect gate="G$1" pin="IM2" pad="P$5"/>
<connect gate="G$1" pin="IM3" pad="P$6"/>
<connect gate="G$1" pin="MISO" pad="P$16"/>
<connect gate="G$1" pin="MOSI" pad="P$15"/>
<connect gate="G$1" pin="NC$1" pad="P$32"/>
<connect gate="G$1" pin="NC$2" pad="P$31"/>
<connect gate="G$1" pin="NC$3" pad="P$30"/>
<connect gate="G$1" pin="NC$4" pad="P$29"/>
<connect gate="G$1" pin="NC$5" pad="P$28"/>
<connect gate="G$1" pin="NC$6" pad="P$24"/>
<connect gate="G$1" pin="NC$7" pad="P$23"/>
<connect gate="G$1" pin="NC$8" pad="P$22"/>
<connect gate="G$1" pin="NC$9" pad="P$21"/>
<connect gate="G$1" pin="RD" pad="P$27"/>
<connect gate="G$1" pin="RST" pad="P$12"/>
<connect gate="G$1" pin="WR" pad="P$26"/>
<connect gate="G$1" pin="X+" pad="P$9"/>
<connect gate="G$1" pin="X-" pad="P$7"/>
<connect gate="G$1" pin="Y+" pad="P$10"/>
<connect gate="G$1" pin="Y-" pad="P$8"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
</devices>
</deviceset>
<deviceset name="TB008A-508-02BE" library_version="29">
<gates>
<gate name="G$1" symbol="TB008A-508-02BE" x="0" y="0"/>
</gates>
<devices>
<device name="" package="TB008A-508-02BE">
<connects>
<connect gate="G$1" pin="1" pad="P$1"/>
<connect gate="G$1" pin="2" pad="P$2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
</devices>
</deviceset>
<deviceset name="JST-PH-2POS" prefix="H" library_version="34">
<gates>
<gate name="G$1" symbol="JST-PH-2POS" x="0" y="0"/>
</gates>
<devices>
<device name="" package="JST-PH-2POS">
<connects>
<connect gate="G$1" pin="1" pad="P$1"/>
<connect gate="G$1" pin="2" pad="P$2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
</devices>
</deviceset>
</devicesets>
</library>
<library name="VOSTOK_KRAETON_LIB" urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ">
<packages>
<package name="SAMSUNG_CAP-0402">
<smd name="P$1" x="-0.515" y="0" dx="0.58" dy="0.7" layer="1" roundness="10"/>
<smd name="P$2" x="0.515" y="0" dx="0.58" dy="0.7" layer="1" roundness="10"/>
<text x="0" y="0.635" size="0.508" layer="25" align="center">&gt;NAME</text>
<wire x1="-0.8128" y1="0.3556" x2="0.8128" y2="0.3556" width="0.127" layer="39"/>
<wire x1="0.8128" y1="0.3556" x2="0.8128" y2="-0.3556" width="0.127" layer="39"/>
<wire x1="0.8128" y1="-0.3556" x2="-0.8128" y2="-0.3556" width="0.127" layer="39"/>
<wire x1="-0.8128" y1="-0.3556" x2="-0.8128" y2="0.3556" width="0.127" layer="39"/>
</package>
<package name="SAMSUNG_CAP-0603">
<smd name="P$1" x="-0.72" y="0" dx="0.76" dy="0.85" layer="1" roundness="10"/>
<smd name="P$2" x="0.72" y="0" dx="0.76" dy="0.85" layer="1" roundness="10"/>
<wire x1="-1.1176" y1="0.4572" x2="1.1176" y2="0.4572" width="0.1524" layer="39"/>
<wire x1="1.1176" y1="0.4572" x2="1.1176" y2="-0.4572" width="0.1524" layer="39"/>
<wire x1="1.1176" y1="-0.4572" x2="-1.1176" y2="-0.4572" width="0.1524" layer="39"/>
<wire x1="-1.1176" y1="-0.4572" x2="-1.1176" y2="0.4572" width="0.1524" layer="39"/>
<text x="0" y="0.889" size="0.508" layer="25" align="center">&gt;NAME</text>
</package>
<package name="SAMSUNG_CAP-0805">
<smd name="P$1" x="-0.905" y="0" dx="0.95" dy="1.35" layer="1" roundness="10"/>
<smd name="P$2" x="0.905" y="0" dx="0.95" dy="1.35" layer="1" roundness="10"/>
<text x="0" y="1.27" size="0.635" layer="25" align="center">&gt;NAME</text>
<wire x1="-1.397" y1="0.6858" x2="1.397" y2="0.6858" width="0.127" layer="39"/>
<wire x1="1.397" y1="0.6858" x2="1.397" y2="-0.6858" width="0.127" layer="39"/>
<wire x1="1.397" y1="-0.6858" x2="-1.397" y2="-0.6858" width="0.127" layer="39"/>
<wire x1="-1.397" y1="-0.6858" x2="-1.397" y2="0.6858" width="0.127" layer="39"/>
</package>
<package name="SAMSUNG_CAP-1206">
<smd name="P$1" x="-1.475" y="0" dx="1.25" dy="1.8" layer="1" roundness="10"/>
<smd name="P$2" x="1.475" y="0" dx="1.25" dy="1.8" layer="1" roundness="10"/>
<wire x1="-2.159" y1="0.889" x2="2.159" y2="0.889" width="0.1524" layer="39"/>
<wire x1="2.159" y1="0.889" x2="2.159" y2="-0.889" width="0.1524" layer="39"/>
<wire x1="2.159" y1="-0.889" x2="-2.159" y2="-0.889" width="0.1524" layer="39"/>
<wire x1="-2.159" y1="-0.889" x2="-2.159" y2="0.889" width="0.1524" layer="39"/>
<text x="0" y="1.397" size="0.635" layer="25" align="center">&gt;NAME</text>
</package>
<package name="KYOCERA_CAP-2225">
<smd name="P$1" x="-2.575" y="0" dx="1.65" dy="6.7" layer="1" roundness="10"/>
<smd name="P$2" x="2.575" y="0" dx="1.65" dy="6.7" layer="1" roundness="10"/>
<text x="0" y="3.81" size="0.635" layer="25" align="center">&gt;NAME</text>
<wire x1="-3.302" y1="3.302" x2="3.302" y2="3.302" width="0.1524" layer="39"/>
<wire x1="3.302" y1="3.302" x2="3.302" y2="-3.302" width="0.1524" layer="39"/>
<wire x1="3.302" y1="-3.302" x2="-3.302" y2="-3.302" width="0.1524" layer="39"/>
<wire x1="-3.302" y1="-3.302" x2="-3.302" y2="3.302" width="0.1524" layer="39"/>
</package>
<package name="WALSIN_CAP-1210" library_version="215">
<smd name="P$1" x="-1.75" y="0" dx="1.25" dy="2" layer="1"/>
<smd name="P$2" x="1.75" y="0" dx="1.25" dy="2" layer="1"/>
<wire x1="-1.7" y1="1.2" x2="1.7" y2="1.2" width="0.1524" layer="39"/>
<wire x1="1.7" y1="1.2" x2="1.7" y2="-1.2" width="0.1524" layer="39"/>
<wire x1="1.7" y1="-1.2" x2="-1.7" y2="-1.2" width="0.1524" layer="39"/>
<wire x1="-1.7" y1="-1.2" x2="-1.7" y2="1.2" width="0.1524" layer="39"/>
<text x="0" y="1.7" size="0.635" layer="21" align="center">&gt;NAME</text>
</package>
<package name="TDK-CGA_CAP-1210" library_version="215">
<smd name="P$1" x="-1.75" y="0" dx="1.2" dy="2.5" layer="1"/>
<smd name="P$2" x="1.75" y="0" dx="1.2" dy="2.5" layer="1"/>
<wire x1="-1.7" y1="1.2" x2="1.7" y2="1.2" width="0.1524" layer="39"/>
<wire x1="1.7" y1="1.2" x2="1.7" y2="-1.2" width="0.1524" layer="39"/>
<wire x1="1.7" y1="-1.2" x2="-1.7" y2="-1.2" width="0.1524" layer="39"/>
<wire x1="-1.7" y1="-1.2" x2="-1.7" y2="1.2" width="0.1524" layer="39"/>
<text x="0" y="1.7" size="0.635" layer="21" align="center">&gt;NAME</text>
</package>
<package name="TDK-CGA_CAP-0805" library_version="215">
<smd name="P$1" x="-0.905" y="0" dx="0.95" dy="1.35" layer="1" roundness="10"/>
<smd name="P$2" x="0.905" y="0" dx="0.95" dy="1.35" layer="1" roundness="10"/>
<text x="0" y="1.27" size="0.635" layer="25" align="center">&gt;NAME</text>
<wire x1="-1.397" y1="0.6858" x2="1.397" y2="0.6858" width="0.127" layer="39"/>
<wire x1="1.397" y1="0.6858" x2="1.397" y2="-0.6858" width="0.127" layer="39"/>
<wire x1="1.397" y1="-0.6858" x2="-1.397" y2="-0.6858" width="0.127" layer="39"/>
<wire x1="-1.397" y1="-0.6858" x2="-1.397" y2="0.6858" width="0.127" layer="39"/>
</package>
<package name="YAGEO_RES-0805">
<smd name="P$1" x="-1.05" y="0" dx="0.9" dy="1.2" layer="1" roundness="5"/>
<smd name="P$2" x="1.05" y="0" dx="0.9" dy="1.2" layer="1" roundness="5"/>
<text x="0" y="1.016" size="0.635" layer="25" align="center">&gt;NAME</text>
<wire x1="-1.524" y1="0.635" x2="1.524" y2="0.635" width="0.1524" layer="39"/>
<wire x1="1.524" y1="0.635" x2="1.524" y2="-0.635" width="0.1524" layer="39"/>
<wire x1="1.524" y1="-0.635" x2="-1.524" y2="-0.635" width="0.1524" layer="39"/>
<wire x1="-1.524" y1="-0.635" x2="-1.524" y2="0.635" width="0.1524" layer="39"/>
</package>
<package name="BOURNS_RES-0612">
<smd name="P$1" x="-0.7747" y="0" dx="0.7112" dy="3.81" layer="1" roundness="10"/>
<smd name="P$2" x="0.7747" y="0" dx="0.7112" dy="3.81" layer="1" roundness="10"/>
<text x="-2.794" y="0" size="0.635" layer="25" rot="R90" align="center">&gt;NAME</text>
<wire x1="-1.143" y1="1.905" x2="1.143" y2="1.905" width="0.1524" layer="39"/>
<wire x1="1.143" y1="1.905" x2="1.143" y2="-1.905" width="0.1524" layer="39"/>
<wire x1="1.143" y1="-1.905" x2="-1.143" y2="-1.905" width="0.1524" layer="39"/>
<wire x1="-1.143" y1="-1.905" x2="-1.143" y2="1.905" width="0.1524" layer="39"/>
</package>
<package name="YAGEO_RES-0603">
<smd name="P$1" x="-0.85" y="0" dx="0.9" dy="0.8" layer="1" roundness="10"/>
<smd name="P$2" x="0.85" y="0" dx="0.9" dy="0.8" layer="1" roundness="10"/>
<wire x1="-1.27" y1="0.381" x2="1.27" y2="0.381" width="0.1524" layer="39"/>
<wire x1="1.27" y1="0.381" x2="1.27" y2="-0.381" width="0.1524" layer="39"/>
<wire x1="1.27" y1="-0.381" x2="-1.27" y2="-0.381" width="0.1524" layer="39"/>
<wire x1="-1.27" y1="-0.381" x2="-1.27" y2="0.381" width="0.1524" layer="39"/>
<text x="0" y="0.762" size="0.508" layer="25" align="center">&gt;NAME</text>
</package>
<package name="YAGEO_RES-0402">
<smd name="P$1" x="-0.5" y="0" dx="0.5" dy="0.6" layer="1" roundness="10"/>
<smd name="P$2" x="0.5" y="0" dx="0.5" dy="0.6" layer="1" roundness="10"/>
<wire x1="-0.762" y1="0.3048" x2="0.762" y2="0.3048" width="0.1524" layer="39"/>
<wire x1="0.762" y1="0.3048" x2="0.762" y2="-0.3048" width="0.1524" layer="39"/>
<wire x1="0.762" y1="-0.3048" x2="-0.762" y2="-0.3048" width="0.1524" layer="39"/>
<wire x1="-0.762" y1="-0.3048" x2="-0.762" y2="0.3048" width="0.1524" layer="39"/>
<text x="0" y="0.762" size="0.508" layer="25" align="center">&gt;NAME</text>
</package>
<package name="YAGEO_RES-1206">
<smd name="P$1" x="-1.6" y="0" dx="1" dy="1.5" layer="1" roundness="10"/>
<smd name="P$2" x="1.6" y="0" dx="1" dy="1.5" layer="1" roundness="10"/>
<wire x1="-2.032" y1="0.762" x2="2.032" y2="0.762" width="0.1524" layer="39"/>
<wire x1="2.032" y1="0.762" x2="2.032" y2="-0.762" width="0.1524" layer="39"/>
<wire x1="2.032" y1="-0.762" x2="-2.032" y2="-0.762" width="0.1524" layer="39"/>
<wire x1="-2.032" y1="-0.762" x2="-2.032" y2="0.762" width="0.1524" layer="39"/>
<text x="0" y="1.27" size="0.635" layer="25" align="center">&gt;NAME</text>
</package>
<package name="ASPI-0530HI-2R2M-T2">
<smd name="P$1" x="-2.5" y="0" dx="2" dy="2.5" layer="1" roundness="5"/>
<smd name="P$2" x="2.5" y="0" dx="2" dy="2.5" layer="1" roundness="5"/>
<wire x1="-3.175" y1="3.175" x2="3.175" y2="3.175" width="0.127" layer="39"/>
<wire x1="3.175" y1="3.175" x2="3.175" y2="-3.175" width="0.127" layer="39"/>
<wire x1="3.175" y1="-3.175" x2="-3.175" y2="-3.175" width="0.127" layer="39"/>
<wire x1="-3.175" y1="-3.175" x2="-3.175" y2="3.175" width="0.127" layer="39"/>
<text x="0" y="3.81" size="0.635" layer="25" align="center">&gt;NAME</text>
</package>
<package name="SRP1270-4R7M">
<smd name="P$1" x="-5.50545" y="0" dx="4.0005" dy="4.4958" layer="1"/>
<smd name="P$2" x="5.50545" y="0" dx="4.0005" dy="4.4958" layer="1"/>
<wire x1="-6.858" y1="-6.35" x2="6.858" y2="-6.35" width="0.1524" layer="39"/>
<wire x1="6.858" y1="-6.35" x2="6.858" y2="6.35" width="0.1524" layer="39"/>
<wire x1="6.858" y1="6.35" x2="-6.858" y2="6.35" width="0.1524" layer="39"/>
<wire x1="-6.858" y1="6.35" x2="-6.858" y2="-6.35" width="0.1524" layer="39"/>
<text x="0" y="8.128" size="0.635" layer="25" font="vector" align="center">&gt;NAME</text>
</package>
<package name="TPS564247DRLR">
<smd name="P$1" x="-0.74" y="0.5" dx="0.67" dy="0.3" layer="1" roundness="5"/>
<smd name="P$2" x="-0.74" y="0" dx="0.67" dy="0.3" layer="1" roundness="5"/>
<smd name="P$3" x="-0.74" y="-0.5" dx="0.67" dy="0.3" layer="1" roundness="5"/>
<smd name="P$4" x="0.74" y="-0.5" dx="0.67" dy="0.3" layer="1" roundness="5"/>
<smd name="P$5" x="0.74" y="0" dx="0.67" dy="0.3" layer="1" roundness="5"/>
<smd name="P$6" x="0.74" y="0.5" dx="0.67" dy="0.3" layer="1" roundness="5"/>
<wire x1="-0.889" y1="0.889" x2="0.889" y2="0.889" width="0.1524" layer="39"/>
<wire x1="0.889" y1="0.889" x2="0.889" y2="-0.889" width="0.1524" layer="39"/>
<wire x1="0.889" y1="-0.889" x2="-0.889" y2="-0.889" width="0.1524" layer="39"/>
<wire x1="-0.889" y1="-0.889" x2="-0.889" y2="0.889" width="0.1524" layer="39"/>
<text x="0" y="1.27" size="0.508" layer="25" align="center">&gt;NAME</text>
</package>
<package name="FC-203-22" library_version="222">
<pad name="P$1" x="-8.9" y="2.5" drill="1.17"/>
<pad name="P$2" x="-8.9" y="-2.5" drill="1.17"/>
<pad name="P$3" x="8.9" y="2.5" drill="1.17"/>
<pad name="P$4" x="8.9" y="-2.5" drill="1.17"/>
<wire x1="-11" y1="4" x2="-11" y2="-4" width="0.1524" layer="21"/>
<wire x1="-11" y1="-4" x2="11" y2="-4" width="0.1524" layer="21"/>
<wire x1="11" y1="-4" x2="11" y2="4" width="0.1524" layer="21"/>
<wire x1="11" y1="4" x2="-11" y2="4" width="0.1524" layer="21"/>
<text x="0" y="6" size="1.778" layer="25" align="center">&gt;NAME</text>
<wire x1="-11.25" y1="4.25" x2="-11.25" y2="-4.25" width="0.1524" layer="39"/>
<wire x1="-11.25" y1="-4.25" x2="11.25" y2="-4.25" width="0.1524" layer="39"/>
<wire x1="11.25" y1="-4.25" x2="11.25" y2="4.25" width="0.1524" layer="39"/>
<wire x1="11.25" y1="4.25" x2="-11.25" y2="4.25" width="0.1524" layer="39"/>
</package>
<package name="100YXJ330MGC16X25" library_version="225">
<pad name="VCC" x="-3.75" y="0" drill="1"/>
<pad name="VDD" x="3.75" y="0" drill="1"/>
<circle x="0" y="0" radius="8.25" width="0.127" layer="39"/>
<polygon width="0.127" layer="21" pour="solid">
<vertex x="0" y="8.5"/>
<vertex x="0" y="-8.5"/>
<vertex x="0.95170625" y="-8.44655"/>
<vertex x="1.89143125" y="-8.2868875"/>
<vertex x="2.807390625" y="-8.023003125"/>
<vertex x="3.68801875" y="-7.658234375"/>
<vertex x="4.5222875" y="-7.197146875"/>
<vertex x="5.299659375" y="-6.645571875"/>
<vertex x="6.01040625" y="-6.01040625"/>
<vertex x="6.645571875" y="-5.299659375"/>
<vertex x="7.197146875" y="-4.5222875"/>
<vertex x="7.658234375" y="-3.68801875"/>
<vertex x="8.023003125" y="-2.807390625"/>
<vertex x="8.2868875" y="-1.89143125"/>
<vertex x="8.44655" y="-0.95170625"/>
<vertex x="8.5" y="0"/>
<vertex x="8.44655" y="0.95170625"/>
<vertex x="8.2868875" y="1.89143125"/>
<vertex x="8.023003125" y="2.807390625"/>
<vertex x="7.658234375" y="3.68801875"/>
<vertex x="7.197146875" y="4.5222875"/>
<vertex x="6.645571875" y="5.299659375"/>
<vertex x="6.01040625" y="6.01040625"/>
<vertex x="5.299659375" y="6.645571875"/>
<vertex x="4.5222875" y="7.197146875"/>
<vertex x="3.68801875" y="7.658234375"/>
<vertex x="2.807390625" y="8.023003125"/>
<vertex x="1.89143125" y="8.2868875"/>
<vertex x="0.95170625" y="8.44655"/>
</polygon>
<wire x1="0" y1="8.5" x2="0" y2="-8.5" width="0.127" layer="21" curve="180"/>
<wire x1="-6.985" y1="5.715" x2="-6.985" y2="6.985" width="0.254" layer="21"/>
<wire x1="-6.985" y1="6.985" x2="-6.985" y2="8.255" width="0.254" layer="21"/>
<wire x1="-6.985" y1="6.985" x2="-8.255" y2="6.985" width="0.254" layer="21"/>
<wire x1="-6.985" y1="6.985" x2="-5.715" y2="6.985" width="0.254" layer="21"/>
<text x="-5.715" y="-6.985" size="0.635" layer="21" rot="R180">&gt;NAME</text>
</package>
<package name="100ZLJ82M10X16" library_version="225">
<pad name="+" x="0" y="2.5" drill="0.8"/>
<pad name="-" x="0" y="-2.5" drill="0.8"/>
<circle x="0" y="0" radius="5.1" width="0.254" layer="39"/>
<circle x="0" y="0" radius="5.2" width="0.254" layer="21"/>
<polygon width="0.1524" layer="21" pour="solid">
<vertex x="-0.603121875" y="-4.96718125"/>
<vertex x="0" y="-5.003659375"/>
<vertex x="0.603121875" y="-4.96718125"/>
<vertex x="1.197459375" y="-4.8582625"/>
<vertex x="1.7743375" y="-4.678496875"/>
<vertex x="2.325321875" y="-4.43051875"/>
<vertex x="2.84241875" y="-4.117921875"/>
<vertex x="3.31804375" y="-3.745290625"/>
<vertex x="3.745290625" y="-3.31804375"/>
<vertex x="4.117921875" y="-2.84241875"/>
<vertex x="4.43051875" y="-2.325321875"/>
<vertex x="4.678496875" y="-1.7743375"/>
<vertex x="4.8582625" y="-1.197459375"/>
<vertex x="4.96718125" y="-0.603121875"/>
<vertex x="4.99905" y="-0.0762"/>
<vertex x="-4.99905" y="-0.0762"/>
<vertex x="-4.96718125" y="-0.603121875"/>
<vertex x="-4.8582625" y="-1.197459375"/>
<vertex x="-4.678496875" y="-1.7743375"/>
<vertex x="-4.43051875" y="-2.325321875"/>
<vertex x="-4.117921875" y="-2.84241875"/>
<vertex x="-3.745290625" y="-3.31804375"/>
<vertex x="-3.31804375" y="-3.745290625"/>
<vertex x="-2.84241875" y="-4.117921875"/>
<vertex x="-2.325321875" y="-4.43051875"/>
<vertex x="-1.7743375" y="-4.678496875"/>
<vertex x="-1.197459375" y="-4.8582625"/>
</polygon>
<wire x1="0" y1="4.826" x2="0" y2="4.064" width="0.254" layer="21"/>
<wire x1="0" y1="4.064" x2="0" y2="3.302" width="0.254" layer="21"/>
<wire x1="0" y1="4.064" x2="-0.762" y2="4.064" width="0.254" layer="21"/>
<wire x1="0.762" y1="4.064" x2="0" y2="4.064" width="0.254" layer="21"/>
<text x="3.048" y="4.826" size="0.635" layer="21" font="vector" rot="R315">&gt;NAME</text>
</package>
<package name="100ZLJ68MT78X20" library_version="225">
<pad name="+" x="-1.75" y="0" drill="0.8"/>
<pad name="-" x="1.75" y="0" drill="0.8"/>
<circle x="0" y="0" radius="4" width="0.127" layer="39"/>
<circle x="0" y="0" radius="4.25" width="0.127" layer="21"/>
<polygon width="0.1524" layer="21" pour="solid">
<vertex x="0.0762" y="4.168640625"/>
<vertex x="0.0762" y="-4.168640625"/>
<vertex x="0.544775" y="-4.13793125"/>
<vertex x="1.08021875" y="-4.031421875"/>
<vertex x="1.59718125" y="-3.8559375"/>
<vertex x="2.086825" y="-3.614471875"/>
<vertex x="2.54074375" y="-3.311175"/>
<vertex x="2.95120625" y="-2.95120625"/>
<vertex x="3.311175" y="-2.54074375"/>
<vertex x="3.614471875" y="-2.086825"/>
<vertex x="3.8559375" y="-1.59718125"/>
<vertex x="4.031421875" y="-1.08021875"/>
<vertex x="4.13793125" y="-0.544775"/>
<vertex x="4.173634375" y="0"/>
<vertex x="4.13793125" y="0.544775"/>
<vertex x="4.031421875" y="1.08021875"/>
<vertex x="3.8559375" y="1.59718125"/>
<vertex x="3.614471875" y="2.086825"/>
<vertex x="3.311175" y="2.54074375"/>
<vertex x="2.95120625" y="2.95120625"/>
<vertex x="2.54074375" y="3.311175"/>
<vertex x="2.086825" y="3.614471875"/>
<vertex x="1.59718125" y="3.8559375"/>
<vertex x="1.08021875" y="4.031421875"/>
<vertex x="0.544775" y="4.13793125"/>
</polygon>
<wire x1="-3.25" y1="0.5" x2="-3.25" y2="-0.5" width="0.127" layer="21"/>
<wire x1="-2.75" y1="0" x2="-3.75" y2="0" width="0.127" layer="21"/>
<text x="-0.5" y="0" size="0.635" layer="21" rot="R90" align="center">&gt;NAME</text>
</package>
<package name="RUBYCON_CAP-POL-5X10">
<pad name="+" x="0" y="2.5" drill="0.8"/>
<pad name="-" x="0" y="-2.5" drill="0.8"/>
<circle x="0" y="0" radius="5" width="0.1524" layer="39"/>
<circle x="0" y="0" radius="5.25" width="0.1524" layer="21"/>
<polygon width="0.1524" layer="21" pour="solid">
<vertex x="-0.623615625" y="-5.135940625"/>
<vertex x="0" y="-5.173659375"/>
<vertex x="0.623615625" y="-5.135940625"/>
<vertex x="1.238140625" y="-5.023321875"/>
<vertex x="1.83461875" y="-4.83745"/>
<vertex x="2.4043125" y="-4.581053125"/>
<vertex x="2.938990625" y="-4.257828125"/>
<vertex x="3.430775" y="-3.8725375"/>
<vertex x="3.8725375" y="-3.430775"/>
<vertex x="4.257828125" y="-2.938990625"/>
<vertex x="4.581053125" y="-2.4043125"/>
<vertex x="4.83745" y="-1.83461875"/>
<vertex x="5.023321875" y="-1.238140625"/>
<vertex x="5.135940625" y="-0.623615625"/>
<vertex x="5.16905" y="-0.0762"/>
<vertex x="-5.16905" y="-0.0762"/>
<vertex x="-5.135940625" y="-0.623615625"/>
<vertex x="-5.023321875" y="-1.238140625"/>
<vertex x="-4.83745" y="-1.83461875"/>
<vertex x="-4.581053125" y="-2.4043125"/>
<vertex x="-4.257828125" y="-2.938990625"/>
<vertex x="-3.8725375" y="-3.430775"/>
<vertex x="-3.430775" y="-3.8725375"/>
<vertex x="-2.938990625" y="-4.257828125"/>
<vertex x="-2.4043125" y="-4.581053125"/>
<vertex x="-1.83461875" y="-4.83745"/>
<vertex x="-1.238140625" y="-5.023321875"/>
</polygon>
<wire x1="0" y1="5" x2="0" y2="3.5" width="0.1524" layer="21"/>
<wire x1="-0.75" y1="4.25" x2="0.75" y2="4.25" width="0.1524" layer="21"/>
<text x="-4.5" y="4.5" size="1.27" layer="21" rot="R45" align="center">&gt;NAME</text>
</package>
<package name="RUBYCON_CAP-POL-3.5X8" library_version="229">
<pad name="+" x="0" y="1.75" drill="0.9"/>
<pad name="-" x="0" y="-1.75" drill="0.9"/>
<circle x="0" y="0" radius="4" width="0.127" layer="39"/>
<circle x="0" y="0" radius="4.25" width="0.127" layer="21"/>
<polygon width="0.1524" layer="21" pour="solid">
<vertex x="-0.544775" y="-4.13793125"/>
<vertex x="0" y="-4.173634375"/>
<vertex x="0.544775" y="-4.13793125"/>
<vertex x="1.08021875" y="-4.031421875"/>
<vertex x="1.59718125" y="-3.8559375"/>
<vertex x="2.086825" y="-3.614471875"/>
<vertex x="2.54074375" y="-3.311175"/>
<vertex x="2.95120625" y="-2.95120625"/>
<vertex x="3.311175" y="-2.54074375"/>
<vertex x="3.614471875" y="-2.086825"/>
<vertex x="3.8559375" y="-1.59718125"/>
<vertex x="4.031421875" y="-1.08021875"/>
<vertex x="4.13793125" y="-0.544775"/>
<vertex x="4.168640625" y="-0.0762"/>
<vertex x="-4.168640625" y="-0.0762"/>
<vertex x="-4.13793125" y="-0.544775"/>
<vertex x="-4.031421875" y="-1.08021875"/>
<vertex x="-3.8559375" y="-1.59718125"/>
<vertex x="-3.614471875" y="-2.086825"/>
<vertex x="-3.311175" y="-2.54074375"/>
<vertex x="-2.95120625" y="-2.95120625"/>
<vertex x="-2.54074375" y="-3.311175"/>
<vertex x="-2.086825" y="-3.614471875"/>
<vertex x="-1.59718125" y="-3.8559375"/>
<vertex x="-1.08021875" y="-4.031421875"/>
</polygon>
<wire x1="0" y1="4" x2="0" y2="3" width="0.127" layer="21"/>
<wire x1="-0.5" y1="3.5" x2="0.5" y2="3.5" width="0.127" layer="21"/>
<text x="-3.75" y="3.75" size="0.889" layer="21" rot="R45" align="center">&gt;NAME</text>
</package>
<package name="ASPI-4030S-4R7M-T" library_version="230">
<smd name="P$1" x="-1.5" y="0" dx="1.1" dy="3.4" layer="1"/>
<smd name="P$2" x="1.5" y="0" dx="1.1" dy="3.4" layer="1"/>
<wire x1="-2" y1="2" x2="2" y2="2" width="0.1524" layer="39"/>
<wire x1="2" y1="2" x2="2" y2="-2" width="0.1524" layer="39"/>
<wire x1="2" y1="-2" x2="-2" y2="-2" width="0.1524" layer="39"/>
<wire x1="-2" y1="-2" x2="-2" y2="2" width="0.1524" layer="39"/>
</package>
<package name="TH_CAP-7.5" library_version="232">
<pad name="P$1" x="0" y="3.75" drill="0.85"/>
<pad name="P$2" x="0" y="-3.75" drill="0.85"/>
<text x="0" y="0" size="1.27" layer="25" rot="R90" align="center">&gt;NAME</text>
<wire x1="-1" y1="4.5" x2="-1" y2="-4.5" width="0.1524" layer="39"/>
<wire x1="-1" y1="-4.5" x2="1" y2="-4.5" width="0.1524" layer="39"/>
<wire x1="1" y1="-4.5" x2="1" y2="4.5" width="0.1524" layer="39"/>
<wire x1="1" y1="4.5" x2="-1" y2="4.5" width="0.1524" layer="39"/>
</package>
<package name="7447720122" library_version="234">
<pad name="P$1" x="-2.5" y="0" drill="1.2"/>
<pad name="P$2" x="2.5" y="0" drill="1.2"/>
<circle x="0" y="0" radius="4" width="0.1524" layer="39"/>
<text x="0" y="5.25" size="1.778" layer="25" align="center">&gt;NAME</text>
</package>
<package name="RUBYCON_CAP-POL-7.5X16" library_version="251">
<pad name="+" x="0" y="3.75" drill="1"/>
<pad name="-" x="0" y="-3.75" drill="1"/>
<circle x="0" y="0" radius="8" width="0.127" layer="39"/>
<circle x="0" y="0" radius="8.25" width="0.127" layer="21"/>
<polygon width="0.1524" layer="21" pour="solid">
<vertex x="-0.915175" y="-8.12228125"/>
<vertex x="0" y="-8.173678125"/>
<vertex x="0.915175" y="-8.12228125"/>
<vertex x="1.818825" y="-7.968746875"/>
<vertex x="2.699603125" y="-7.714996875"/>
<vertex x="3.54643125" y="-7.36423125"/>
<vertex x="4.34866875" y="-6.920846875"/>
<vertex x="5.096196875" y="-6.390446875"/>
<vertex x="5.7796625" y="-5.7796625"/>
<vertex x="6.390446875" y="-5.096196875"/>
<vertex x="6.920846875" y="-4.34866875"/>
<vertex x="7.36423125" y="-3.54643125"/>
<vertex x="7.714996875" y="-2.699603125"/>
<vertex x="7.968746875" y="-1.818825"/>
<vertex x="8.12228125" y="-0.915175"/>
<vertex x="8.1694" y="-0.0762"/>
<vertex x="-8.1694" y="-0.0762"/>
<vertex x="-8.12228125" y="-0.915175"/>
<vertex x="-7.968746875" y="-1.818825"/>
<vertex x="-7.714996875" y="-2.699603125"/>
<vertex x="-7.36423125" y="-3.54643125"/>
<vertex x="-6.920846875" y="-4.34866875"/>
<vertex x="-6.390446875" y="-5.096196875"/>
<vertex x="-5.7796625" y="-5.7796625"/>
<vertex x="-5.096196875" y="-6.390446875"/>
<vertex x="-4.34866875" y="-6.920846875"/>
<vertex x="-3.54643125" y="-7.36423125"/>
<vertex x="-2.699603125" y="-7.714996875"/>
<vertex x="-1.818825" y="-7.968746875"/>
</polygon>
<wire x1="0" y1="7.25" x2="0" y2="5.75" width="0.127" layer="21"/>
<wire x1="0.75" y1="6.5" x2="-0.75" y2="6.5" width="0.127" layer="21"/>
<text x="-7" y="7" size="1.27" layer="25" rot="R45" align="center">&gt;NAME</text>
</package>
<package name="UCC27517DBVR" library_version="255">
<smd name="P$1" x="-1.3" y="0.95" dx="1.1" dy="0.6" layer="1" roundness="5"/>
<smd name="P$2" x="-1.3" y="0" dx="1.1" dy="0.6" layer="1" roundness="5"/>
<smd name="P$3" x="-1.3" y="-0.95" dx="1.1" dy="0.6" layer="1" roundness="5"/>
<smd name="P$4" x="1.3" y="-0.95" dx="1.1" dy="0.6" layer="1" roundness="5"/>
<smd name="P$5" x="1.3" y="0.95" dx="1.1" dy="0.6" layer="1" roundness="5"/>
<wire x1="-1.25" y1="1.75" x2="-1.25" y2="-1.75" width="0.1524" layer="39"/>
<wire x1="-1.25" y1="-1.75" x2="1.25" y2="-1.75" width="0.1524" layer="39"/>
<wire x1="1.25" y1="-1.75" x2="1.25" y2="1.75" width="0.1524" layer="39"/>
<wire x1="1.25" y1="1.75" x2="-1.25" y2="1.75" width="0.1524" layer="39"/>
<text x="0" y="2.25" size="0.635" layer="25" align="center">&gt;NAME</text>
</package>
<package name="B1701NG--20D000314U1930" library_version="258">
<smd name="P$1" x="0" y="0.92" dx="1.1" dy="0.9" layer="1" roundness="5"/>
<smd name="P$2" x="0" y="-0.95" dx="1.1" dy="0.9" layer="1" roundness="5"/>
<rectangle x1="-0.508" y1="0" x2="0.508" y2="0.381" layer="21"/>
<rectangle x1="-0.762" y1="0" x2="-0.508" y2="0.381" layer="21"/>
<rectangle x1="0.508" y1="0" x2="0.762" y2="0.381" layer="21"/>
<wire x1="-0.762" y1="1.016" x2="0.762" y2="1.016" width="0.127" layer="39"/>
<wire x1="0.762" y1="1.016" x2="0.762" y2="-1.143" width="0.127" layer="39"/>
<wire x1="0.762" y1="-1.143" x2="-0.762" y2="-1.143" width="0.127" layer="39"/>
<wire x1="-0.762" y1="-1.143" x2="-0.762" y2="1.016" width="0.127" layer="39"/>
<text x="0" y="1.778" size="0.508" layer="21" rot="R180" align="center">&gt;NAME</text>
</package>
<package name="BSC190N12NS3GATMA1" library_version="260">
<smd name="P$5" x="-2.4892" y="1.9304" dx="1.2192" dy="0.7112" layer="1" roundness="10"/>
<smd name="P$6" x="-2.4892" y="0.6096" dx="1.2192" dy="0.7112" layer="1" roundness="10"/>
<smd name="P$7" x="-2.4892" y="-0.7112" dx="1.2192" dy="0.7112" layer="1" roundness="10"/>
<smd name="P$8" x="-2.4892" y="-2.032" dx="1.2192" dy="0.7112" layer="1" roundness="10"/>
<smd name="P$1" x="3.1496" y="-2.032" dx="1.2192" dy="0.7112" layer="1" roundness="10"/>
<smd name="P$2" x="3.1496" y="-0.7112" dx="1.2192" dy="0.7112" layer="1" roundness="10"/>
<smd name="P$3" x="3.1496" y="0.6096" dx="1.2192" dy="0.7112" layer="1" roundness="10"/>
<smd name="P$4" x="3.1496" y="1.9304" dx="1.2192" dy="0.7112" layer="1" roundness="10"/>
<polygon width="0.1524" layer="1" pour="solid">
<vertex x="-2.54" y="-2.3368"/>
<vertex x="1.7526" y="-2.3368"/>
<vertex x="1.7526" y="2.2352"/>
<vertex x="-2.54" y="2.2352"/>
</polygon>
<wire x1="-2.921" y1="2.794" x2="-2.921" y2="-2.921" width="0.1524" layer="39"/>
<wire x1="-2.921" y1="-2.921" x2="3.556" y2="-2.921" width="0.1524" layer="39"/>
<wire x1="3.556" y1="-2.921" x2="3.556" y2="2.794" width="0.1524" layer="39"/>
<wire x1="3.556" y1="2.794" x2="-2.921" y2="2.794" width="0.1524" layer="39"/>
<text x="0" y="3.81" size="1.27" layer="25" font="vector" align="center">&gt;NAME</text>
<rectangle x1="-2.6162" y1="-2.413" x2="1.8288" y2="2.3114" layer="29"/>
</package>
<package name="630A" library_version="260">
<smd name="G" x="-2.3" y="-6.9" dx="1.5" dy="2.5" layer="1"/>
<smd name="S" x="2.3" y="-6.9" dx="1.5" dy="2.5" layer="1"/>
<smd name="D" x="0" y="0" dx="7" dy="7" layer="1"/>
<wire x1="-4" y1="3" x2="-4" y2="-5" width="0.1524" layer="39"/>
<wire x1="-4" y1="-5" x2="4" y2="-5" width="0.1524" layer="39"/>
<wire x1="4" y1="-5" x2="4" y2="3" width="0.1524" layer="39"/>
<wire x1="4" y1="3" x2="-4" y2="3" width="0.1524" layer="39"/>
<text x="0" y="5" size="1.778" layer="25" align="center">&gt;NAME</text>
</package>
<package name="FET_TO220-SMTH" library_version="260">
<pad name="G" x="-2.54" y="0" drill="1" shape="long" rot="R90"/>
<pad name="D" x="0" y="0" drill="1" shape="long" rot="R90"/>
<pad name="S" x="2.54" y="0" drill="1" shape="long" rot="R90"/>
<wire x1="5" y1="2" x2="5" y2="11" width="0.1524" layer="21"/>
<wire x1="5" y1="11" x2="5" y2="18" width="0.1524" layer="21"/>
<wire x1="5" y1="18" x2="-5" y2="18" width="0.1524" layer="21"/>
<wire x1="-5" y1="18" x2="-5" y2="11" width="0.1524" layer="21"/>
<wire x1="-5" y1="11" x2="-5" y2="2" width="0.1524" layer="21"/>
<wire x1="-5" y1="2" x2="5" y2="2" width="0.1524" layer="21"/>
<wire x1="5" y1="11" x2="-5" y2="11" width="0.1524" layer="21"/>
<hole x="0" y="15" drill="3.4"/>
<text x="0" y="19" size="1" layer="25" align="center">&gt;NAME</text>
<wire x1="-5.25" y1="18.25" x2="-5.25" y2="-1.75" width="0.1524" layer="39"/>
<wire x1="-5.25" y1="-1.75" x2="5.25" y2="-1.75" width="0.1524" layer="39"/>
<wire x1="5.25" y1="-1.75" x2="5.25" y2="18.25" width="0.1524" layer="39"/>
<wire x1="5.25" y1="18.25" x2="-5.25" y2="18.25" width="0.1524" layer="39"/>
</package>
<package name="FET_TO220-VTH" library_version="260">
<pad name="G" x="-2.54" y="0" drill="1" shape="long" rot="R90"/>
<pad name="D" x="0" y="0" drill="1" shape="long" rot="R90"/>
<pad name="S" x="2.54" y="0" drill="1" shape="long" rot="R90"/>
<text x="0" y="2.5" size="1" layer="25" align="center">&gt;NAME</text>
<wire x1="-5.25" y1="1.75" x2="-5.25" y2="-1.75" width="0.1524" layer="39"/>
<wire x1="-5.25" y1="-1.75" x2="5.25" y2="-1.75" width="0.1524" layer="39"/>
<wire x1="5.25" y1="-1.75" x2="5.25" y2="1.75" width="0.1524" layer="39"/>
<wire x1="5.25" y1="1.75" x2="-5.25" y2="1.75" width="0.1524" layer="39"/>
</package>
<package name="BOURNS_RES-2512">
<smd name="P$1" x="-2.75" y="0" dx="1.5" dy="3.5" layer="1" rot="R180"/>
<smd name="P$2" x="2.75" y="0" dx="1.5" dy="3.5" layer="1" rot="R180"/>
<wire x1="-3.25" y1="1.75" x2="-3.25" y2="-1.75" width="0.1524" layer="39"/>
<wire x1="-3.25" y1="-1.75" x2="3.25" y2="-1.75" width="0.1524" layer="39"/>
<wire x1="3.25" y1="-1.75" x2="3.25" y2="1.75" width="0.1524" layer="39"/>
<wire x1="3.25" y1="1.75" x2="-3.25" y2="1.75" width="0.1524" layer="39"/>
<text x="-4" y="0" size="0.635" layer="25" rot="R90" align="center">&gt;NAME</text>
</package>
<package name="MCAC60N10YA-TP">
<smd name="S$1" x="-1.905" y="-2.745" dx="0.51" dy="0.76" layer="1"/>
<smd name="S$2" x="-0.635" y="-2.745" dx="0.51" dy="0.76" layer="1"/>
<smd name="S$3" x="0.635" y="-2.745" dx="0.51" dy="0.76" layer="1"/>
<smd name="G$1" x="1.905" y="-2.745" dx="0.51" dy="0.76" layer="1"/>
<smd name="D$4" x="-1.905" y="2.745" dx="0.51" dy="0.76" layer="1"/>
<smd name="D$3" x="-0.635" y="2.745" dx="0.51" dy="0.76" layer="1"/>
<smd name="D$2" x="0.635" y="2.745" dx="0.51" dy="0.76" layer="1"/>
<smd name="D$1" x="1.905" y="2.745" dx="0.51" dy="0.76" layer="1"/>
<polygon width="0.1524" layer="1" pour="solid">
<vertex x="-2.1738" y="-1.1738"/>
<vertex x="2.1738" y="-1.1738"/>
<vertex x="2.1738" y="2.5488"/>
<vertex x="-2.1738" y="2.5488"/>
</polygon>
<wire x1="-2.625" y1="-3.25" x2="2.625" y2="-3.25" width="0.1524" layer="39"/>
<wire x1="2.625" y1="-3.25" x2="2.625" y2="3.25" width="0.1524" layer="39"/>
<wire x1="2.625" y1="3.25" x2="-2.625" y2="3.25" width="0.1524" layer="39"/>
<wire x1="-2.625" y1="3.25" x2="-2.625" y2="-3.25" width="0.1524" layer="39"/>
<text x="0" y="3.75" size="0.635" layer="25" align="center">&gt;NAME</text>
<polygon width="0.1524" layer="29" pour="solid">
<vertex x="-2.1738" y="-1.1738"/>
<vertex x="2.1738" y="-1.1738"/>
<vertex x="2.1738" y="2.5488"/>
<vertex x="-2.1738" y="2.5488"/>
</polygon>
<rectangle x1="-2.125" y1="-1.125" x2="-1.375" y2="-0.375" layer="31"/>
<rectangle x1="1.375" y1="-1.125" x2="2.125" y2="-0.375" layer="31"/>
<rectangle x1="-1.25" y1="-1.125" x2="-0.5" y2="-0.375" layer="31"/>
<rectangle x1="0.5" y1="-1.125" x2="1.25" y2="-0.375" layer="31"/>
<rectangle x1="-0.375" y1="-1.125" x2="0.375" y2="-0.375" layer="31"/>
<rectangle x1="-2.125" y1="-0.25" x2="-1.375" y2="0.5" layer="31"/>
<rectangle x1="-1.25" y1="-0.25" x2="-0.5" y2="0.5" layer="31"/>
<rectangle x1="-0.375" y1="-0.25" x2="0.375" y2="0.5" layer="31"/>
<rectangle x1="0.5" y1="-0.25" x2="1.25" y2="0.5" layer="31"/>
<rectangle x1="1.375" y1="-0.25" x2="2.125" y2="0.5" layer="31"/>
<rectangle x1="-2.125" y1="0.625" x2="-1.375" y2="1.375" layer="31"/>
<rectangle x1="-1.25" y1="0.625" x2="-0.5" y2="1.375" layer="31"/>
<rectangle x1="-0.375" y1="0.625" x2="0.375" y2="1.375" layer="31"/>
<rectangle x1="0.5" y1="0.625" x2="1.25" y2="1.375" layer="31"/>
<rectangle x1="1.375" y1="0.625" x2="2.125" y2="1.375" layer="31"/>
<rectangle x1="-2.125" y1="1.5" x2="-1.375" y2="2.25" layer="31"/>
<rectangle x1="-1.25" y1="1.5" x2="-0.5" y2="2.25" layer="31"/>
<rectangle x1="-0.375" y1="1.5" x2="0.375" y2="2.25" layer="31"/>
<rectangle x1="0.5" y1="1.5" x2="1.25" y2="2.25" layer="31"/>
<rectangle x1="1.375" y1="1.5" x2="2.125" y2="2.25" layer="31"/>
</package>
<package name="MAX31850" library_version="267">
<smd name="P$1" x="-1.92" y="1" dx="0.79" dy="0.3" layer="1"/>
<smd name="P$2" x="-1.92" y="0.5" dx="0.79" dy="0.3" layer="1"/>
<smd name="P$3" x="-1.92" y="0" dx="0.79" dy="0.3" layer="1"/>
<smd name="P$4" x="-1.92" y="-0.5" dx="0.79" dy="0.3" layer="1"/>
<smd name="P$5" x="-1.92" y="-1" dx="0.79" dy="0.3" layer="1"/>
<smd name="P$6" x="1.92" y="-1" dx="0.79" dy="0.3" layer="1"/>
<smd name="P$7" x="1.92" y="-0.5" dx="0.79" dy="0.3" layer="1"/>
<smd name="P$8" x="1.92" y="0" dx="0.79" dy="0.3" layer="1"/>
<smd name="P$9" x="1.92" y="0.5" dx="0.79" dy="0.3" layer="1"/>
<smd name="P$10" x="1.92" y="1" dx="0.79" dy="0.3" layer="1"/>
<smd name="EP" x="0" y="0" dx="2.6" dy="2.3" layer="1"/>
<text x="0" y="2.5" size="0.635" layer="25" align="center">&gt;NAME</text>
<wire x1="2.25" y1="1.5" x2="-2.25" y2="1.5" width="0.1524" layer="39"/>
<wire x1="-2.25" y1="1.5" x2="-2.25" y2="-1.5" width="0.1524" layer="39"/>
<wire x1="-2.25" y1="-1.5" x2="2.25" y2="-1.5" width="0.1524" layer="39"/>
<wire x1="2.25" y1="-1.5" x2="2.25" y2="1.5" width="0.1524" layer="39"/>
<circle x="-2.5" y="1.75" radius="0.125" width="0.508" layer="21"/>
</package>
<package name="MIC5365-3.3YC5-TR">
<smd name="P$1" x="0.65" y="0.975" dx="0.45" dy="0.95" layer="1"/>
<smd name="P$2" x="0" y="0.975" dx="0.45" dy="0.95" layer="1"/>
<smd name="P$3" x="-0.65" y="0.975" dx="0.45" dy="0.95" layer="1"/>
<smd name="P$4" x="-0.65" y="-0.975" dx="0.45" dy="0.95" layer="1"/>
<smd name="P$5" x="0.65" y="-0.975" dx="0.45" dy="0.95" layer="1"/>
<wire x1="-1.375" y1="0.875" x2="-1.375" y2="-0.875" width="0.127" layer="39"/>
<wire x1="-1.375" y1="-0.875" x2="1.375" y2="-0.875" width="0.127" layer="39"/>
<wire x1="1.375" y1="-0.875" x2="1.375" y2="0.875" width="0.127" layer="39"/>
<wire x1="1.375" y1="0.875" x2="-1.375" y2="0.875" width="0.127" layer="39"/>
<text x="-1.875" y="0" size="0.635" layer="25" rot="R90" align="center">&gt;NAME</text>
</package>
</packages>
<symbols>
<symbol name="CAP-NON-POL">
<pin name="P$1" x="-7.62" y="0" visible="off" length="point"/>
<pin name="P$2" x="7.62" y="0" visible="off" length="point"/>
<wire x1="-0.635" y1="2.54" x2="-0.635" y2="0" width="0.254" layer="94"/>
<wire x1="-0.635" y1="0" x2="-0.635" y2="-2.54" width="0.254" layer="94"/>
<wire x1="0.635" y1="2.54" x2="0.635" y2="0" width="0.254" layer="94"/>
<wire x1="0.635" y1="0" x2="0.635" y2="-2.54" width="0.254" layer="94"/>
<wire x1="0.635" y1="0" x2="7.62" y2="0" width="0.254" layer="94"/>
<wire x1="-0.635" y1="0" x2="-7.62" y2="0" width="0.254" layer="94"/>
<text x="0" y="-3.81" size="1.778" layer="96" align="center">&gt;VALUE</text>
<text x="0" y="3.81" size="1.778" layer="95" align="center">&gt;NAME</text>
</symbol>
<symbol name="RES-CHIP">
<pin name="P$1" x="-7.62" y="0" visible="off" length="point"/>
<pin name="P$2" x="7.62" y="0" visible="off" length="point"/>
<wire x1="-7.62" y1="0" x2="-5.08" y2="0" width="0.254" layer="94"/>
<wire x1="7.62" y1="0" x2="5.08" y2="0" width="0.254" layer="94"/>
<text x="0" y="2.54" size="1.778" layer="95" align="center">&gt;NAME</text>
<text x="0" y="-2.54" size="1.778" layer="96" align="center">&gt;VALUE</text>
<wire x1="-5.08" y1="0" x2="-5.08" y2="1.27" width="0.254" layer="94"/>
<wire x1="-5.08" y1="1.27" x2="5.08" y2="1.27" width="0.254" layer="94"/>
<wire x1="5.08" y1="1.27" x2="5.08" y2="-1.27" width="0.254" layer="94"/>
<wire x1="5.08" y1="-1.27" x2="-5.08" y2="-1.27" width="0.254" layer="94"/>
<wire x1="-5.08" y1="-1.27" x2="-5.08" y2="0" width="0.254" layer="94"/>
</symbol>
<symbol name="INDUCTOR">
<pin name="P$1" x="-7.62" y="0" visible="off" length="point"/>
<pin name="P$2" x="7.62" y="0" visible="off" length="point"/>
<wire x1="-7.62" y1="0" x2="-5.08" y2="0" width="0.254" layer="94"/>
<wire x1="7.62" y1="0" x2="5.08" y2="0" width="0.254" layer="94"/>
<wire x1="-5.08" y1="0" x2="-2.54" y2="0" width="0.254" layer="94" curve="-180"/>
<wire x1="-2.54" y1="0" x2="0" y2="0" width="0.254" layer="94" curve="-180"/>
<wire x1="0" y1="0" x2="2.54" y2="0" width="0.254" layer="94" curve="-180"/>
<wire x1="2.54" y1="0" x2="5.08" y2="0" width="0.254" layer="94" curve="-180"/>
<text x="0" y="2.54" size="1.778" layer="95" align="center">&gt;NAME</text>
<text x="0" y="-1.27" size="1.778" layer="95" align="center">&gt;VALUE</text>
</symbol>
<symbol name="TPS564247DRLR">
<pin name="VIN" x="-10.16" y="5.08" visible="pin" length="short"/>
<pin name="SW" x="10.16" y="5.08" visible="pin" length="short" rot="R180"/>
<pin name="FB" x="10.16" y="0" visible="pin" length="short" rot="R180"/>
<pin name="AGND" x="10.16" y="-5.08" visible="pin" length="short" rot="R180"/>
<pin name="GND" x="10.16" y="-7.62" visible="pin" length="short" rot="R180"/>
<pin name="EN" x="-10.16" y="-7.62" visible="pin" length="short"/>
<wire x1="-7.62" y1="7.62" x2="7.62" y2="7.62" width="0.1524" layer="94"/>
<wire x1="7.62" y1="7.62" x2="7.62" y2="-10.16" width="0.1524" layer="94"/>
<wire x1="7.62" y1="-10.16" x2="-7.62" y2="-10.16" width="0.1524" layer="94"/>
<wire x1="-7.62" y1="-10.16" x2="-7.62" y2="7.62" width="0.1524" layer="94"/>
<text x="0" y="10.16" size="1.778" layer="95" align="center">&gt;NAME</text>
<text x="0" y="-12.7" size="1.778" layer="96" align="center">&gt;VALUE</text>
</symbol>
<symbol name="FUSE" library_version="222">
<wire x1="-5.08" y1="1.27" x2="-5.08" y2="-1.27" width="0.254" layer="94"/>
<wire x1="-5.08" y1="-1.27" x2="-3.81" y2="-1.27" width="0.254" layer="94"/>
<wire x1="-3.81" y1="-1.27" x2="3.81" y2="-1.27" width="0.254" layer="94"/>
<wire x1="3.81" y1="-1.27" x2="5.08" y2="-1.27" width="0.254" layer="94"/>
<wire x1="5.08" y1="-1.27" x2="5.08" y2="1.27" width="0.254" layer="94"/>
<wire x1="5.08" y1="1.27" x2="3.81" y2="1.27" width="0.254" layer="94"/>
<pin name="P$1" x="-7.62" y="0" visible="off" length="short"/>
<pin name="P$2" x="7.62" y="0" visible="off" length="short" rot="R180"/>
<text x="0" y="3.175" size="1.778" layer="95" align="center">&gt;NAME</text>
<text x="0" y="-3.175" size="1.778" layer="95" align="center">&gt;VALUE</text>
<wire x1="3.81" y1="1.27" x2="-3.81" y2="1.27" width="0.254" layer="94"/>
<wire x1="-3.81" y1="1.27" x2="-5.08" y2="1.27" width="0.254" layer="94"/>
<wire x1="-3.81" y1="1.27" x2="-3.81" y2="-1.27" width="0.254" layer="94"/>
<wire x1="3.81" y1="1.27" x2="3.81" y2="-1.27" width="0.254" layer="94"/>
</symbol>
<symbol name="CAP-POL" library_version="225">
<pin name="-" x="-7.62" y="0" visible="off" length="point"/>
<pin name="+" x="7.62" y="0" visible="off" length="point"/>
<wire x1="0.635" y1="2.54" x2="0.635" y2="0" width="0.254" layer="94"/>
<wire x1="0.635" y1="0" x2="0.635" y2="-2.54" width="0.254" layer="94"/>
<wire x1="0.635" y1="0" x2="7.62" y2="0" width="0.254" layer="94"/>
<wire x1="-0.635" y1="0" x2="-7.62" y2="0" width="0.254" layer="94"/>
<text x="0" y="-3.81" size="1.778" layer="96" align="center">&gt;VALUE</text>
<text x="0" y="3.81" size="1.778" layer="95" align="center">&gt;NAME</text>
<wire x1="-0.635" y1="0" x2="-1.27" y2="-2.54" width="0.254" layer="94" curve="-19.983107"/>
<wire x1="-0.635" y1="0" x2="-1.27" y2="2.54" width="0.254" layer="94" curve="28.072487"/>
</symbol>
<symbol name="SYM-GND" library_version="239">
<text x="0" y="-1.27" size="1.778" layer="95" align="top-center">GND</text>
<pin name="GND" x="0" y="2.54" visible="off" length="short" direction="sup" rot="R270"/>
<wire x1="-2.54" y1="0" x2="2.54" y2="0" width="0.254" layer="94"/>
</symbol>
<symbol name="SYM-12V0" library_version="251">
<pin name="12V0" x="0" y="0" visible="off" length="short" direction="sup" rot="R90"/>
<wire x1="0" y1="5.08" x2="-2.54" y2="2.54" width="0.254" layer="94"/>
<wire x1="2.54" y1="2.54" x2="0" y2="5.08" width="0.254" layer="94"/>
<wire x1="0" y1="5.08" x2="0" y2="2.54" width="0.254" layer="94"/>
<text x="0" y="6.35" size="1.778" layer="95" align="bottom-center">12V0</text>
</symbol>
<symbol name="SYM-4V0" library_version="251">
<pin name="4V0" x="0" y="0" visible="off" length="short" direction="sup" rot="R90"/>
<wire x1="0" y1="5.08" x2="-2.54" y2="2.54" width="0.254" layer="94"/>
<wire x1="2.54" y1="2.54" x2="0" y2="5.08" width="0.254" layer="94"/>
<wire x1="0" y1="5.08" x2="0" y2="2.54" width="0.254" layer="94"/>
<text x="0" y="6.35" size="1.778" layer="95" align="bottom-center">4V0</text>
</symbol>
<symbol name="SYM-3V3" library_version="251">
<pin name="3V3" x="0" y="0" visible="off" length="short" direction="sup" rot="R90"/>
<wire x1="0" y1="5.08" x2="-2.54" y2="2.54" width="0.254" layer="94"/>
<wire x1="2.54" y1="2.54" x2="0" y2="5.08" width="0.254" layer="94"/>
<wire x1="0" y1="5.08" x2="0" y2="2.54" width="0.254" layer="94"/>
<text x="0" y="6.35" size="1.778" layer="95" align="bottom-center">3V3</text>
</symbol>
<symbol name="UCC27517DBVR" library_version="255">
<pin name="VDD" x="-10.16" y="5.08" visible="pin" length="short"/>
<pin name="GND" x="-10.16" y="0" visible="pin" length="short"/>
<pin name="IN+" x="-10.16" y="-5.08" visible="pin" length="short"/>
<pin name="OUT" x="10.16" y="5.08" visible="pin" length="short" rot="R180"/>
<pin name="IN-" x="10.16" y="-5.08" visible="pin" length="short" rot="R180"/>
<wire x1="-7.62" y1="7.62" x2="7.62" y2="7.62" width="0.1524" layer="94"/>
<wire x1="7.62" y1="7.62" x2="7.62" y2="-7.62" width="0.1524" layer="94"/>
<wire x1="7.62" y1="-7.62" x2="-7.62" y2="-7.62" width="0.1524" layer="94"/>
<wire x1="-7.62" y1="-7.62" x2="-7.62" y2="7.62" width="0.1524" layer="94"/>
<text x="0" y="10.16" size="1.778" layer="95" align="center">&gt;NAME</text>
<text x="0" y="-10.16" size="1.778" layer="96" align="center">&gt;VALUE</text>
</symbol>
<symbol name="DIODE-LED" library_version="258">
<pin name="VDD" x="-7.62" y="0" visible="off" length="point"/>
<pin name="VSS" x="7.62" y="0" visible="off" length="point"/>
<wire x1="7.62" y1="0" x2="1.27" y2="0" width="0.254" layer="94"/>
<wire x1="1.27" y1="0" x2="-2.54" y2="2.54" width="0.254" layer="94"/>
<wire x1="-2.54" y1="2.54" x2="-2.54" y2="0" width="0.254" layer="94"/>
<wire x1="-2.54" y1="0" x2="-2.54" y2="-2.54" width="0.254" layer="94"/>
<wire x1="-2.54" y1="-2.54" x2="1.27" y2="0" width="0.254" layer="94"/>
<wire x1="-2.54" y1="0" x2="-7.62" y2="0" width="0.254" layer="94"/>
<wire x1="1.27" y1="0" x2="1.27" y2="2.54" width="0.254" layer="94"/>
<wire x1="1.27" y1="0" x2="1.27" y2="-2.54" width="0.254" layer="94"/>
<text x="0" y="6.35" size="1.778" layer="95" align="center">&gt;NAME</text>
<text x="0" y="-3.81" size="1.778" layer="95" align="center">&gt;VALUE</text>
<wire x1="-1.905" y1="3.175" x2="0" y2="5.08" width="0.254" layer="94"/>
<wire x1="0" y1="5.08" x2="-0.635" y2="5.08" width="0.254" layer="94"/>
<wire x1="0" y1="5.08" x2="0" y2="4.445" width="0.254" layer="94"/>
<wire x1="0" y1="3.175" x2="1.905" y2="5.08" width="0.254" layer="94"/>
<wire x1="1.905" y1="5.08" x2="1.27" y2="5.08" width="0.254" layer="94"/>
<wire x1="1.905" y1="5.08" x2="1.905" y2="4.445" width="0.254" layer="94"/>
</symbol>
<symbol name="FET-NCH" library_version="260">
<wire x1="-5.08" y1="7.62" x2="-5.08" y2="-7.62" width="0.1524" layer="94"/>
<wire x1="-5.08" y1="-7.62" x2="5.08" y2="-7.62" width="0.1524" layer="94"/>
<wire x1="5.08" y1="-7.62" x2="5.08" y2="7.62" width="0.1524" layer="94"/>
<wire x1="5.08" y1="7.62" x2="-5.08" y2="7.62" width="0.1524" layer="94"/>
<pin name="G" x="-7.62" y="0" visible="pin" length="short"/>
<pin name="D" x="2.54" y="10.16" visible="pin" length="short" rot="R270"/>
<pin name="S" x="2.54" y="-10.16" visible="pin" length="short" rot="R90"/>
<wire x1="-5.08" y1="0" x2="-0.635" y2="0" width="0.1524" layer="91"/>
<wire x1="-0.635" y1="0" x2="-0.635" y2="3.175" width="0.1524" layer="91"/>
<wire x1="-0.635" y1="0" x2="-0.635" y2="-3.175" width="0.1524" layer="91"/>
<wire x1="2.54" y1="-7.62" x2="2.54" y2="-3.175" width="0.1524" layer="91"/>
<wire x1="2.54" y1="-3.175" x2="2.54" y2="0" width="0.1524" layer="91"/>
<wire x1="2.54" y1="0" x2="0" y2="0" width="0.1524" layer="91"/>
<wire x1="0" y1="0" x2="0" y2="1.27" width="0.1524" layer="91"/>
<wire x1="0" y1="0" x2="0" y2="-1.27" width="0.1524" layer="91"/>
<wire x1="0" y1="-1.905" x2="0" y2="-3.175" width="0.1524" layer="91"/>
<wire x1="0" y1="-3.175" x2="0" y2="-4.445" width="0.1524" layer="91"/>
<wire x1="0" y1="-3.175" x2="2.54" y2="-3.175" width="0.1524" layer="91"/>
<wire x1="0" y1="1.905" x2="0" y2="3.175" width="0.1524" layer="91"/>
<wire x1="0" y1="3.175" x2="0" y2="4.445" width="0.1524" layer="91"/>
<wire x1="0" y1="3.175" x2="2.54" y2="3.175" width="0.1524" layer="91"/>
<wire x1="2.54" y1="3.175" x2="2.54" y2="7.62" width="0.1524" layer="91"/>
<polygon width="0.1524" layer="91" pour="solid">
<vertex x="0.170390625" y="0"/>
<vertex x="1.1938" y="-0.51170625"/>
<vertex x="1.1938" y="0.51170625"/>
</polygon>
<text x="6.35" y="0" size="1.778" layer="96" font="vector" rot="R90" align="center">&gt;VALUE</text>
<text x="8.89" y="0" size="1.778" layer="95" font="vector" rot="R90" align="center">&gt;NAME</text>
</symbol>
<symbol name="MAX31850" library_version="267">
<pin name="VDD" x="-10.16" y="7.62" visible="pin" length="short"/>
<pin name="GND" x="-10.16" y="5.08" visible="pin" length="short"/>
<pin name="DQ" x="-10.16" y="-5.08" visible="pin" length="short"/>
<pin name="T+" x="10.16" y="7.62" visible="pin" length="short" rot="R180"/>
<pin name="T-" x="10.16" y="5.08" visible="pin" length="short" rot="R180"/>
<pin name="A0" x="10.16" y="0" visible="pin" length="short" rot="R180"/>
<pin name="A1" x="10.16" y="-2.54" visible="pin" length="short" rot="R180"/>
<pin name="A2" x="10.16" y="-5.08" visible="pin" length="short" rot="R180"/>
<pin name="A3" x="10.16" y="-7.62" visible="pin" length="short" rot="R180"/>
<pin name="EP" x="-10.16" y="-7.62" visible="pin" length="short"/>
<wire x1="-7.62" y1="10.16" x2="-7.62" y2="-10.16" width="0.1524" layer="94"/>
<wire x1="-7.62" y1="-10.16" x2="7.62" y2="-10.16" width="0.1524" layer="94"/>
<wire x1="7.62" y1="-10.16" x2="7.62" y2="10.16" width="0.1524" layer="94"/>
<wire x1="7.62" y1="10.16" x2="-7.62" y2="10.16" width="0.1524" layer="94"/>
<text x="0" y="12.7" size="1.778" layer="95" align="center">&gt;NAME</text>
<text x="0" y="-12.7" size="1.778" layer="96" align="center">&gt;VALUE</text>
</symbol>
<symbol name="MIC5365-3.3YC5-TR" library_version="270">
<pin name="VDD" x="-10.16" y="5.08" visible="pin" length="short"/>
<pin name="EN" x="-10.16" y="-5.08" visible="pin" length="short"/>
<pin name="VOUT" x="10.16" y="5.08" visible="pin" length="short" rot="R180"/>
<pin name="VSS" x="10.16" y="-5.08" visible="pin" length="short" rot="R180"/>
<wire x1="-7.62" y1="7.62" x2="7.62" y2="7.62" width="0.254" layer="94"/>
<wire x1="7.62" y1="7.62" x2="7.62" y2="-7.62" width="0.254" layer="94"/>
<wire x1="7.62" y1="-7.62" x2="-7.62" y2="-7.62" width="0.254" layer="94"/>
<wire x1="-7.62" y1="-7.62" x2="-7.62" y2="7.62" width="0.254" layer="94"/>
<text x="0" y="8.89" size="1.778" layer="95" align="center">&gt;NAME</text>
<text x="0" y="-8.89" size="1.778" layer="96" align="center">&gt;VALUE</text>
</symbol>
</symbols>
<devicesets>
<deviceset name="CAP-NON-POL" prefix="C">
<gates>
<gate name="G$1" symbol="CAP-NON-POL" x="0" y="0"/>
</gates>
<devices>
<device name="_SAMSUNG-0402" package="SAMSUNG_CAP-0402">
<connects>
<connect gate="G$1" pin="P$1" pad="P$1"/>
<connect gate="G$1" pin="P$2" pad="P$2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="_SAMSUNG-0603" package="SAMSUNG_CAP-0603">
<connects>
<connect gate="G$1" pin="P$1" pad="P$1"/>
<connect gate="G$1" pin="P$2" pad="P$2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="_SAMSUNG-0805" package="SAMSUNG_CAP-0805">
<connects>
<connect gate="G$1" pin="P$1" pad="P$1"/>
<connect gate="G$1" pin="P$2" pad="P$2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="_SAMSUNG-1206" package="SAMSUNG_CAP-1206">
<connects>
<connect gate="G$1" pin="P$1" pad="P$1"/>
<connect gate="G$1" pin="P$2" pad="P$2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="_KYOCERA-2225" package="KYOCERA_CAP-2225">
<connects>
<connect gate="G$1" pin="P$1" pad="P$1"/>
<connect gate="G$1" pin="P$2" pad="P$2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="_WALSIN-1210" package="WALSIN_CAP-1210">
<connects>
<connect gate="G$1" pin="P$1" pad="P$1"/>
<connect gate="G$1" pin="P$2" pad="P$2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="_TDK-CGA_CAP-1210" package="TDK-CGA_CAP-1210">
<connects>
<connect gate="G$1" pin="P$1" pad="P$1"/>
<connect gate="G$1" pin="P$2" pad="P$2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="_TDK-CGA_CAP-0805" package="TDK-CGA_CAP-0805">
<connects>
<connect gate="G$1" pin="P$1" pad="P$1"/>
<connect gate="G$1" pin="P$2" pad="P$2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="_TC_CAP-7.5" package="TH_CAP-7.5">
<connects>
<connect gate="G$1" pin="P$1" pad="P$1"/>
<connect gate="G$1" pin="P$2" pad="P$2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
</devices>
</deviceset>
<deviceset name="RES-CHIP" prefix="R">
<gates>
<gate name="G$1" symbol="RES-CHIP" x="0" y="0"/>
</gates>
<devices>
<device name="_YAGEO-0805" package="YAGEO_RES-0805">
<connects>
<connect gate="G$1" pin="P$1" pad="P$1"/>
<connect gate="G$1" pin="P$2" pad="P$2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="_BOURNS-0612" package="BOURNS_RES-0612">
<connects>
<connect gate="G$1" pin="P$1" pad="P$1"/>
<connect gate="G$1" pin="P$2" pad="P$2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="_YAGEO-0603" package="YAGEO_RES-0603">
<connects>
<connect gate="G$1" pin="P$1" pad="P$1"/>
<connect gate="G$1" pin="P$2" pad="P$2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="_YAGEO-0402" package="YAGEO_RES-0402">
<connects>
<connect gate="G$1" pin="P$1" pad="P$1"/>
<connect gate="G$1" pin="P$2" pad="P$2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="_YAGEO-1206" package="YAGEO_RES-1206">
<connects>
<connect gate="G$1" pin="P$1" pad="P$1"/>
<connect gate="G$1" pin="P$2" pad="P$2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="_BOURNS-2512" package="BOURNS_RES-2512">
<connects>
<connect gate="G$1" pin="P$1" pad="P$1"/>
<connect gate="G$1" pin="P$2" pad="P$2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
</devices>
</deviceset>
<deviceset name="INDUCTOR" prefix="L" library_version="234">
<gates>
<gate name="G$1" symbol="INDUCTOR" x="0" y="0"/>
</gates>
<devices>
<device name="_ASPI-0530HI-2R2M-T2" package="ASPI-0530HI-2R2M-T2">
<connects>
<connect gate="G$1" pin="P$1" pad="P$1"/>
<connect gate="G$1" pin="P$2" pad="P$2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="_SRP1270-4R7M" package="SRP1270-4R7M">
<connects>
<connect gate="G$1" pin="P$1" pad="P$1"/>
<connect gate="G$1" pin="P$2" pad="P$2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="_ASPI-4030S-4R7M-T" package="ASPI-4030S-4R7M-T">
<connects>
<connect gate="G$1" pin="P$1" pad="P$1"/>
<connect gate="G$1" pin="P$2" pad="P$2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="_7447720122" package="7447720122">
<connects>
<connect gate="G$1" pin="P$1" pad="P$1"/>
<connect gate="G$1" pin="P$2" pad="P$2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
</devices>
</deviceset>
<deviceset name="TPS564247DRLR" prefix="U">
<gates>
<gate name="G$1" symbol="TPS564247DRLR" x="0" y="0"/>
</gates>
<devices>
<device name="" package="TPS564247DRLR">
<connects>
<connect gate="G$1" pin="AGND" pad="P$4"/>
<connect gate="G$1" pin="EN" pad="P$5"/>
<connect gate="G$1" pin="FB" pad="P$6"/>
<connect gate="G$1" pin="GND" pad="P$3"/>
<connect gate="G$1" pin="SW" pad="P$2"/>
<connect gate="G$1" pin="VIN" pad="P$1"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
</devices>
</deviceset>
<deviceset name="FUSE" library_version="222">
<gates>
<gate name="G$1" symbol="FUSE" x="0" y="0"/>
</gates>
<devices>
<device name="_FC-203-22-5X20MM" package="FC-203-22">
<connects>
<connect gate="G$1" pin="P$1" pad="P$1 P$2"/>
<connect gate="G$1" pin="P$2" pad="P$3 P$4"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
</devices>
</deviceset>
<deviceset name="CAP-POL" prefix="C" library_version="251">
<gates>
<gate name="G$1" symbol="CAP-POL" x="0" y="0"/>
</gates>
<devices>
<device name="_100YXJ330MGC16X25" package="100YXJ330MGC16X25">
<connects>
<connect gate="G$1" pin="+" pad="VCC"/>
<connect gate="G$1" pin="-" pad="VDD"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="_100ZLJ82M10X16" package="100ZLJ82M10X16">
<connects>
<connect gate="G$1" pin="+" pad="-"/>
<connect gate="G$1" pin="-" pad="+"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="_100ZLJ68MT78X20" package="100ZLJ68MT78X20">
<connects>
<connect gate="G$1" pin="+" pad="+"/>
<connect gate="G$1" pin="-" pad="-"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="_RUBYCON_CAP-POL-5X10" package="RUBYCON_CAP-POL-5X10">
<connects>
<connect gate="G$1" pin="+" pad="+"/>
<connect gate="G$1" pin="-" pad="-"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="_RUBYCON_CAP-POL-3.5X8" package="RUBYCON_CAP-POL-3.5X8">
<connects>
<connect gate="G$1" pin="+" pad="+"/>
<connect gate="G$1" pin="-" pad="-"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="_RUBYCON_CAP-POL-7.5X16" package="RUBYCON_CAP-POL-7.5X16">
<connects>
<connect gate="G$1" pin="+" pad="+"/>
<connect gate="G$1" pin="-" pad="-"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
</devices>
</deviceset>
<deviceset name="SYM-GND" library_version="239">
<gates>
<gate name="G$1" symbol="SYM-GND" x="0" y="-2.54"/>
</gates>
<devices>
<device name="">
<technologies>
<technology name=""/>
</technologies>
</device>
</devices>
</deviceset>
<deviceset name="SYM-12V0" library_version="251">
<gates>
<gate name="G$1" symbol="SYM-12V0" x="0" y="0"/>
</gates>
<devices>
<device name="">
<technologies>
<technology name=""/>
</technologies>
</device>
</devices>
</deviceset>
<deviceset name="SYM-4V0" library_version="251">
<gates>
<gate name="G$1" symbol="SYM-4V0" x="0" y="0"/>
</gates>
<devices>
<device name="">
<technologies>
<technology name=""/>
</technologies>
</device>
</devices>
</deviceset>
<deviceset name="SYM-3V3" library_version="251">
<gates>
<gate name="G$1" symbol="SYM-3V3" x="0" y="0"/>
</gates>
<devices>
<device name="">
<technologies>
<technology name=""/>
</technologies>
</device>
</devices>
</deviceset>
<deviceset name="UCC27517DBVR" prefix="U" library_version="255">
<gates>
<gate name="G$1" symbol="UCC27517DBVR" x="0" y="0"/>
</gates>
<devices>
<device name="" package="UCC27517DBVR">
<connects>
<connect gate="G$1" pin="GND" pad="P$2"/>
<connect gate="G$1" pin="IN+" pad="P$3"/>
<connect gate="G$1" pin="IN-" pad="P$4"/>
<connect gate="G$1" pin="OUT" pad="P$5"/>
<connect gate="G$1" pin="VDD" pad="P$1"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
</devices>
</deviceset>
<deviceset name="DIODE-LED" prefix="D" library_version="258">
<gates>
<gate name="G$1" symbol="DIODE-LED" x="0" y="0"/>
</gates>
<devices>
<device name="_B1701NG--20D000314U1930" package="B1701NG--20D000314U1930">
<connects>
<connect gate="G$1" pin="VDD" pad="P$2"/>
<connect gate="G$1" pin="VSS" pad="P$1"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
</devices>
</deviceset>
<deviceset name="FET-NCH" prefix="Q">
<gates>
<gate name="G$1" symbol="FET-NCH" x="0" y="0"/>
</gates>
<devices>
<device name="_BSC190N12NS3GATMA1" package="BSC190N12NS3GATMA1">
<connects>
<connect gate="G$1" pin="D" pad="P$5 P$6 P$7 P$8"/>
<connect gate="G$1" pin="G" pad="P$4"/>
<connect gate="G$1" pin="S" pad="P$1 P$2 P$3"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="_630A" package="630A">
<connects>
<connect gate="G$1" pin="D" pad="D"/>
<connect gate="G$1" pin="G" pad="G"/>
<connect gate="G$1" pin="S" pad="S"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="_FET_TO220-SMTH" package="FET_TO220-SMTH">
<connects>
<connect gate="G$1" pin="D" pad="D"/>
<connect gate="G$1" pin="G" pad="G"/>
<connect gate="G$1" pin="S" pad="S"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="_FET_TO220-VTH" package="FET_TO220-VTH">
<connects>
<connect gate="G$1" pin="D" pad="D"/>
<connect gate="G$1" pin="G" pad="G"/>
<connect gate="G$1" pin="S" pad="S"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="_MCAC60N10YA-TP" package="MCAC60N10YA-TP">
<connects>
<connect gate="G$1" pin="D" pad="D$1 D$2 D$3 D$4"/>
<connect gate="G$1" pin="G" pad="G$1"/>
<connect gate="G$1" pin="S" pad="S$1 S$2 S$3"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
</devices>
</deviceset>
<deviceset name="MAX31850" prefix="U" library_version="267">
<gates>
<gate name="G$1" symbol="MAX31850" x="0" y="0"/>
</gates>
<devices>
<device name="_MAX31850KATB+T" package="MAX31850">
<connects>
<connect gate="G$1" pin="A0" pad="P$6"/>
<connect gate="G$1" pin="A1" pad="P$7"/>
<connect gate="G$1" pin="A2" pad="P$8"/>
<connect gate="G$1" pin="A3" pad="P$9"/>
<connect gate="G$1" pin="DQ" pad="P$5"/>
<connect gate="G$1" pin="EP" pad="EP"/>
<connect gate="G$1" pin="GND" pad="P$1"/>
<connect gate="G$1" pin="T+" pad="P$3"/>
<connect gate="G$1" pin="T-" pad="P$2"/>
<connect gate="G$1" pin="VDD" pad="P$4"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
</devices>
</deviceset>
<deviceset name="MIC5365-3.3YC5-TR" prefix="VR">
<gates>
<gate name="G$1" symbol="MIC5365-3.3YC5-TR" x="0" y="0"/>
</gates>
<devices>
<device name="&quot;" package="MIC5365-3.3YC5-TR">
<connects>
<connect gate="G$1" pin="EN" pad="P$3"/>
<connect gate="G$1" pin="VDD" pad="P$1"/>
<connect gate="G$1" pin="VOUT" pad="P$5"/>
<connect gate="G$1" pin="VSS" pad="P$2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
</devices>
</deviceset>
</devicesets>
</library>
</libraries>
<attributes>
</attributes>
<variantdefs>
</variantdefs>
<classes>
<class number="0" name="default" width="0" drill="0">
</class>
</classes>
<parts>
<part name="PS1" library="VOSTOK_MISC_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2QirG-pvTuembVHon_9QUw" deviceset="LS05-13BXXR3" device=""/>
<part name="RP2040" library="VOSTOK_MISC_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2QirG-pvTuembVHon_9QUw" deviceset="SC0915" device="" value="SC0918"/>
<part name="C1" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="CAP-NON-POL" device="_SAMSUNG-0805" value="22u0 25V0"/>
<part name="C2" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="CAP-NON-POL" device="_SAMSUNG-0805" value="22u0 25V0"/>
<part name="C3" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="CAP-NON-POL" device="_SAMSUNG-0805" value="10u0 25V0"/>
<part name="C4" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="CAP-NON-POL" device="_SAMSUNG-0805" value="10u0 25V0"/>
<part name="R1" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="RES-CHIP" device="_YAGEO-0402" value="100K0"/>
<part name="R2" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="RES-CHIP" device="_YAGEO-0402" value="13K7"/>
<part name="C5" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="CAP-NON-POL" device="_SAMSUNG-0402" value="0u1 50V0 X7R"/>
<part name="C6" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="CAP-NON-POL" device="_SAMSUNG-0402" value="0u1 50V0 X7R"/>
<part name="L1" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="INDUCTOR" device="_ASPI-0530HI-2R2M-T2" value="ASPI-0530HI-2R2M-T2"/>
<part name="C9" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="CAP-NON-POL" device="_SAMSUNG-0402" value="33p0 50V0"/>
<part name="R3" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="RES-CHIP" device="_YAGEO-0402" value="169K0"/>
<part name="R4" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="RES-CHIP" device="_YAGEO-0402" value="30K0"/>
<part name="U1" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="TPS564247DRLR" device=""/>
<part name="C7" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="CAP-NON-POL" device="_SAMSUNG-0402" value="1n0 50V0 C0G/NP0"/>
<part name="C8" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="CAP-NON-POL" device="_SAMSUNG-0402" value="1n0 50V0 C0G/NP0"/>
<part name="F1" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="FUSE" device="_FC-203-22-5X20MM" value="5X20MM 1A/300V SLOW"/>
<part name="R17" library="VOSTOK_MISC_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2QirG-pvTuembVHon_9QUw" deviceset="SMW312RJT" device=""/>
<part name="C10" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="CAP-POL" device="_RUBYCON_CAP-POL-5X10" value="10u0 450V0"/>
<part name="C11" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="CAP-POL" device="_RUBYCON_CAP-POL-3.5X8" value="270u0 16V0"/>
<part name="L2" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="INDUCTOR" device="_ASPI-4030S-4R7M-T" value="ASPI-4030S-4R7M-T"/>
<part name="C12" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="CAP-POL" device="_RUBYCON_CAP-POL-3.5X8" value="47u0 35V0"/>
<part name="C13" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="CAP-NON-POL" device="_TC_CAP-7.5" value="C927U102KZYDAA7317"/>
<part name="C14" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="CAP-NON-POL" device="_TC_CAP-7.5" value="W1X223SCVCF0KR"/>
<part name="C15" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="CAP-NON-POL" device="_TC_CAP-7.5" value="W1X223SCVCF0KR"/>
<part name="C16" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="CAP-NON-POL" device="_TC_CAP-7.5" value="W1X223SCVCF0KR"/>
<part name="L3" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="INDUCTOR" device="_7447720122"/>
<part name="C17" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="CAP-NON-POL" device="_SAMSUNG-0402" value="0u1 50V0"/>
<part name="C18" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="CAP-NON-POL" device="_SAMSUNG-0402" value="1n0 50V0"/>
<part name="U$3" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="SYM-GND" device=""/>
<part name="BR1" library="VOSTOK_MISC_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2QirG-pvTuembVHon_9QUw" deviceset="GBJ2510" device="" value="3191-GBJ2510-ND"/>
<part name="C19" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="CAP-POL" device="_RUBYCON_CAP-POL-7.5X16" value="UCS2C101MHD6TN"/>
<part name="C20" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="CAP-POL" device="_RUBYCON_CAP-POL-7.5X16" value="UCS2C101MHD6TN"/>
<part name="C21" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="CAP-POL" device="_RUBYCON_CAP-POL-7.5X16" value="UCS2C101MHD6TN"/>
<part name="U$7" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="SYM-GND" device=""/>
<part name="U$8" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="SYM-12V0" device=""/>
<part name="U$9" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="SYM-4V0" device=""/>
<part name="U$12" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="SYM-12V0" device=""/>
<part name="U2" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="UCC27517DBVR" device=""/>
<part name="C22" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="CAP-NON-POL" device="_SAMSUNG-0805" value="1u0 25V0"/>
<part name="C23" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="CAP-NON-POL" device="_SAMSUNG-0402" value="0u1 50V0"/>
<part name="R5" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="RES-CHIP" device="_YAGEO-0402" value="TBD"/>
<part name="U$13" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="SYM-GND" device=""/>
<part name="U$14" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="SYM-12V0" device=""/>
<part name="U3" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="UCC27517DBVR" device=""/>
<part name="C24" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="CAP-NON-POL" device="_SAMSUNG-0805" value="1u0 25V0"/>
<part name="C25" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="CAP-NON-POL" device="_SAMSUNG-0402" value="0u1 50V0"/>
<part name="R6" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="RES-CHIP" device="_YAGEO-0402" value="TBD"/>
<part name="U$15" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="SYM-GND" device=""/>
<part name="U$16" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="SYM-12V0" device=""/>
<part name="U4" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="UCC27517DBVR" device=""/>
<part name="C26" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="CAP-NON-POL" device="_SAMSUNG-0805" value="1u0 25V0"/>
<part name="C27" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="CAP-NON-POL" device="_SAMSUNG-0402" value="0u1 50V0"/>
<part name="R7" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="RES-CHIP" device="_YAGEO-0402" value="TBD"/>
<part name="U$17" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="SYM-GND" device=""/>
<part name="U$18" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="SYM-12V0" device=""/>
<part name="U$19" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="SYM-GND" device=""/>
<part name="DISP1" library="VOSTOK_MISC_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2QirG-pvTuembVHon_9QUw" deviceset="DISP-1743" device=""/>
<part name="U$1" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="SYM-GND" device=""/>
<part name="U$23" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="SYM-3V3" device=""/>
<part name="D1" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="DIODE-LED" device="_B1701NG--20D000314U1930" value="B1701NG--20D000314U1930"/>
<part name="R8" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="RES-CHIP" device="_YAGEO-0402" value="TBD"/>
<part name="D2" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="DIODE-LED" device="_B1701NG--20D000314U1930" value="B1701NG--20D000314U1930"/>
<part name="R9" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="RES-CHIP" device="_YAGEO-0402" value="TBD"/>
<part name="U$10" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="SYM-4V0" device=""/>
<part name="U$11" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="SYM-GND" device=""/>
<part name="U$24" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="SYM-GND" device=""/>
<part name="C28" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="CAP-NON-POL" device="_SAMSUNG-0805" value="1u0 25V0"/>
<part name="C29" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="CAP-NON-POL" device="_SAMSUNG-0402" value="0u1 50V0"/>
<part name="U$25" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="SYM-4V0" device=""/>
<part name="U$26" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="SYM-GND" device=""/>
<part name="H1" library="VOSTOK_MISC_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2QirG-pvTuembVHon_9QUw" deviceset="TB008A-508-02BE" device=""/>
<part name="H2" library="VOSTOK_MISC_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2QirG-pvTuembVHon_9QUw" deviceset="TB008A-508-02BE" device=""/>
<part name="H3" library="VOSTOK_MISC_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2QirG-pvTuembVHon_9QUw" deviceset="TB008A-508-02BE" device=""/>
<part name="H4" library="VOSTOK_MISC_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2QirG-pvTuembVHon_9QUw" deviceset="JST-PH-2POS" device=""/>
<part name="H5" library="VOSTOK_MISC_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2QirG-pvTuembVHon_9QUw" deviceset="JST-PH-2POS" device=""/>
<part name="H6" library="VOSTOK_MISC_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2QirG-pvTuembVHon_9QUw" deviceset="JST-PH-2POS" device=""/>
<part name="H7" library="VOSTOK_MISC_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2QirG-pvTuembVHon_9QUw" deviceset="JST-PH-2POS" device=""/>
<part name="H8" library="VOSTOK_MISC_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2QirG-pvTuembVHon_9QUw" deviceset="JST-PH-2POS" device=""/>
<part name="H9" library="VOSTOK_MISC_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2QirG-pvTuembVHon_9QUw" deviceset="JST-PH-2POS" device=""/>
<part name="R10" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="RES-CHIP" device="_YAGEO-0402" value="5K0"/>
<part name="R11" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="RES-CHIP" device="_YAGEO-0402" value="5K0"/>
<part name="R12" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="RES-CHIP" device="_YAGEO-0402" value="5K0"/>
<part name="R13" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="RES-CHIP" device="_YAGEO-0402" value="5K0"/>
<part name="R14" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="RES-CHIP" device="_YAGEO-0402" value="5K0"/>
<part name="R15" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="RES-CHIP" device="_YAGEO-0402" value="5K0"/>
<part name="U$4" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="SYM-GND" device=""/>
<part name="U$5" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="SYM-3V3" device=""/>
<part name="U$6" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="SYM-3V3" device=""/>
<part name="AC" library="VOSTOK_MISC_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2QirG-pvTuembVHon_9QUw" deviceset="TB008A-508-02BE" device=""/>
<part name="Q1" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="FET-NCH" device="_FET_TO220-VTH" value="RCX300N20"/>
<part name="Q2" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="FET-NCH" device="_FET_TO220-VTH" value="RCX300N20"/>
<part name="Q3" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="FET-NCH" device="_FET_TO220-VTH" value="RCX300N20"/>
<part name="C30" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="CAP-NON-POL" device="_SAMSUNG-0402" value="0u1 50V0 X7R"/>
<part name="C31" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="CAP-NON-POL" device="_SAMSUNG-0402" value="1n0 50V0 C0G/NP0"/>
<part name="U5" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="MAX31850" device="_MAX31850KATB+T" value="MAX31850KATB+T">
<attribute name="SPICEPREFIX" value="X"/>
</part>
<part name="C32" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="CAP-NON-POL" device="_SAMSUNG-0402" value="0u1 50V0">
<attribute name="SPICEPREFIX" value="C"/>
</part>
<part name="C33" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="CAP-NON-POL" device="_SAMSUNG-0402" value="0u1 50V0">
<attribute name="SPICEPREFIX" value="C"/>
</part>
<part name="A3L" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="RES-CHIP" device="_YAGEO-0402" value="TBD">
<attribute name="SPICEPREFIX" value="B"/>
</part>
<part name="A3H" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="RES-CHIP" device="_YAGEO-0402" value="TBD">
<attribute name="SPICEPREFIX" value="B"/>
</part>
<part name="A2L" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="RES-CHIP" device="_YAGEO-0402" value="TBD">
<attribute name="SPICEPREFIX" value="B"/>
</part>
<part name="A2H" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="RES-CHIP" device="_YAGEO-0402" value="TBD">
<attribute name="SPICEPREFIX" value="B"/>
</part>
<part name="A1L" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="RES-CHIP" device="_YAGEO-0402" value="TBD">
<attribute name="SPICEPREFIX" value="B"/>
</part>
<part name="A1H" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="RES-CHIP" device="_YAGEO-0402" value="TBD">
<attribute name="SPICEPREFIX" value="B"/>
</part>
<part name="A0L" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="RES-CHIP" device="_YAGEO-0402" value="TBD">
<attribute name="SPICEPREFIX" value="B"/>
</part>
<part name="U$27" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="SYM-GND" device="">
<attribute name="SPICEPREFIX" value="G"/>
</part>
<part name="C34" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="CAP-NON-POL" device="_SAMSUNG-0603" value="1u0 25V0">
<attribute name="SPICEPREFIX" value="C"/>
</part>
<part name="C35" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="CAP-NON-POL" device="_SAMSUNG-0603" value="1u0 25V0">
<attribute name="SPICEPREFIX" value="C"/>
</part>
<part name="VR1" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="MIC5365-3.3YC5-TR" device="&quot;" value="MIC5365-3.3YC5-TR">
<attribute name="SPICEPREFIX" value="E"/>
</part>
<part name="U$28" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="SYM-4V0" device=""/>
<part name="U$29" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="SYM-GND" device="">
<attribute name="SPICEPREFIX" value="G"/>
</part>
<part name="U$30" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="SYM-GND" device="">
<attribute name="SPICEPREFIX" value="G"/>
</part>
<part name="A0H" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="RES-CHIP" device="_YAGEO-0402" value="TBD">
<attribute name="SPICEPREFIX" value="B"/>
</part>
<part name="H10" library="VOSTOK_MISC_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2QirG-pvTuembVHon_9QUw" deviceset="JST-PH-2POS" device=""/>
<part name="H11" library="VOSTOK_MISC_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2QirG-pvTuembVHon_9QUw" deviceset="JST-PH-2POS" device=""/>
<part name="H12" library="VOSTOK_MISC_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2QirG-pvTuembVHon_9QUw" deviceset="JST-PH-2POS" device=""/>
<part name="R16" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="RES-CHIP" device="_YAGEO-0402" value="5K0"/>
<part name="U$31" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="SYM-3V3" device=""/>
<part name="U6" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="MAX31850" device="_MAX31850KATB+T" value="MAX31850KATB+T">
<attribute name="SPICEPREFIX" value="X"/>
</part>
<part name="C36" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="CAP-NON-POL" device="_SAMSUNG-0402" value="0u1 50V0">
<attribute name="SPICEPREFIX" value="C"/>
</part>
<part name="C37" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="CAP-NON-POL" device="_SAMSUNG-0402" value="0u1 50V0">
<attribute name="SPICEPREFIX" value="C"/>
</part>
<part name="A3L1" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="RES-CHIP" device="_YAGEO-0402" value="TBD">
<attribute name="SPICEPREFIX" value="B"/>
</part>
<part name="A3H1" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="RES-CHIP" device="_YAGEO-0402" value="TBD">
<attribute name="SPICEPREFIX" value="B"/>
</part>
<part name="A2L1" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="RES-CHIP" device="_YAGEO-0402" value="TBD">
<attribute name="SPICEPREFIX" value="B"/>
</part>
<part name="A2H1" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="RES-CHIP" device="_YAGEO-0402" value="TBD">
<attribute name="SPICEPREFIX" value="B"/>
</part>
<part name="A1L1" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="RES-CHIP" device="_YAGEO-0402" value="TBD">
<attribute name="SPICEPREFIX" value="B"/>
</part>
<part name="A1H1" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="RES-CHIP" device="_YAGEO-0402" value="TBD">
<attribute name="SPICEPREFIX" value="B"/>
</part>
<part name="A0L1" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="RES-CHIP" device="_YAGEO-0402" value="TBD">
<attribute name="SPICEPREFIX" value="B"/>
</part>
<part name="U$32" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="SYM-GND" device="">
<attribute name="SPICEPREFIX" value="G"/>
</part>
<part name="C38" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="CAP-NON-POL" device="_SAMSUNG-0603" value="1u0 25V0">
<attribute name="SPICEPREFIX" value="C"/>
</part>
<part name="C39" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="CAP-NON-POL" device="_SAMSUNG-0603" value="1u0 25V0">
<attribute name="SPICEPREFIX" value="C"/>
</part>
<part name="VR2" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="MIC5365-3.3YC5-TR" device="&quot;" value="MIC5365-3.3YC5-TR">
<attribute name="SPICEPREFIX" value="E"/>
</part>
<part name="U$33" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="SYM-4V0" device=""/>
<part name="U$34" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="SYM-GND" device="">
<attribute name="SPICEPREFIX" value="G"/>
</part>
<part name="U$35" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="SYM-GND" device="">
<attribute name="SPICEPREFIX" value="G"/>
</part>
<part name="A0H1" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="RES-CHIP" device="_YAGEO-0402" value="TBD">
<attribute name="SPICEPREFIX" value="B"/>
</part>
<part name="U7" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="MAX31850" device="_MAX31850KATB+T" value="MAX31850KATB+T">
<attribute name="SPICEPREFIX" value="X"/>
</part>
<part name="C40" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="CAP-NON-POL" device="_SAMSUNG-0402" value="0u1 50V0">
<attribute name="SPICEPREFIX" value="C"/>
</part>
<part name="C41" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="CAP-NON-POL" device="_SAMSUNG-0402" value="0u1 50V0">
<attribute name="SPICEPREFIX" value="C"/>
</part>
<part name="A3L2" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="RES-CHIP" device="_YAGEO-0402" value="TBD">
<attribute name="SPICEPREFIX" value="B"/>
</part>
<part name="A3H2" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="RES-CHIP" device="_YAGEO-0402" value="TBD">
<attribute name="SPICEPREFIX" value="B"/>
</part>
<part name="A2L2" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="RES-CHIP" device="_YAGEO-0402" value="TBD">
<attribute name="SPICEPREFIX" value="B"/>
</part>
<part name="A2H2" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="RES-CHIP" device="_YAGEO-0402" value="TBD">
<attribute name="SPICEPREFIX" value="B"/>
</part>
<part name="A1L2" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="RES-CHIP" device="_YAGEO-0402" value="TBD">
<attribute name="SPICEPREFIX" value="B"/>
</part>
<part name="A1H2" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="RES-CHIP" device="_YAGEO-0402" value="TBD">
<attribute name="SPICEPREFIX" value="B"/>
</part>
<part name="A0L2" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="RES-CHIP" device="_YAGEO-0402" value="TBD">
<attribute name="SPICEPREFIX" value="B"/>
</part>
<part name="U$36" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="SYM-GND" device="">
<attribute name="SPICEPREFIX" value="G"/>
</part>
<part name="C42" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="CAP-NON-POL" device="_SAMSUNG-0603" value="1u0 25V0">
<attribute name="SPICEPREFIX" value="C"/>
</part>
<part name="C43" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="CAP-NON-POL" device="_SAMSUNG-0603" value="1u0 25V0">
<attribute name="SPICEPREFIX" value="C"/>
</part>
<part name="VR3" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="MIC5365-3.3YC5-TR" device="&quot;" value="MIC5365-3.3YC5-TR">
<attribute name="SPICEPREFIX" value="E"/>
</part>
<part name="U$37" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="SYM-4V0" device=""/>
<part name="U$38" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="SYM-GND" device="">
<attribute name="SPICEPREFIX" value="G"/>
</part>
<part name="U$39" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="SYM-GND" device="">
<attribute name="SPICEPREFIX" value="G"/>
</part>
<part name="A0H2" library="VOSTOK_KRAETON_LIB" library_urn="urn:adsk.wipprod:fs.file:vf.2FIgwUkRSduhHATOY2hocQ" deviceset="RES-CHIP" device="_YAGEO-0402" value="TBD">
<attribute name="SPICEPREFIX" value="B"/>
</part>
</parts>
<sheets>
<sheet>
<description>POWER SUPPLY</description>
<plain>
<text x="5.08" y="172.72" size="1.778" layer="94">120V AC TO 12V DC</text>
<text x="5.08" y="86.36" size="1.778" layer="94">12V DC TO 4V DC</text>
<text x="5.08" y="83.82" size="0.889" layer="94">3.96V NOM</text>
</plain>
<instances>
<instance part="PS1" gate="G$1" x="140.97" y="146.05" smashed="yes">
<attribute name="VALUE" x="140.97" y="135.89" size="1.778" layer="96" align="center"/>
<attribute name="NAME" x="140.97" y="156.21" size="1.778" layer="95" align="center"/>
</instance>
<instance part="C1" gate="G$1" x="194.31" y="59.69" smashed="yes" rot="R90">
<attribute name="VALUE" x="198.12" y="59.69" size="1.778" layer="96" rot="R90" align="center"/>
<attribute name="NAME" x="190.5" y="59.69" size="1.778" layer="95" rot="R90" align="center"/>
</instance>
<instance part="C2" gate="G$1" x="204.47" y="59.69" smashed="yes" rot="R90">
<attribute name="VALUE" x="208.28" y="59.69" size="1.778" layer="96" rot="R90" align="center"/>
<attribute name="NAME" x="200.66" y="59.69" size="1.778" layer="95" rot="R90" align="center"/>
</instance>
<instance part="C3" gate="G$1" x="113.03" y="59.69" smashed="yes" rot="R90">
<attribute name="VALUE" x="116.84" y="59.69" size="1.778" layer="96" rot="R90" align="center"/>
<attribute name="NAME" x="109.22" y="59.69" size="1.778" layer="95" rot="R90" align="center"/>
</instance>
<instance part="C4" gate="G$1" x="102.87" y="59.69" smashed="yes" rot="R90">
<attribute name="VALUE" x="106.68" y="59.69" size="1.778" layer="96" rot="R90" align="center"/>
<attribute name="NAME" x="99.06" y="59.69" size="1.778" layer="95" rot="R90" align="center"/>
</instance>
<instance part="R1" gate="G$1" x="121.92" y="59.69" smashed="yes" rot="R90">
<attribute name="NAME" x="119.38" y="59.69" size="1.778" layer="95" rot="R90" align="center"/>
<attribute name="VALUE" x="124.46" y="59.69" size="1.778" layer="96" rot="R90" align="center"/>
</instance>
<instance part="R2" gate="G$1" x="137.16" y="44.45" smashed="yes" rot="R180">
<attribute name="NAME" x="137.16" y="41.91" size="1.778" layer="95" rot="R180" align="center"/>
<attribute name="VALUE" x="137.16" y="46.99" size="1.778" layer="96" rot="R180" align="center"/>
</instance>
<instance part="C5" gate="G$1" x="92.71" y="59.69" smashed="yes" rot="R90">
<attribute name="VALUE" x="96.52" y="59.69" size="1.778" layer="96" rot="R90" align="center"/>
<attribute name="NAME" x="88.9" y="59.69" size="1.778" layer="95" rot="R90" align="center"/>
</instance>
<instance part="C6" gate="G$1" x="82.55" y="59.69" smashed="yes" rot="R90">
<attribute name="VALUE" x="86.36" y="59.69" size="1.778" layer="96" rot="R90" align="center"/>
<attribute name="NAME" x="78.74" y="59.69" size="1.778" layer="95" rot="R90" align="center"/>
</instance>
<instance part="L1" gate="G$1" x="166.37" y="69.85" smashed="yes">
<attribute name="NAME" x="166.37" y="74.93" size="1.778" layer="95" align="center"/>
<attribute name="VALUE" x="166.37" y="72.39" size="1.778" layer="95" align="center"/>
</instance>
<instance part="C9" gate="G$1" x="176.53" y="59.69" smashed="yes" rot="R90">
<attribute name="VALUE" x="180.34" y="59.69" size="1.778" layer="96" rot="R90" align="center"/>
<attribute name="NAME" x="172.72" y="59.69" size="1.778" layer="95" rot="R90" align="center"/>
</instance>
<instance part="R3" gate="G$1" x="185.42" y="59.69" smashed="yes" rot="R90">
<attribute name="NAME" x="182.88" y="59.69" size="1.778" layer="95" rot="R90" align="center"/>
<attribute name="VALUE" x="187.96" y="59.69" size="1.778" layer="96" rot="R90" align="center"/>
</instance>
<instance part="R4" gate="G$1" x="175.26" y="44.45" smashed="yes" rot="R180">
<attribute name="NAME" x="175.26" y="41.91" size="1.778" layer="95" rot="R180" align="center"/>
<attribute name="VALUE" x="175.26" y="46.99" size="1.778" layer="96" rot="R180" align="center"/>
</instance>
<instance part="U1" gate="G$1" x="143.51" y="64.77" smashed="yes">
<attribute name="NAME" x="143.51" y="74.93" size="1.778" layer="95" align="center"/>
<attribute name="VALUE" x="143.51" y="52.07" size="1.778" layer="96" align="center"/>
</instance>
<instance part="C7" gate="G$1" x="72.39" y="59.69" smashed="yes" rot="R90">
<attribute name="VALUE" x="76.2" y="59.69" size="1.778" layer="96" rot="R90" align="center"/>
<attribute name="NAME" x="68.58" y="59.69" size="1.778" layer="95" rot="R90" align="center"/>
</instance>
<instance part="C8" gate="G$1" x="62.23" y="59.69" smashed="yes" rot="R90">
<attribute name="VALUE" x="66.04" y="59.69" size="1.778" layer="96" rot="R90" align="center"/>
<attribute name="NAME" x="58.42" y="59.69" size="1.778" layer="95" rot="R90" align="center"/>
</instance>
<instance part="F1" gate="G$1" x="67.31" y="151.13" smashed="yes">
<attribute name="NAME" x="67.31" y="154.305" size="1.778" layer="95" align="center"/>
<attribute name="VALUE" x="67.31" y="147.955" size="1.778" layer="95" align="center"/>
</instance>
<instance part="R17" gate="G$1" x="90.17" y="151.13" smashed="yes">
<attribute name="NAME" x="90.17" y="153.67" size="1.778" layer="95" align="center"/>
<attribute name="VALUE" x="90.17" y="148.59" size="1.778" layer="96" align="center"/>
</instance>
<instance part="C10" gate="G$1" x="120.65" y="133.35" smashed="yes" rot="R90">
<attribute name="VALUE" x="124.46" y="133.35" size="1.778" layer="96" rot="R90" align="center"/>
<attribute name="NAME" x="116.84" y="133.35" size="1.778" layer="95" rot="R90" align="center"/>
</instance>
<instance part="C11" gate="G$1" x="163.83" y="140.97" smashed="yes" rot="R90">
<attribute name="VALUE" x="167.64" y="140.97" size="1.778" layer="96" rot="R90" align="center"/>
<attribute name="NAME" x="160.02" y="140.97" size="1.778" layer="95" rot="R90" align="center"/>
</instance>
<instance part="L2" gate="G$1" x="173.99" y="151.13" smashed="yes">
<attribute name="NAME" x="173.99" y="156.21" size="1.778" layer="95" align="center"/>
<attribute name="VALUE" x="173.99" y="153.67" size="1.778" layer="95" align="center"/>
</instance>
<instance part="C12" gate="G$1" x="184.15" y="140.97" smashed="yes" rot="R90">
<attribute name="VALUE" x="187.96" y="140.97" size="1.778" layer="96" rot="R90" align="center"/>
<attribute name="NAME" x="180.34" y="140.97" size="1.778" layer="95" rot="R90" align="center"/>
</instance>
<instance part="C13" gate="G$1" x="140.97" y="123.19" smashed="yes">
<attribute name="VALUE" x="140.97" y="119.38" size="1.778" layer="96" align="center"/>
<attribute name="NAME" x="140.97" y="127" size="1.778" layer="95" align="center"/>
</instance>
<instance part="C14" gate="G$1" x="102.87" y="135.89" smashed="yes" rot="R90">
<attribute name="VALUE" x="106.68" y="135.89" size="1.778" layer="96" rot="R90" align="center"/>
<attribute name="NAME" x="99.06" y="135.89" size="1.778" layer="95" rot="R90" align="center"/>
</instance>
<instance part="C15" gate="G$1" x="92.71" y="135.89" smashed="yes" rot="R90">
<attribute name="VALUE" x="96.52" y="135.89" size="1.778" layer="96" rot="R90" align="center"/>
<attribute name="NAME" x="88.9" y="135.89" size="1.778" layer="95" rot="R90" align="center"/>
</instance>
<instance part="C16" gate="G$1" x="82.55" y="135.89" smashed="yes" rot="R90">
<attribute name="VALUE" x="86.36" y="135.89" size="1.778" layer="96" rot="R90" align="center"/>
<attribute name="NAME" x="78.74" y="135.89" size="1.778" layer="95" rot="R90" align="center"/>
</instance>
<instance part="L3" gate="G$1" x="113.03" y="151.13" smashed="yes">
<attribute name="NAME" x="113.03" y="156.21" size="1.778" layer="95" align="center"/>
<attribute name="VALUE" x="113.03" y="153.67" size="1.778" layer="95" align="center"/>
</instance>
<instance part="C17" gate="G$1" x="194.31" y="140.97" smashed="yes" rot="R90">
<attribute name="VALUE" x="198.12" y="140.97" size="1.778" layer="96" rot="R90" align="center"/>
<attribute name="NAME" x="190.5" y="140.97" size="1.778" layer="95" rot="R90" align="center"/>
</instance>
<instance part="C18" gate="G$1" x="204.47" y="140.97" smashed="yes" rot="R90">
<attribute name="VALUE" x="208.28" y="140.97" size="1.778" layer="96" rot="R90" align="center"/>
<attribute name="NAME" x="200.66" y="140.97" size="1.778" layer="95" rot="R90" align="center"/>
</instance>
<instance part="U$3" gate="G$1" x="204.47" y="118.11" smashed="yes"/>
<instance part="U$7" gate="G$1" x="62.23" y="35.56" smashed="yes"/>
<instance part="U$8" gate="G$1" x="62.23" y="72.39" smashed="yes"/>
<instance part="U$9" gate="G$1" x="224.79" y="72.39" smashed="yes"/>
<instance part="U$12" gate="G$1" x="204.47" y="153.67" smashed="yes"/>
<instance part="AC" gate="G$1" x="44.45" y="148.59" smashed="yes" rot="R180">
<attribute name="NAME" x="40.64" y="148.59" size="1.778" layer="95" rot="R270" align="center"/>
<attribute name="VALUE" x="38.1" y="148.59" size="1.778" layer="96" rot="R270" align="center"/>
</instance>
<instance part="C30" gate="G$1" x="214.63" y="59.69" smashed="yes" rot="R90">
<attribute name="VALUE" x="218.44" y="59.69" size="1.778" layer="96" rot="R90" align="center"/>
<attribute name="NAME" x="210.82" y="59.69" size="1.778" layer="95" rot="R90" align="center"/>
</instance>
<instance part="C31" gate="G$1" x="224.79" y="59.69" smashed="yes" rot="R90">
<attribute name="VALUE" x="228.6" y="59.69" size="1.778" layer="96" rot="R90" align="center"/>
<attribute name="NAME" x="220.98" y="59.69" size="1.778" layer="95" rot="R90" align="center"/>
</instance>
</instances>
<busses>
</busses>
<nets>
<net name="GND" class="0">
<segment>
<pinref part="PS1" gate="G$1" pin="GND"/>
<wire x1="153.67" y1="140.97" x2="156.21" y2="140.97" width="0.1524" layer="91"/>
<wire x1="156.21" y1="140.97" x2="156.21" y2="123.19" width="0.1524" layer="91"/>
<wire x1="156.21" y1="123.19" x2="148.59" y2="123.19" width="0.1524" layer="91"/>
<wire x1="156.21" y1="123.19" x2="163.83" y2="123.19" width="0.1524" layer="91"/>
<wire x1="163.83" y1="123.19" x2="163.83" y2="133.35" width="0.1524" layer="91"/>
<wire x1="163.83" y1="123.19" x2="184.15" y2="123.19" width="0.1524" layer="91"/>
<wire x1="184.15" y1="123.19" x2="184.15" y2="133.35" width="0.1524" layer="91"/>
<wire x1="194.31" y1="133.35" x2="194.31" y2="123.19" width="0.1524" layer="91"/>
<wire x1="194.31" y1="123.19" x2="184.15" y2="123.19" width="0.1524" layer="91"/>
<wire x1="204.47" y1="133.35" x2="204.47" y2="123.19" width="0.1524" layer="91"/>
<wire x1="204.47" y1="123.19" x2="194.31" y2="123.19" width="0.1524" layer="91"/>
<junction x="156.21" y="123.19"/>
<junction x="163.83" y="123.19"/>
<junction x="184.15" y="123.19"/>
<junction x="194.31" y="123.19"/>
<wire x1="204.47" y1="123.19" x2="204.47" y2="120.65" width="0.1524" layer="91"/>
<junction x="204.47" y="123.19"/>
<pinref part="U$3" gate="G$1" pin="GND"/>
<pinref part="C11" gate="G$1" pin="-"/>
<pinref part="C12" gate="G$1" pin="-"/>
<pinref part="C13" gate="G$1" pin="P$2"/>
<pinref part="C17" gate="G$1" pin="P$1"/>
<pinref part="C18" gate="G$1" pin="P$1"/>
</segment>
<segment>
<pinref part="U$7" gate="G$1" pin="GND"/>
<wire x1="62.23" y1="38.1" x2="62.23" y2="40.64" width="0.1524" layer="91"/>
<wire x1="153.67" y1="57.15" x2="157.48" y2="57.15" width="0.1524" layer="91"/>
<wire x1="153.67" y1="59.69" x2="157.48" y2="59.69" width="0.1524" layer="91"/>
<wire x1="157.48" y1="59.69" x2="157.48" y2="57.15" width="0.1524" layer="91"/>
<wire x1="194.31" y1="40.64" x2="162.56" y2="40.64" width="0.1524" layer="91"/>
<wire x1="162.56" y1="40.64" x2="157.48" y2="40.64" width="0.1524" layer="91"/>
<wire x1="157.48" y1="40.64" x2="157.48" y2="57.15" width="0.1524" layer="91"/>
<wire x1="194.31" y1="52.07" x2="194.31" y2="40.64" width="0.1524" layer="91"/>
<wire x1="204.47" y1="52.07" x2="204.47" y2="40.64" width="0.1524" layer="91"/>
<wire x1="204.47" y1="40.64" x2="194.31" y2="40.64" width="0.1524" layer="91"/>
<wire x1="113.03" y1="40.64" x2="147.32" y2="40.64" width="0.1524" layer="91"/>
<wire x1="147.32" y1="40.64" x2="157.48" y2="40.64" width="0.1524" layer="91"/>
<wire x1="113.03" y1="52.07" x2="113.03" y2="40.64" width="0.1524" layer="91"/>
<wire x1="102.87" y1="52.07" x2="102.87" y2="40.64" width="0.1524" layer="91"/>
<wire x1="102.87" y1="40.64" x2="113.03" y2="40.64" width="0.1524" layer="91"/>
<wire x1="92.71" y1="52.07" x2="92.71" y2="40.64" width="0.1524" layer="91"/>
<wire x1="92.71" y1="40.64" x2="102.87" y2="40.64" width="0.1524" layer="91"/>
<wire x1="82.55" y1="52.07" x2="82.55" y2="40.64" width="0.1524" layer="91"/>
<wire x1="82.55" y1="40.64" x2="92.71" y2="40.64" width="0.1524" layer="91"/>
<wire x1="72.39" y1="52.07" x2="72.39" y2="40.64" width="0.1524" layer="91"/>
<wire x1="72.39" y1="40.64" x2="82.55" y2="40.64" width="0.1524" layer="91"/>
<wire x1="62.23" y1="52.07" x2="62.23" y2="40.64" width="0.1524" layer="91"/>
<wire x1="62.23" y1="40.64" x2="72.39" y2="40.64" width="0.1524" layer="91"/>
<pinref part="U1" gate="G$1" pin="AGND"/>
<pinref part="U1" gate="G$1" pin="GND"/>
<wire x1="144.78" y1="44.45" x2="147.32" y2="44.45" width="0.1524" layer="91"/>
<wire x1="147.32" y1="44.45" x2="147.32" y2="40.64" width="0.1524" layer="91"/>
<wire x1="167.64" y1="44.45" x2="162.56" y2="44.45" width="0.1524" layer="91"/>
<wire x1="162.56" y1="44.45" x2="162.56" y2="40.64" width="0.1524" layer="91"/>
<junction x="62.23" y="40.64"/>
<junction x="157.48" y="57.15"/>
<junction x="194.31" y="40.64"/>
<junction x="162.56" y="40.64"/>
<junction x="157.48" y="40.64"/>
<junction x="113.03" y="40.64"/>
<junction x="147.32" y="40.64"/>
<junction x="102.87" y="40.64"/>
<junction x="92.71" y="40.64"/>
<junction x="82.55" y="40.64"/>
<junction x="72.39" y="40.64"/>
<wire x1="204.47" y1="40.64" x2="214.63" y2="40.64" width="0.1524" layer="91"/>
<wire x1="214.63" y1="40.64" x2="214.63" y2="52.07" width="0.1524" layer="91"/>
<junction x="204.47" y="40.64"/>
<wire x1="214.63" y1="40.64" x2="224.79" y2="40.64" width="0.1524" layer="91"/>
<wire x1="224.79" y1="40.64" x2="224.79" y2="52.07" width="0.1524" layer="91"/>
<junction x="214.63" y="40.64"/>
<pinref part="C1" gate="G$1" pin="P$1"/>
<pinref part="C2" gate="G$1" pin="P$1"/>
<pinref part="C3" gate="G$1" pin="P$1"/>
<pinref part="C4" gate="G$1" pin="P$1"/>
<pinref part="R2" gate="G$1" pin="P$1"/>
<pinref part="C5" gate="G$1" pin="P$1"/>
<pinref part="C6" gate="G$1" pin="P$1"/>
<pinref part="R4" gate="G$1" pin="P$2"/>
<pinref part="C7" gate="G$1" pin="P$1"/>
<pinref part="C8" gate="G$1" pin="P$1"/>
<pinref part="C30" gate="G$1" pin="P$1"/>
<pinref part="C31" gate="G$1" pin="P$1"/>
</segment>
</net>
<net name="OUT" class="0">
<segment>
<wire x1="153.67" y1="69.85" x2="158.75" y2="69.85" width="0.1524" layer="91"/>
<pinref part="U1" gate="G$1" pin="SW"/>
<pinref part="L1" gate="G$1" pin="P$1"/>
</segment>
</net>
<net name="N$9" class="0">
<segment>
<wire x1="162.56" y1="49.53" x2="162.56" y2="64.77" width="0.1524" layer="91"/>
<wire x1="162.56" y1="64.77" x2="153.67" y2="64.77" width="0.1524" layer="91"/>
<wire x1="162.56" y1="49.53" x2="176.53" y2="49.53" width="0.1524" layer="91"/>
<wire x1="176.53" y1="49.53" x2="185.42" y2="49.53" width="0.1524" layer="91"/>
<wire x1="185.42" y1="49.53" x2="185.42" y2="52.07" width="0.1524" layer="91"/>
<wire x1="176.53" y1="52.07" x2="176.53" y2="49.53" width="0.1524" layer="91"/>
<junction x="176.53" y="49.53"/>
<pinref part="U1" gate="G$1" pin="FB"/>
<wire x1="182.88" y1="44.45" x2="185.42" y2="44.45" width="0.1524" layer="91"/>
<wire x1="185.42" y1="44.45" x2="185.42" y2="49.53" width="0.1524" layer="91"/>
<junction x="185.42" y="49.53"/>
<pinref part="C9" gate="G$1" pin="P$1"/>
<pinref part="R3" gate="G$1" pin="P$1"/>
<pinref part="R4" gate="G$1" pin="P$1"/>
</segment>
</net>
<net name="N$2" class="0">
<segment>
<wire x1="133.35" y1="57.15" x2="127" y2="57.15" width="0.1524" layer="91"/>
<wire x1="127" y1="57.15" x2="127" y2="44.45" width="0.1524" layer="91"/>
<wire x1="127" y1="44.45" x2="121.92" y2="44.45" width="0.1524" layer="91"/>
<pinref part="U1" gate="G$1" pin="EN"/>
<wire x1="129.54" y1="44.45" x2="127" y2="44.45" width="0.1524" layer="91"/>
<wire x1="121.92" y1="44.45" x2="121.92" y2="52.07" width="0.1524" layer="91"/>
<junction x="127" y="44.45"/>
<pinref part="R1" gate="G$1" pin="P$1"/>
<pinref part="R2" gate="G$1" pin="P$2"/>
</segment>
</net>
<net name="AC_L" class="0">
<segment>
<pinref part="F1" gate="G$1" pin="P$1"/>
<wire x1="59.69" y1="151.13" x2="49.53" y2="151.13" width="0.1524" layer="91"/>
<label x="53.34" y="151.13" size="1.778" layer="95"/>
<pinref part="AC" gate="G$1" pin="2"/>
</segment>
</net>
<net name="N$3" class="0">
<segment>
<pinref part="PS1" gate="G$1" pin="C+"/>
<wire x1="128.27" y1="143.51" x2="120.65" y2="143.51" width="0.1524" layer="91"/>
<wire x1="120.65" y1="143.51" x2="120.65" y2="140.97" width="0.1524" layer="91"/>
<pinref part="C10" gate="G$1" pin="+"/>
</segment>
</net>
<net name="N$4" class="0">
<segment>
<wire x1="120.65" y1="125.73" x2="120.65" y2="123.19" width="0.1524" layer="91"/>
<wire x1="120.65" y1="123.19" x2="125.73" y2="123.19" width="0.1524" layer="91"/>
<pinref part="PS1" gate="G$1" pin="C-"/>
<wire x1="125.73" y1="123.19" x2="133.35" y2="123.19" width="0.1524" layer="91"/>
<wire x1="128.27" y1="140.97" x2="125.73" y2="140.97" width="0.1524" layer="91"/>
<wire x1="125.73" y1="140.97" x2="125.73" y2="123.19" width="0.1524" layer="91"/>
<junction x="125.73" y="123.19"/>
<pinref part="C10" gate="G$1" pin="-"/>
<pinref part="C13" gate="G$1" pin="P$1"/>
</segment>
</net>
<net name="N$6" class="0">
<segment>
<wire x1="166.37" y1="151.13" x2="163.83" y2="151.13" width="0.1524" layer="91"/>
<wire x1="163.83" y1="151.13" x2="163.83" y2="148.59" width="0.1524" layer="91"/>
<wire x1="163.83" y1="151.13" x2="153.67" y2="151.13" width="0.1524" layer="91"/>
<pinref part="PS1" gate="G$1" pin="VOUT"/>
<pinref part="L2" gate="G$1" pin="P$1"/>
<junction x="163.83" y="151.13"/>
<pinref part="C11" gate="G$1" pin="+"/>
</segment>
</net>
<net name="N$8" class="0">
<segment>
<pinref part="F1" gate="G$1" pin="P$2"/>
<wire x1="74.93" y1="151.13" x2="82.55" y2="151.13" width="0.1524" layer="91"/>
<pinref part="R17" gate="G$1" pin="P$4"/>
</segment>
</net>
<net name="N$10" class="0">
<segment>
<pinref part="R17" gate="G$1" pin="P$3"/>
<wire x1="97.79" y1="151.13" x2="102.87" y2="151.13" width="0.1524" layer="91"/>
<pinref part="L3" gate="G$1" pin="P$1"/>
<wire x1="102.87" y1="151.13" x2="105.41" y2="151.13" width="0.1524" layer="91"/>
<junction x="102.87" y="151.13"/>
<wire x1="102.87" y1="151.13" x2="102.87" y2="146.05" width="0.1524" layer="91"/>
<wire x1="102.87" y1="146.05" x2="92.71" y2="146.05" width="0.1524" layer="91"/>
<wire x1="92.71" y1="146.05" x2="92.71" y2="143.51" width="0.1524" layer="91"/>
<wire x1="102.87" y1="146.05" x2="102.87" y2="143.51" width="0.1524" layer="91"/>
<junction x="102.87" y="146.05"/>
<wire x1="92.71" y1="146.05" x2="82.55" y2="146.05" width="0.1524" layer="91"/>
<wire x1="82.55" y1="146.05" x2="82.55" y2="143.51" width="0.1524" layer="91"/>
<junction x="92.71" y="146.05"/>
<pinref part="C14" gate="G$1" pin="P$2"/>
<pinref part="C15" gate="G$1" pin="P$2"/>
<pinref part="C16" gate="G$1" pin="P$2"/>
</segment>
</net>
<net name="N$11" class="0">
<segment>
<pinref part="L3" gate="G$1" pin="P$2"/>
<wire x1="120.65" y1="151.13" x2="128.27" y2="151.13" width="0.1524" layer="91"/>
<pinref part="PS1" gate="G$1" pin="AC(L)"/>
</segment>
</net>
<net name="AC_N" class="0">
<segment>
<pinref part="PS1" gate="G$1" pin="AC(N)"/>
<wire x1="128.27" y1="148.59" x2="110.49" y2="148.59" width="0.1524" layer="91"/>
<wire x1="110.49" y1="148.59" x2="110.49" y2="123.19" width="0.1524" layer="91"/>
<wire x1="110.49" y1="123.19" x2="102.87" y2="123.19" width="0.1524" layer="91"/>
<wire x1="102.87" y1="123.19" x2="92.71" y2="123.19" width="0.1524" layer="91"/>
<wire x1="92.71" y1="123.19" x2="92.71" y2="128.27" width="0.1524" layer="91"/>
<wire x1="92.71" y1="123.19" x2="82.55" y2="123.19" width="0.1524" layer="91"/>
<wire x1="82.55" y1="123.19" x2="82.55" y2="128.27" width="0.1524" layer="91"/>
<wire x1="102.87" y1="128.27" x2="102.87" y2="123.19" width="0.1524" layer="91"/>
<wire x1="82.55" y1="123.19" x2="52.07" y2="123.19" width="0.1524" layer="91"/>
<junction x="102.87" y="123.19"/>
<junction x="92.71" y="123.19"/>
<junction x="82.55" y="123.19"/>
<label x="53.34" y="123.19" size="1.778" layer="95"/>
<wire x1="52.07" y1="123.19" x2="52.07" y2="146.05" width="0.1524" layer="91"/>
<wire x1="52.07" y1="146.05" x2="49.53" y2="146.05" width="0.1524" layer="91"/>
<pinref part="AC" gate="G$1" pin="1"/>
<pinref part="C14" gate="G$1" pin="P$1"/>
<pinref part="C15" gate="G$1" pin="P$1"/>
<pinref part="C16" gate="G$1" pin="P$1"/>
</segment>
</net>
<net name="12V0" class="0">
<segment>
<pinref part="U$8" gate="G$1" pin="12V0"/>
<wire x1="62.23" y1="72.39" x2="62.23" y2="69.85" width="0.1524" layer="91"/>
<wire x1="121.92" y1="69.85" x2="113.03" y2="69.85" width="0.1524" layer="91"/>
<wire x1="113.03" y1="69.85" x2="102.87" y2="69.85" width="0.1524" layer="91"/>
<wire x1="102.87" y1="69.85" x2="92.71" y2="69.85" width="0.1524" layer="91"/>
<wire x1="92.71" y1="69.85" x2="82.55" y2="69.85" width="0.1524" layer="91"/>
<wire x1="82.55" y1="69.85" x2="72.39" y2="69.85" width="0.1524" layer="91"/>
<wire x1="72.39" y1="69.85" x2="62.23" y2="69.85" width="0.1524" layer="91"/>
<wire x1="121.92" y1="69.85" x2="133.35" y2="69.85" width="0.1524" layer="91"/>
<junction x="121.92" y="69.85"/>
<wire x1="121.92" y1="67.31" x2="121.92" y2="69.85" width="0.1524" layer="91"/>
<wire x1="62.23" y1="67.31" x2="62.23" y2="69.85" width="0.1524" layer="91"/>
<wire x1="72.39" y1="67.31" x2="72.39" y2="69.85" width="0.1524" layer="91"/>
<junction x="72.39" y="69.85"/>
<wire x1="82.55" y1="67.31" x2="82.55" y2="69.85" width="0.1524" layer="91"/>
<junction x="82.55" y="69.85"/>
<wire x1="92.71" y1="67.31" x2="92.71" y2="69.85" width="0.1524" layer="91"/>
<junction x="92.71" y="69.85"/>
<wire x1="102.87" y1="67.31" x2="102.87" y2="69.85" width="0.1524" layer="91"/>
<junction x="102.87" y="69.85"/>
<wire x1="113.03" y1="67.31" x2="113.03" y2="69.85" width="0.1524" layer="91"/>
<junction x="113.03" y="69.85"/>
<pinref part="U1" gate="G$1" pin="VIN"/>
<junction x="62.23" y="69.85"/>
<pinref part="C3" gate="G$1" pin="P$2"/>
<pinref part="C4" gate="G$1" pin="P$2"/>
<pinref part="R1" gate="G$1" pin="P$2"/>
<pinref part="C5" gate="G$1" pin="P$2"/>
<pinref part="C6" gate="G$1" pin="P$2"/>
<pinref part="C7" gate="G$1" pin="P$2"/>
<pinref part="C8" gate="G$1" pin="P$2"/>
</segment>
<segment>
<pinref part="U$12" gate="G$1" pin="12V0"/>
<wire x1="204.47" y1="153.67" x2="204.47" y2="151.13" width="0.1524" layer="91"/>
<wire x1="181.61" y1="151.13" x2="184.15" y2="151.13" width="0.1524" layer="91"/>
<wire x1="184.15" y1="151.13" x2="184.15" y2="148.59" width="0.1524" layer="91"/>
<pinref part="L2" gate="G$1" pin="P$2"/>
<wire x1="184.15" y1="151.13" x2="194.31" y2="151.13" width="0.1524" layer="91"/>
<wire x1="194.31" y1="151.13" x2="194.31" y2="148.59" width="0.1524" layer="91"/>
<wire x1="194.31" y1="151.13" x2="204.47" y2="151.13" width="0.1524" layer="91"/>
<wire x1="204.47" y1="151.13" x2="204.47" y2="148.59" width="0.1524" layer="91"/>
<junction x="184.15" y="151.13"/>
<junction x="194.31" y="151.13"/>
<pinref part="C12" gate="G$1" pin="+"/>
<junction x="204.47" y="151.13"/>
<pinref part="C17" gate="G$1" pin="P$2"/>
<pinref part="C18" gate="G$1" pin="P$2"/>
</segment>
</net>
<net name="4V0" class="0">
<segment>
<pinref part="U$9" gate="G$1" pin="4V0"/>
<wire x1="224.79" y1="72.39" x2="224.79" y2="69.85" width="0.1524" layer="91"/>
<wire x1="194.31" y1="69.85" x2="204.47" y2="69.85" width="0.1524" layer="91"/>
<wire x1="194.31" y1="67.31" x2="194.31" y2="69.85" width="0.1524" layer="91"/>
<wire x1="204.47" y1="67.31" x2="204.47" y2="69.85" width="0.1524" layer="91"/>
<wire x1="173.99" y1="69.85" x2="176.53" y2="69.85" width="0.1524" layer="91"/>
<wire x1="176.53" y1="69.85" x2="185.42" y2="69.85" width="0.1524" layer="91"/>
<wire x1="185.42" y1="69.85" x2="194.31" y2="69.85" width="0.1524" layer="91"/>
<wire x1="185.42" y1="67.31" x2="185.42" y2="69.85" width="0.1524" layer="91"/>
<wire x1="176.53" y1="67.31" x2="176.53" y2="69.85" width="0.1524" layer="91"/>
<pinref part="L1" gate="G$1" pin="P$2"/>
<wire x1="204.47" y1="69.85" x2="214.63" y2="69.85" width="0.1524" layer="91"/>
<wire x1="214.63" y1="69.85" x2="214.63" y2="67.31" width="0.1524" layer="91"/>
<wire x1="214.63" y1="69.85" x2="224.79" y2="69.85" width="0.1524" layer="91"/>
<wire x1="224.79" y1="69.85" x2="224.79" y2="67.31" width="0.1524" layer="91"/>
<junction x="224.79" y="69.85"/>
<junction x="194.31" y="69.85"/>
<junction x="204.47" y="69.85"/>
<junction x="176.53" y="69.85"/>
<junction x="185.42" y="69.85"/>
<junction x="214.63" y="69.85"/>
<pinref part="C1" gate="G$1" pin="P$2"/>
<pinref part="C2" gate="G$1" pin="P$2"/>
<pinref part="C9" gate="G$1" pin="P$2"/>
<pinref part="R3" gate="G$1" pin="P$2"/>
<pinref part="C30" gate="G$1" pin="P$2"/>
<pinref part="C31" gate="G$1" pin="P$2"/>
</segment>
</net>
</nets>
</sheet>
<sheet>
<description>POWER</description>
<plain>
</plain>
<instances>
<instance part="BR1" gate="G$1" x="88.9" y="66.04" smashed="yes">
<attribute name="NAME" x="88.9" y="73.66" size="1.778" layer="95" align="center"/>
<attribute name="VALUE" x="88.9" y="58.42" size="1.778" layer="96" align="center"/>
</instance>
<instance part="C19" gate="G$1" x="106.68" y="58.42" smashed="yes" rot="R90">
<attribute name="VALUE" x="110.49" y="58.42" size="1.778" layer="96" rot="R90" align="center"/>
<attribute name="NAME" x="102.87" y="58.42" size="1.778" layer="95" rot="R90" align="center"/>
</instance>
<instance part="C20" gate="G$1" x="116.84" y="58.42" smashed="yes" rot="R90">
<attribute name="VALUE" x="120.65" y="58.42" size="1.778" layer="96" rot="R90" align="center"/>
<attribute name="NAME" x="113.03" y="58.42" size="1.778" layer="95" rot="R90" align="center"/>
</instance>
<instance part="C21" gate="G$1" x="127" y="58.42" smashed="yes" rot="R90">
<attribute name="VALUE" x="130.81" y="58.42" size="1.778" layer="96" rot="R90" align="center"/>
<attribute name="NAME" x="123.19" y="58.42" size="1.778" layer="95" rot="R90" align="center"/>
</instance>
<instance part="U2" gate="G$1" x="92.71" y="129.54" smashed="yes">
<attribute name="NAME" x="92.71" y="139.7" size="1.778" layer="95" align="center"/>
<attribute name="VALUE" x="92.71" y="119.38" size="1.778" layer="96" align="center"/>
</instance>
<instance part="C22" gate="G$1" x="57.15" y="124.46" smashed="yes" rot="R90">
<attribute name="VALUE" x="60.96" y="124.46" size="1.778" layer="96" rot="R90" align="center"/>
<attribute name="NAME" x="53.34" y="124.46" size="1.778" layer="95" rot="R90" align="center"/>
</instance>
<instance part="C23" gate="G$1" x="67.31" y="124.46" smashed="yes" rot="R90">
<attribute name="VALUE" x="71.12" y="124.46" size="1.778" layer="96" rot="R90" align="center"/>
<attribute name="NAME" x="63.5" y="124.46" size="1.778" layer="95" rot="R90" align="center"/>
</instance>
<instance part="R5" gate="G$1" x="105.41" y="144.78" smashed="yes" rot="R90">
<attribute name="NAME" x="102.87" y="144.78" size="1.778" layer="95" rot="R90" align="center"/>
<attribute name="VALUE" x="107.95" y="144.78" size="1.778" layer="96" rot="R90" align="center"/>
</instance>
<instance part="U$13" gate="G$1" x="57.15" y="109.22" smashed="yes"/>
<instance part="U$14" gate="G$1" x="57.15" y="137.16" smashed="yes"/>
<instance part="U3" gate="G$1" x="151.13" y="129.54" smashed="yes">
<attribute name="NAME" x="151.13" y="139.7" size="1.778" layer="95" align="center"/>
<attribute name="VALUE" x="151.13" y="119.38" size="1.778" layer="96" align="center"/>
</instance>
<instance part="C24" gate="G$1" x="115.57" y="124.46" smashed="yes" rot="R90">
<attribute name="VALUE" x="119.38" y="124.46" size="1.778" layer="96" rot="R90" align="center"/>
<attribute name="NAME" x="111.76" y="124.46" size="1.778" layer="95" rot="R90" align="center"/>
</instance>
<instance part="C25" gate="G$1" x="125.73" y="124.46" smashed="yes" rot="R90">
<attribute name="VALUE" x="129.54" y="124.46" size="1.778" layer="96" rot="R90" align="center"/>
<attribute name="NAME" x="121.92" y="124.46" size="1.778" layer="95" rot="R90" align="center"/>
</instance>
<instance part="R6" gate="G$1" x="163.83" y="144.78" smashed="yes" rot="R90">
<attribute name="NAME" x="161.29" y="144.78" size="1.778" layer="95" rot="R90" align="center"/>
<attribute name="VALUE" x="166.37" y="144.78" size="1.778" layer="96" rot="R90" align="center"/>
</instance>
<instance part="U$15" gate="G$1" x="115.57" y="109.22" smashed="yes"/>
<instance part="U$16" gate="G$1" x="115.57" y="137.16" smashed="yes"/>
<instance part="U4" gate="G$1" x="209.55" y="129.54" smashed="yes">
<attribute name="NAME" x="209.55" y="139.7" size="1.778" layer="95" align="center"/>
<attribute name="VALUE" x="209.55" y="119.38" size="1.778" layer="96" align="center"/>
</instance>
<instance part="C26" gate="G$1" x="173.99" y="124.46" smashed="yes" rot="R90">
<attribute name="VALUE" x="177.8" y="124.46" size="1.778" layer="96" rot="R90" align="center"/>
<attribute name="NAME" x="170.18" y="124.46" size="1.778" layer="95" rot="R90" align="center"/>
</instance>
<instance part="C27" gate="G$1" x="184.15" y="124.46" smashed="yes" rot="R90">
<attribute name="VALUE" x="187.96" y="124.46" size="1.778" layer="96" rot="R90" align="center"/>
<attribute name="NAME" x="180.34" y="124.46" size="1.778" layer="95" rot="R90" align="center"/>
</instance>
<instance part="R7" gate="G$1" x="222.25" y="144.78" smashed="yes" rot="R90">
<attribute name="NAME" x="219.71" y="144.78" size="1.778" layer="95" rot="R90" align="center"/>
<attribute name="VALUE" x="224.79" y="144.78" size="1.778" layer="96" rot="R90" align="center"/>
</instance>
<instance part="U$17" gate="G$1" x="173.99" y="109.22" smashed="yes"/>
<instance part="U$18" gate="G$1" x="173.99" y="137.16" smashed="yes"/>
<instance part="U$19" gate="G$1" x="101.6" y="38.1" smashed="yes"/>
<instance part="H1" gate="G$1" x="144.78" y="76.2" smashed="yes" rot="R90">
<attribute name="NAME" x="144.78" y="80.01" size="1.778" layer="95" rot="R180" align="center"/>
<attribute name="VALUE" x="139.7" y="82.55" size="1.778" layer="96" rot="R180" align="center"/>
</instance>
<instance part="H2" gate="G$1" x="165.1" y="76.2" smashed="yes" rot="R90">
<attribute name="NAME" x="165.1" y="80.01" size="1.778" layer="95" rot="R180" align="center"/>
<attribute name="VALUE" x="165.1" y="82.55" size="1.778" layer="96" rot="R180" align="center"/>
</instance>
<instance part="H3" gate="G$1" x="185.42" y="76.2" smashed="yes" rot="R90">
<attribute name="NAME" x="185.42" y="80.01" size="1.778" layer="95" rot="R180" align="center"/>
<attribute name="VALUE" x="190.5" y="82.55" size="1.778" layer="96" rot="R180" align="center"/>
</instance>
<instance part="Q1" gate="G$1" x="144.78" y="55.88" smashed="yes">
<attribute name="VALUE" x="151.13" y="55.88" size="1.778" layer="96" font="vector" rot="R90" align="center"/>
<attribute name="NAME" x="153.67" y="55.88" size="1.778" layer="95" font="vector" rot="R90" align="center"/>
</instance>
<instance part="Q2" gate="G$1" x="165.1" y="55.88" smashed="yes">
<attribute name="VALUE" x="171.45" y="55.88" size="1.778" layer="96" font="vector" rot="R90" align="center"/>
<attribute name="NAME" x="173.99" y="55.88" size="1.778" layer="95" font="vector" rot="R90" align="center"/>
</instance>
<instance part="Q3" gate="G$1" x="185.42" y="55.88" smashed="yes">
<attribute name="VALUE" x="191.77" y="55.88" size="1.778" layer="96" font="vector" rot="R90" align="center"/>
<attribute name="NAME" x="194.31" y="55.88" size="1.778" layer="95" font="vector" rot="R90" align="center"/>
</instance>
</instances>
<busses>
</busses>
<nets>
<net name="GND" class="0">
<segment>
<pinref part="U$13" gate="G$1" pin="GND"/>
<wire x1="57.15" y1="111.76" x2="57.15" y2="114.3" width="0.1524" layer="91"/>
<pinref part="U2" gate="G$1" pin="GND"/>
<wire x1="82.55" y1="129.54" x2="72.39" y2="129.54" width="0.1524" layer="91"/>
<wire x1="72.39" y1="129.54" x2="72.39" y2="114.3" width="0.1524" layer="91"/>
<wire x1="72.39" y1="114.3" x2="67.31" y2="114.3" width="0.1524" layer="91"/>
<wire x1="67.31" y1="114.3" x2="67.31" y2="116.84" width="0.1524" layer="91"/>
<wire x1="67.31" y1="114.3" x2="57.15" y2="114.3" width="0.1524" layer="91"/>
<wire x1="57.15" y1="114.3" x2="57.15" y2="116.84" width="0.1524" layer="91"/>
<pinref part="U2" gate="G$1" pin="IN-"/>
<wire x1="102.87" y1="124.46" x2="105.41" y2="124.46" width="0.1524" layer="91"/>
<wire x1="105.41" y1="124.46" x2="105.41" y2="114.3" width="0.1524" layer="91"/>
<wire x1="105.41" y1="114.3" x2="72.39" y2="114.3" width="0.1524" layer="91"/>
<junction x="72.39" y="114.3"/>
<junction x="67.31" y="114.3"/>
<junction x="57.15" y="114.3"/>
<pinref part="C22" gate="G$1" pin="P$1"/>
<pinref part="C23" gate="G$1" pin="P$1"/>
</segment>
<segment>
<pinref part="U$15" gate="G$1" pin="GND"/>
<wire x1="115.57" y1="111.76" x2="115.57" y2="114.3" width="0.1524" layer="91"/>
<pinref part="U3" gate="G$1" pin="GND"/>
<wire x1="140.97" y1="129.54" x2="130.81" y2="129.54" width="0.1524" layer="91"/>
<wire x1="130.81" y1="129.54" x2="130.81" y2="114.3" width="0.1524" layer="91"/>
<wire x1="130.81" y1="114.3" x2="125.73" y2="114.3" width="0.1524" layer="91"/>
<wire x1="125.73" y1="114.3" x2="125.73" y2="116.84" width="0.1524" layer="91"/>
<wire x1="125.73" y1="114.3" x2="115.57" y2="114.3" width="0.1524" layer="91"/>
<wire x1="115.57" y1="114.3" x2="115.57" y2="116.84" width="0.1524" layer="91"/>
<pinref part="U3" gate="G$1" pin="IN-"/>
<wire x1="161.29" y1="124.46" x2="163.83" y2="124.46" width="0.1524" layer="91"/>
<wire x1="163.83" y1="124.46" x2="163.83" y2="114.3" width="0.1524" layer="91"/>
<wire x1="163.83" y1="114.3" x2="130.81" y2="114.3" width="0.1524" layer="91"/>
<junction x="130.81" y="114.3"/>
<junction x="125.73" y="114.3"/>
<junction x="115.57" y="114.3"/>
<pinref part="C24" gate="G$1" pin="P$1"/>
<pinref part="C25" gate="G$1" pin="P$1"/>
</segment>
<segment>
<pinref part="U$17" gate="G$1" pin="GND"/>
<wire x1="173.99" y1="111.76" x2="173.99" y2="114.3" width="0.1524" layer="91"/>
<pinref part="U4" gate="G$1" pin="GND"/>
<wire x1="199.39" y1="129.54" x2="189.23" y2="129.54" width="0.1524" layer="91"/>
<wire x1="189.23" y1="129.54" x2="189.23" y2="114.3" width="0.1524" layer="91"/>
<wire x1="189.23" y1="114.3" x2="184.15" y2="114.3" width="0.1524" layer="91"/>
<wire x1="184.15" y1="114.3" x2="184.15" y2="116.84" width="0.1524" layer="91"/>
<wire x1="184.15" y1="114.3" x2="173.99" y2="114.3" width="0.1524" layer="91"/>
<wire x1="173.99" y1="114.3" x2="173.99" y2="116.84" width="0.1524" layer="91"/>
<pinref part="U4" gate="G$1" pin="IN-"/>
<wire x1="219.71" y1="124.46" x2="222.25" y2="124.46" width="0.1524" layer="91"/>
<wire x1="222.25" y1="124.46" x2="222.25" y2="114.3" width="0.1524" layer="91"/>
<wire x1="222.25" y1="114.3" x2="189.23" y2="114.3" width="0.1524" layer="91"/>
<junction x="189.23" y="114.3"/>
<junction x="184.15" y="114.3"/>
<junction x="173.99" y="114.3"/>
<pinref part="C26" gate="G$1" pin="P$1"/>
<pinref part="C27" gate="G$1" pin="P$1"/>
</segment>
<segment>
<wire x1="127" y1="43.18" x2="127" y2="50.8" width="0.1524" layer="91"/>
<pinref part="BR1" gate="G$1" pin="GND"/>
<wire x1="99.06" y1="63.5" x2="101.6" y2="63.5" width="0.1524" layer="91"/>
<wire x1="101.6" y1="63.5" x2="101.6" y2="43.18" width="0.1524" layer="91"/>
<wire x1="101.6" y1="43.18" x2="106.68" y2="43.18" width="0.1524" layer="91"/>
<wire x1="106.68" y1="43.18" x2="106.68" y2="50.8" width="0.1524" layer="91"/>
<pinref part="C19" gate="G$1" pin="-"/>
<wire x1="106.68" y1="43.18" x2="116.84" y2="43.18" width="0.1524" layer="91"/>
<wire x1="116.84" y1="43.18" x2="116.84" y2="50.8" width="0.1524" layer="91"/>
<pinref part="C20" gate="G$1" pin="-"/>
<wire x1="116.84" y1="43.18" x2="127" y2="43.18" width="0.1524" layer="91"/>
<pinref part="C21" gate="G$1" pin="-"/>
<junction x="106.68" y="43.18"/>
<junction x="116.84" y="43.18"/>
<wire x1="147.32" y1="45.72" x2="147.32" y2="43.18" width="0.1524" layer="91"/>
<wire x1="147.32" y1="43.18" x2="127" y2="43.18" width="0.1524" layer="91"/>
<junction x="127" y="43.18"/>
<wire x1="167.64" y1="45.72" x2="167.64" y2="43.18" width="0.1524" layer="91"/>
<wire x1="167.64" y1="43.18" x2="147.32" y2="43.18" width="0.1524" layer="91"/>
<junction x="147.32" y="43.18"/>
<wire x1="187.96" y1="45.72" x2="187.96" y2="43.18" width="0.1524" layer="91"/>
<wire x1="187.96" y1="43.18" x2="167.64" y2="43.18" width="0.1524" layer="91"/>
<junction x="167.64" y="43.18"/>
<wire x1="101.6" y1="43.18" x2="101.6" y2="40.64" width="0.1524" layer="91"/>
<junction x="101.6" y="43.18"/>
<pinref part="U$19" gate="G$1" pin="GND"/>
<pinref part="Q1" gate="G$1" pin="S"/>
<pinref part="Q2" gate="G$1" pin="S"/>
<pinref part="Q3" gate="G$1" pin="S"/>
</segment>
</net>
<net name="AC_L" class="0">
<segment>
<pinref part="BR1" gate="G$1" pin="AC(L)"/>
<wire x1="78.74" y1="68.58" x2="68.58" y2="68.58" width="0.1524" layer="91"/>
<label x="68.58" y="68.58" size="0.889" layer="95" rot="R180" xref="yes"/>
</segment>
</net>
<net name="AC_N" class="0">
<segment>
<pinref part="BR1" gate="G$1" pin="AC(N)"/>
<wire x1="78.74" y1="63.5" x2="68.58" y2="63.5" width="0.1524" layer="91"/>
<label x="68.58" y="63.5" size="0.889" layer="95" rot="R180" xref="yes"/>
</segment>
</net>
<net name="12V0" class="0">
<segment>
<pinref part="U$14" gate="G$1" pin="12V0"/>
<wire x1="57.15" y1="137.16" x2="57.15" y2="134.62" width="0.1524" layer="91"/>
<pinref part="U2" gate="G$1" pin="VDD"/>
<wire x1="82.55" y1="134.62" x2="67.31" y2="134.62" width="0.1524" layer="91"/>
<wire x1="67.31" y1="134.62" x2="67.31" y2="132.08" width="0.1524" layer="91"/>
<wire x1="67.31" y1="134.62" x2="57.15" y2="134.62" width="0.1524" layer="91"/>
<wire x1="57.15" y1="134.62" x2="57.15" y2="132.08" width="0.1524" layer="91"/>
<junction x="67.31" y="134.62"/>
<junction x="57.15" y="134.62"/>
<pinref part="C22" gate="G$1" pin="P$2"/>
<pinref part="C23" gate="G$1" pin="P$2"/>
</segment>
<segment>
<pinref part="U$16" gate="G$1" pin="12V0"/>
<wire x1="115.57" y1="137.16" x2="115.57" y2="134.62" width="0.1524" layer="91"/>
<pinref part="U3" gate="G$1" pin="VDD"/>
<wire x1="140.97" y1="134.62" x2="125.73" y2="134.62" width="0.1524" layer="91"/>
<wire x1="125.73" y1="134.62" x2="125.73" y2="132.08" width="0.1524" layer="91"/>
<wire x1="125.73" y1="134.62" x2="115.57" y2="134.62" width="0.1524" layer="91"/>
<wire x1="115.57" y1="134.62" x2="115.57" y2="132.08" width="0.1524" layer="91"/>
<junction x="125.73" y="134.62"/>
<junction x="115.57" y="134.62"/>
<pinref part="C24" gate="G$1" pin="P$2"/>
<pinref part="C25" gate="G$1" pin="P$2"/>
</segment>
<segment>
<pinref part="U$18" gate="G$1" pin="12V0"/>
<wire x1="173.99" y1="137.16" x2="173.99" y2="134.62" width="0.1524" layer="91"/>
<pinref part="U4" gate="G$1" pin="VDD"/>
<wire x1="199.39" y1="134.62" x2="184.15" y2="134.62" width="0.1524" layer="91"/>
<wire x1="184.15" y1="134.62" x2="184.15" y2="132.08" width="0.1524" layer="91"/>
<wire x1="184.15" y1="134.62" x2="173.99" y2="134.62" width="0.1524" layer="91"/>
<wire x1="173.99" y1="134.62" x2="173.99" y2="132.08" width="0.1524" layer="91"/>
<junction x="184.15" y="134.62"/>
<junction x="173.99" y="134.62"/>
<pinref part="C26" gate="G$1" pin="P$2"/>
<pinref part="C27" gate="G$1" pin="P$2"/>
</segment>
</net>
<net name="N$17" class="0">
<segment>
<pinref part="U2" gate="G$1" pin="OUT"/>
<wire x1="102.87" y1="134.62" x2="105.41" y2="134.62" width="0.1524" layer="91"/>
<wire x1="105.41" y1="134.62" x2="105.41" y2="137.16" width="0.1524" layer="91"/>
<pinref part="R5" gate="G$1" pin="P$1"/>
</segment>
</net>
<net name="LI1" class="0">
<segment>
<pinref part="U2" gate="G$1" pin="IN+"/>
<wire x1="82.55" y1="124.46" x2="77.47" y2="124.46" width="0.1524" layer="91"/>
<wire x1="77.47" y1="124.46" x2="77.47" y2="109.22" width="0.1524" layer="91"/>
<label x="77.47" y="109.22" size="0.889" layer="95" rot="R270" xref="yes"/>
</segment>
</net>
<net name="LO1" class="0">
<segment>
<wire x1="105.41" y1="152.4" x2="105.41" y2="157.48" width="0.1524" layer="91"/>
<label x="105.41" y="157.48" size="0.889" layer="95" rot="R90" xref="yes"/>
<pinref part="R5" gate="G$1" pin="P$2"/>
</segment>
<segment>
<wire x1="137.16" y1="55.88" x2="134.62" y2="55.88" width="0.1524" layer="91"/>
<wire x1="134.62" y1="55.88" x2="134.62" y2="35.56" width="0.1524" layer="91"/>
<label x="134.62" y="35.56" size="0.889" layer="95" rot="R270" xref="yes"/>
<pinref part="Q1" gate="G$1" pin="G"/>
</segment>
</net>
<net name="N$16" class="0">
<segment>
<pinref part="U3" gate="G$1" pin="OUT"/>
<wire x1="161.29" y1="134.62" x2="163.83" y2="134.62" width="0.1524" layer="91"/>
<wire x1="163.83" y1="134.62" x2="163.83" y2="137.16" width="0.1524" layer="91"/>
<pinref part="R6" gate="G$1" pin="P$1"/>
</segment>
</net>
<net name="LI2" class="0">
<segment>
<pinref part="U3" gate="G$1" pin="IN+"/>
<wire x1="140.97" y1="124.46" x2="135.89" y2="124.46" width="0.1524" layer="91"/>
<wire x1="135.89" y1="124.46" x2="135.89" y2="109.22" width="0.1524" layer="91"/>
<label x="135.89" y="109.22" size="0.889" layer="95" rot="R270" xref="yes"/>
</segment>
</net>
<net name="LO2" class="0">
<segment>
<wire x1="163.83" y1="152.4" x2="163.83" y2="157.48" width="0.1524" layer="91"/>
<label x="163.83" y="157.48" size="0.889" layer="95" rot="R90" xref="yes"/>
<pinref part="R6" gate="G$1" pin="P$2"/>
</segment>
<segment>
<wire x1="157.48" y1="55.88" x2="154.94" y2="55.88" width="0.1524" layer="91"/>
<wire x1="154.94" y1="55.88" x2="154.94" y2="35.56" width="0.1524" layer="91"/>
<label x="154.94" y="35.56" size="0.889" layer="95" rot="R270" xref="yes"/>
<pinref part="Q2" gate="G$1" pin="G"/>
</segment>
</net>
<net name="N$21" class="0">
<segment>
<pinref part="U4" gate="G$1" pin="OUT"/>
<wire x1="219.71" y1="134.62" x2="222.25" y2="134.62" width="0.1524" layer="91"/>
<wire x1="222.25" y1="134.62" x2="222.25" y2="137.16" width="0.1524" layer="91"/>
<pinref part="R7" gate="G$1" pin="P$1"/>
</segment>
</net>
<net name="LI3" class="0">
<segment>
<pinref part="U4" gate="G$1" pin="IN+"/>
<wire x1="199.39" y1="124.46" x2="194.31" y2="124.46" width="0.1524" layer="91"/>
<wire x1="194.31" y1="124.46" x2="194.31" y2="109.22" width="0.1524" layer="91"/>
<label x="194.31" y="109.22" size="0.889" layer="95" rot="R270" xref="yes"/>
</segment>
</net>
<net name="LO3" class="0">
<segment>
<wire x1="222.25" y1="152.4" x2="222.25" y2="157.48" width="0.1524" layer="91"/>
<label x="222.25" y="157.48" size="0.889" layer="95" rot="R90" xref="yes"/>
<pinref part="R7" gate="G$1" pin="P$2"/>
</segment>
<segment>
<wire x1="177.8" y1="55.88" x2="175.26" y2="55.88" width="0.1524" layer="91"/>
<wire x1="175.26" y1="55.88" x2="175.26" y2="35.56" width="0.1524" layer="91"/>
<label x="175.26" y="35.56" size="0.889" layer="95" rot="R270" xref="yes"/>
<pinref part="Q3" gate="G$1" pin="G"/>
</segment>
</net>
<net name="N$14" class="0">
<segment>
<pinref part="C21" gate="G$1" pin="+"/>
<wire x1="127" y1="66.04" x2="127" y2="68.58" width="0.1524" layer="91"/>
<pinref part="C20" gate="G$1" pin="+"/>
<wire x1="116.84" y1="68.58" x2="116.84" y2="66.04" width="0.1524" layer="91"/>
<wire x1="116.84" y1="68.58" x2="127" y2="68.58" width="0.1524" layer="91"/>
<junction x="116.84" y="68.58"/>
<pinref part="C19" gate="G$1" pin="+"/>
<wire x1="106.68" y1="68.58" x2="106.68" y2="66.04" width="0.1524" layer="91"/>
<wire x1="106.68" y1="68.58" x2="116.84" y2="68.58" width="0.1524" layer="91"/>
<junction x="106.68" y="68.58"/>
<pinref part="BR1" gate="G$1" pin="VOUT"/>
<wire x1="99.06" y1="68.58" x2="106.68" y2="68.58" width="0.1524" layer="91"/>
<wire x1="127" y1="68.58" x2="142.24" y2="68.58" width="0.1524" layer="91"/>
<wire x1="142.24" y1="68.58" x2="142.24" y2="71.12" width="0.1524" layer="91"/>
<junction x="127" y="68.58"/>
<wire x1="142.24" y1="68.58" x2="162.56" y2="68.58" width="0.1524" layer="91"/>
<wire x1="162.56" y1="68.58" x2="162.56" y2="71.12" width="0.1524" layer="91"/>
<junction x="142.24" y="68.58"/>
<wire x1="162.56" y1="68.58" x2="182.88" y2="68.58" width="0.1524" layer="91"/>
<wire x1="182.88" y1="68.58" x2="182.88" y2="71.12" width="0.1524" layer="91"/>
<junction x="162.56" y="68.58"/>
<pinref part="H1" gate="G$1" pin="1"/>
<pinref part="H2" gate="G$1" pin="1"/>
<pinref part="H3" gate="G$1" pin="1"/>
</segment>
</net>
<net name="N$1" class="0">
<segment>
<wire x1="147.32" y1="71.12" x2="147.32" y2="66.04" width="0.1524" layer="91"/>
<pinref part="H1" gate="G$1" pin="2"/>
<pinref part="Q1" gate="G$1" pin="D"/>
</segment>
</net>
<net name="N$5" class="0">
<segment>
<wire x1="167.64" y1="71.12" x2="167.64" y2="66.04" width="0.1524" layer="91"/>
<pinref part="H2" gate="G$1" pin="2"/>
<pinref part="Q2" gate="G$1" pin="D"/>
</segment>
</net>
<net name="N$12" class="0">
<segment>
<wire x1="187.96" y1="71.12" x2="187.96" y2="66.04" width="0.1524" layer="91"/>
<pinref part="H3" gate="G$1" pin="2"/>
<pinref part="Q3" gate="G$1" pin="D"/>
</segment>
</net>
</nets>
</sheet>
<sheet>
<description>LOGIC</description>
<plain>
<text x="6.35" y="71.12" size="2.54" layer="94">DIGITAL IO</text>
<text x="6.35" y="171.45" size="2.54" layer="94">PI PICO W</text>
<text x="179.07" y="171.45" size="2.54" layer="94">DISPLAY HEADERS</text>
<text x="127" y="71.12" size="2.54" layer="94">THERMOCOUPLE</text>
</plain>
<instances>
<instance part="RP2040" gate="G$1" x="114.3" y="124.46" smashed="yes">
<attribute name="NAME" x="114.3" y="149.86" size="1.778" layer="95" align="center"/>
<attribute name="VALUE" x="114.3" y="88.9" size="1.778" layer="96" align="center"/>
</instance>
<instance part="DISP1" gate="G$1" x="226.06" y="105.41" smashed="yes">
<attribute name="NAME" x="226.06" y="132.08" size="1.778" layer="95" align="center"/>
<attribute name="VALUE" x="226.06" y="76.2" size="1.778" layer="96" align="center"/>
</instance>
<instance part="U$1" gate="G$1" x="205.74" y="72.39" smashed="yes"/>
<instance part="U$23" gate="G$1" x="190.5" y="87.63" smashed="yes"/>
<instance part="D1" gate="G$1" x="48.26" y="104.14" smashed="yes" rot="R180">
<attribute name="NAME" x="48.26" y="97.79" size="1.778" layer="95" rot="R180" align="center"/>
<attribute name="VALUE" x="48.26" y="107.95" size="1.778" layer="95" rot="R180" align="center"/>
</instance>
<instance part="R8" gate="G$1" x="71.12" y="104.14" smashed="yes" rot="R180">
<attribute name="NAME" x="71.12" y="101.6" size="1.778" layer="95" rot="R180" align="center"/>
<attribute name="VALUE" x="71.12" y="106.68" size="1.778" layer="96" rot="R180" align="center"/>
</instance>
<instance part="D2" gate="G$1" x="48.26" y="116.84" smashed="yes" rot="R180">
<attribute name="NAME" x="48.26" y="110.49" size="1.778" layer="95" rot="R180" align="center"/>
<attribute name="VALUE" x="48.26" y="120.65" size="1.778" layer="95" rot="R180" align="center"/>
</instance>
<instance part="R9" gate="G$1" x="71.12" y="116.84" smashed="yes" rot="R180">
<attribute name="NAME" x="71.12" y="114.3" size="1.778" layer="95" rot="R180" align="center"/>
<attribute name="VALUE" x="71.12" y="119.38" size="1.778" layer="96" rot="R180" align="center"/>
</instance>
<instance part="U$10" gate="G$1" x="91.44" y="147.32" smashed="yes"/>
<instance part="U$11" gate="G$1" x="91.44" y="129.54" smashed="yes"/>
<instance part="U$24" gate="G$1" x="35.56" y="100.33" smashed="yes"/>
<instance part="C28" gate="G$1" x="35.56" y="142.24" smashed="yes" rot="R90">
<attribute name="VALUE" x="39.37" y="142.24" size="1.778" layer="96" rot="R90" align="center"/>
<attribute name="NAME" x="31.75" y="142.24" size="1.778" layer="95" rot="R90" align="center"/>
</instance>
<instance part="C29" gate="G$1" x="45.72" y="142.24" smashed="yes" rot="R90">
<attribute name="VALUE" x="49.53" y="142.24" size="1.778" layer="96" rot="R90" align="center"/>
<attribute name="NAME" x="41.91" y="142.24" size="1.778" layer="95" rot="R90" align="center"/>
</instance>
<instance part="U$25" gate="G$1" x="35.56" y="154.94" smashed="yes"/>
<instance part="U$26" gate="G$1" x="35.56" y="127" smashed="yes"/>
<instance part="H4" gate="G$1" x="20.32" y="22.86" smashed="yes" rot="R270">
<attribute name="NAME" x="20.32" y="19.05" size="1.778" layer="95" align="center"/>
<attribute name="VALUE" x="20.32" y="16.51" size="1.778" layer="95" align="center"/>
</instance>
<instance part="H5" gate="G$1" x="38.1" y="22.86" smashed="yes" rot="R270">
<attribute name="NAME" x="38.1" y="19.05" size="1.778" layer="95" align="center"/>
<attribute name="VALUE" x="38.1" y="16.51" size="1.778" layer="95" align="center"/>
</instance>
<instance part="H6" gate="G$1" x="55.88" y="22.86" smashed="yes" rot="R270">
<attribute name="NAME" x="55.88" y="19.05" size="1.778" layer="95" align="center"/>
<attribute name="VALUE" x="55.88" y="16.51" size="1.778" layer="95" align="center"/>
</instance>
<instance part="H7" gate="G$1" x="73.66" y="22.86" smashed="yes" rot="R270">
<attribute name="NAME" x="73.66" y="19.05" size="1.778" layer="95" align="center"/>
<attribute name="VALUE" x="73.66" y="16.51" size="1.778" layer="95" align="center"/>
</instance>
<instance part="H8" gate="G$1" x="91.44" y="22.86" smashed="yes" rot="R270">
<attribute name="NAME" x="91.44" y="19.05" size="1.778" layer="95" align="center"/>
<attribute name="VALUE" x="91.44" y="16.51" size="1.778" layer="95" align="center"/>
</instance>
<instance part="H9" gate="G$1" x="109.22" y="22.86" smashed="yes" rot="R270">
<attribute name="NAME" x="109.22" y="19.05" size="1.778" layer="95" align="center"/>
<attribute name="VALUE" x="109.22" y="16.51" size="1.778" layer="95" align="center"/>
</instance>
<instance part="R10" gate="G$1" x="22.86" y="43.18" smashed="yes" rot="R90">
<attribute name="NAME" x="20.32" y="43.18" size="1.778" layer="95" rot="R90" align="center"/>
<attribute name="VALUE" x="25.4" y="43.18" size="1.778" layer="96" rot="R90" align="center"/>
</instance>
<instance part="R11" gate="G$1" x="40.64" y="43.18" smashed="yes" rot="R90">
<attribute name="NAME" x="38.1" y="43.18" size="1.778" layer="95" rot="R90" align="center"/>
<attribute name="VALUE" x="43.18" y="43.18" size="1.778" layer="96" rot="R90" align="center"/>
</instance>
<instance part="R12" gate="G$1" x="58.42" y="43.18" smashed="yes" rot="R90">
<attribute name="NAME" x="55.88" y="43.18" size="1.778" layer="95" rot="R90" align="center"/>
<attribute name="VALUE" x="60.96" y="43.18" size="1.778" layer="96" rot="R90" align="center"/>
</instance>
<instance part="R13" gate="G$1" x="76.2" y="43.18" smashed="yes" rot="R90">
<attribute name="NAME" x="73.66" y="43.18" size="1.778" layer="95" rot="R90" align="center"/>
<attribute name="VALUE" x="78.74" y="43.18" size="1.778" layer="96" rot="R90" align="center"/>
</instance>
<instance part="R14" gate="G$1" x="93.98" y="43.18" smashed="yes" rot="R90">
<attribute name="NAME" x="91.44" y="43.18" size="1.778" layer="95" rot="R90" align="center"/>
<attribute name="VALUE" x="96.52" y="43.18" size="1.778" layer="96" rot="R90" align="center"/>
</instance>
<instance part="R15" gate="G$1" x="111.76" y="43.18" smashed="yes" rot="R90">
<attribute name="NAME" x="109.22" y="43.18" size="1.778" layer="95" rot="R90" align="center"/>
<attribute name="VALUE" x="114.3" y="43.18" size="1.778" layer="96" rot="R90" align="center"/>
</instance>
<instance part="U$4" gate="G$1" x="12.7" y="27.94" smashed="yes"/>
<instance part="U$5" gate="G$1" x="81.28" y="147.32" smashed="yes"/>
<instance part="U$6" gate="G$1" x="119.38" y="35.56" smashed="yes"/>
<instance part="H10" gate="G$1" x="144.78" y="53.34" smashed="yes" rot="R180">
<attribute name="NAME" x="140.97" y="53.34" size="1.778" layer="95" rot="R270" align="center"/>
<attribute name="VALUE" x="138.43" y="53.34" size="1.778" layer="95" rot="R270" align="center"/>
</instance>
<instance part="H11" gate="G$1" x="144.78" y="35.56" smashed="yes" rot="R180">
<attribute name="NAME" x="140.97" y="35.56" size="1.778" layer="95" rot="R270" align="center"/>
<attribute name="VALUE" x="138.43" y="35.56" size="1.778" layer="95" rot="R270" align="center"/>
</instance>
<instance part="H12" gate="G$1" x="144.78" y="17.78" smashed="yes" rot="R180">
<attribute name="NAME" x="140.97" y="17.78" size="1.778" layer="95" rot="R270" align="center"/>
<attribute name="VALUE" x="138.43" y="17.78" size="1.778" layer="95" rot="R270" align="center"/>
</instance>
<instance part="R16" gate="G$1" x="149.86" y="142.24" smashed="yes" rot="R90">
<attribute name="NAME" x="147.32" y="142.24" size="1.778" layer="95" rot="R90" align="center"/>
<attribute name="VALUE" x="152.4" y="142.24" size="1.778" layer="96" rot="R90" align="center"/>
</instance>
<instance part="U$31" gate="G$1" x="149.86" y="152.4" smashed="yes"/>
</instances>
<busses>
</busses>
<nets>
<net name="SPI_TX" class="0">
<segment>
<pinref part="RP2040" gate="G$1" pin="25"/>
<wire x1="129.54" y1="121.92" x2="139.7" y2="121.92" width="0.1524" layer="91"/>
<label x="139.7" y="121.92" size="0.889" layer="95" xref="yes"/>
</segment>
<segment>
<pinref part="DISP1" gate="G$1" pin="MOSI"/>
<wire x1="210.82" y1="92.71" x2="200.66" y2="92.71" width="0.1524" layer="91"/>
<label x="200.66" y="92.71" size="0.889" layer="95" rot="R180" xref="yes"/>
</segment>
</net>
<net name="SPI_RX" class="0">
<segment>
<pinref part="RP2040" gate="G$1" pin="21"/>
<wire x1="129.54" y1="111.76" x2="139.7" y2="111.76" width="0.1524" layer="91"/>
<label x="139.7" y="111.76" size="0.889" layer="95" xref="yes"/>
</segment>
<segment>
<pinref part="DISP1" gate="G$1" pin="MISO"/>
<wire x1="210.82" y1="90.17" x2="200.66" y2="90.17" width="0.1524" layer="91"/>
<label x="200.66" y="90.17" size="0.889" layer="95" rot="R180" xref="yes"/>
</segment>
</net>
<net name="SPI_CS" class="0">
<segment>
<pinref part="RP2040" gate="G$1" pin="22"/>
<wire x1="129.54" y1="114.3" x2="139.7" y2="114.3" width="0.1524" layer="91"/>
<label x="139.7" y="114.3" size="0.889" layer="95" xref="yes"/>
</segment>
<segment>
<pinref part="DISP1" gate="G$1" pin="CS"/>
<wire x1="210.82" y1="95.25" x2="200.66" y2="95.25" width="0.1524" layer="91"/>
<label x="200.66" y="95.25" size="0.889" layer="95" rot="R180" xref="yes"/>
</segment>
</net>
<net name="SPI_DS" class="0">
<segment>
<pinref part="RP2040" gate="G$1" pin="26"/>
<wire x1="129.54" y1="124.46" x2="139.7" y2="124.46" width="0.1524" layer="91"/>
<label x="139.7" y="124.46" size="0.889" layer="95" xref="yes"/>
</segment>
<segment>
<pinref part="DISP1" gate="G$1" pin="D/C"/>
<wire x1="210.82" y1="97.79" x2="200.66" y2="97.79" width="0.1524" layer="91"/>
<label x="200.66" y="97.79" size="0.889" layer="95" rot="R180" xref="yes"/>
</segment>
<segment>
<pinref part="DISP1" gate="G$1" pin="X+"/>
<wire x1="210.82" y1="107.95" x2="200.66" y2="107.95" width="0.1524" layer="91"/>
<label x="200.66" y="107.95" size="0.889" layer="95" rot="R180" xref="yes"/>
</segment>
</net>
<net name="SPI_CLK" class="0">
<segment>
<pinref part="DISP1" gate="G$1" pin="CLK"/>
<wire x1="210.82" y1="87.63" x2="200.66" y2="87.63" width="0.1524" layer="91"/>
<label x="200.66" y="87.63" size="0.889" layer="95" rot="R180" xref="yes"/>
</segment>
<segment>
<pinref part="RP2040" gate="G$1" pin="24"/>
<wire x1="129.54" y1="119.38" x2="139.7" y2="119.38" width="0.1524" layer="91"/>
<label x="139.7" y="119.38" size="0.889" layer="95" xref="yes"/>
</segment>
</net>
<net name="GND" class="0">
<segment>
<pinref part="DISP1" gate="G$1" pin="GND"/>
<wire x1="210.82" y1="80.01" x2="205.74" y2="80.01" width="0.1524" layer="91"/>
<wire x1="205.74" y1="80.01" x2="205.74" y2="74.93" width="0.1524" layer="91"/>
<pinref part="U$1" gate="G$1" pin="GND"/>
</segment>
<segment>
<pinref part="RP2040" gate="G$1" pin="GND"/>
<wire x1="99.06" y1="139.7" x2="91.44" y2="139.7" width="0.1524" layer="91"/>
<wire x1="91.44" y1="139.7" x2="91.44" y2="137.16" width="0.1524" layer="91"/>
<pinref part="U$11" gate="G$1" pin="GND"/>
<pinref part="RP2040" gate="G$1" pin="AGND"/>
<wire x1="91.44" y1="137.16" x2="91.44" y2="132.08" width="0.1524" layer="91"/>
<wire x1="99.06" y1="137.16" x2="91.44" y2="137.16" width="0.1524" layer="91"/>
<junction x="91.44" y="137.16"/>
</segment>
<segment>
<pinref part="D2" gate="G$1" pin="VSS"/>
<wire x1="40.64" y1="116.84" x2="35.56" y2="116.84" width="0.1524" layer="91"/>
<wire x1="35.56" y1="116.84" x2="35.56" y2="104.14" width="0.1524" layer="91"/>
<wire x1="35.56" y1="104.14" x2="40.64" y2="104.14" width="0.1524" layer="91"/>
<pinref part="D1" gate="G$1" pin="VSS"/>
<pinref part="U$24" gate="G$1" pin="GND"/>
<wire x1="35.56" y1="104.14" x2="35.56" y2="102.87" width="0.1524" layer="91"/>
</segment>
<segment>
<wire x1="35.56" y1="134.62" x2="35.56" y2="132.08" width="0.1524" layer="91"/>
<wire x1="35.56" y1="132.08" x2="45.72" y2="132.08" width="0.1524" layer="91"/>
<wire x1="45.72" y1="132.08" x2="45.72" y2="134.62" width="0.1524" layer="91"/>
<wire x1="35.56" y1="132.08" x2="35.56" y2="129.54" width="0.1524" layer="91"/>
<junction x="35.56" y="132.08"/>
<pinref part="U$26" gate="G$1" pin="GND"/>
<pinref part="C28" gate="G$1" pin="P$1"/>
<pinref part="C29" gate="G$1" pin="P$1"/>
</segment>
<segment>
<wire x1="22.86" y1="35.56" x2="22.86" y2="33.02" width="0.1524" layer="91"/>
<wire x1="22.86" y1="33.02" x2="40.64" y2="33.02" width="0.1524" layer="91"/>
<wire x1="40.64" y1="33.02" x2="40.64" y2="35.56" width="0.1524" layer="91"/>
<wire x1="40.64" y1="33.02" x2="58.42" y2="33.02" width="0.1524" layer="91"/>
<wire x1="58.42" y1="33.02" x2="58.42" y2="35.56" width="0.1524" layer="91"/>
<wire x1="58.42" y1="33.02" x2="76.2" y2="33.02" width="0.1524" layer="91"/>
<wire x1="76.2" y1="33.02" x2="76.2" y2="35.56" width="0.1524" layer="91"/>
<wire x1="76.2" y1="33.02" x2="93.98" y2="33.02" width="0.1524" layer="91"/>
<wire x1="93.98" y1="33.02" x2="93.98" y2="35.56" width="0.1524" layer="91"/>
<wire x1="93.98" y1="33.02" x2="111.76" y2="33.02" width="0.1524" layer="91"/>
<wire x1="111.76" y1="33.02" x2="111.76" y2="35.56" width="0.1524" layer="91"/>
<wire x1="22.86" y1="33.02" x2="12.7" y2="33.02" width="0.1524" layer="91"/>
<wire x1="12.7" y1="33.02" x2="12.7" y2="30.48" width="0.1524" layer="91"/>
<pinref part="U$4" gate="G$1" pin="GND"/>
<junction x="22.86" y="33.02"/>
<junction x="40.64" y="33.02"/>
<junction x="58.42" y="33.02"/>
<junction x="76.2" y="33.02"/>
<junction x="93.98" y="33.02"/>
<pinref part="R10" gate="G$1" pin="P$1"/>
<pinref part="R11" gate="G$1" pin="P$1"/>
<pinref part="R12" gate="G$1" pin="P$1"/>
<pinref part="R13" gate="G$1" pin="P$1"/>
<pinref part="R14" gate="G$1" pin="P$1"/>
<pinref part="R15" gate="G$1" pin="P$1"/>
</segment>
</net>
<net name="3V3" class="0">
<segment>
<pinref part="DISP1" gate="G$1" pin="3-5V"/>
<wire x1="210.82" y1="82.55" x2="190.5" y2="82.55" width="0.1524" layer="91"/>
<wire x1="190.5" y1="82.55" x2="190.5" y2="87.63" width="0.1524" layer="91"/>
<pinref part="U$23" gate="G$1" pin="3V3"/>
</segment>
<segment>
<pinref part="RP2040" gate="G$1" pin="3V3_OUT"/>
<wire x1="99.06" y1="127" x2="96.52" y2="127" width="0.1524" layer="91"/>
<wire x1="96.52" y1="127" x2="96.52" y2="124.46" width="0.1524" layer="91"/>
<wire x1="96.52" y1="124.46" x2="81.28" y2="124.46" width="0.1524" layer="91"/>
<wire x1="81.28" y1="124.46" x2="81.28" y2="147.32" width="0.1524" layer="91"/>
<pinref part="U$5" gate="G$1" pin="3V3"/>
</segment>
<segment>
<pinref part="H4" gate="G$1" pin="1"/>
<wire x1="22.86" y1="27.94" x2="22.86" y2="30.48" width="0.1524" layer="91"/>
<wire x1="22.86" y1="30.48" x2="40.64" y2="30.48" width="0.1524" layer="91"/>
<wire x1="40.64" y1="30.48" x2="40.64" y2="27.94" width="0.1524" layer="91"/>
<pinref part="H5" gate="G$1" pin="1"/>
<wire x1="40.64" y1="30.48" x2="58.42" y2="30.48" width="0.1524" layer="91"/>
<wire x1="58.42" y1="30.48" x2="58.42" y2="27.94" width="0.1524" layer="91"/>
<pinref part="H6" gate="G$1" pin="1"/>
<wire x1="58.42" y1="30.48" x2="76.2" y2="30.48" width="0.1524" layer="91"/>
<wire x1="76.2" y1="30.48" x2="76.2" y2="27.94" width="0.1524" layer="91"/>
<pinref part="H7" gate="G$1" pin="1"/>
<wire x1="76.2" y1="30.48" x2="93.98" y2="30.48" width="0.1524" layer="91"/>
<wire x1="93.98" y1="30.48" x2="93.98" y2="27.94" width="0.1524" layer="91"/>
<pinref part="H8" gate="G$1" pin="1"/>
<wire x1="93.98" y1="30.48" x2="111.76" y2="30.48" width="0.1524" layer="91"/>
<wire x1="111.76" y1="30.48" x2="111.76" y2="27.94" width="0.1524" layer="91"/>
<pinref part="H9" gate="G$1" pin="1"/>
<wire x1="111.76" y1="30.48" x2="119.38" y2="30.48" width="0.1524" layer="91"/>
<wire x1="119.38" y1="30.48" x2="119.38" y2="35.56" width="0.1524" layer="91"/>
<pinref part="U$6" gate="G$1" pin="3V3"/>
<junction x="40.64" y="30.48"/>
<junction x="58.42" y="30.48"/>
<junction x="76.2" y="30.48"/>
<junction x="93.98" y="30.48"/>
<junction x="111.76" y="30.48"/>
</segment>
<segment>
<pinref part="U$31" gate="G$1" pin="3V3"/>
<wire x1="149.86" y1="152.4" x2="149.86" y2="149.86" width="0.1524" layer="91" style="longdash"/>
<pinref part="R16" gate="G$1" pin="P$2"/>
</segment>
</net>
<net name="X-" class="0">
<segment>
<pinref part="DISP1" gate="G$1" pin="X-"/>
<wire x1="210.82" y1="113.03" x2="200.66" y2="113.03" width="0.1524" layer="91"/>
<label x="200.66" y="113.03" size="0.889" layer="95" rot="R180" xref="yes"/>
</segment>
<segment>
<pinref part="RP2040" gate="G$1" pin="32"/>
<wire x1="129.54" y1="137.16" x2="139.7" y2="137.16" width="0.1524" layer="91"/>
<label x="139.7" y="137.16" size="0.889" layer="95" xref="yes"/>
</segment>
</net>
<net name="Y-" class="0">
<segment>
<pinref part="DISP1" gate="G$1" pin="Y-"/>
<wire x1="210.82" y1="110.49" x2="200.66" y2="110.49" width="0.1524" layer="91"/>
<label x="200.66" y="110.49" size="0.889" layer="95" rot="R180" xref="yes"/>
</segment>
<segment>
<pinref part="RP2040" gate="G$1" pin="27"/>
<wire x1="129.54" y1="127" x2="139.7" y2="127" width="0.1524" layer="91"/>
<label x="139.7" y="127" size="0.889" layer="95" xref="yes"/>
</segment>
</net>
<net name="Y+" class="0">
<segment>
<pinref part="DISP1" gate="G$1" pin="Y+"/>
<wire x1="210.82" y1="105.41" x2="200.66" y2="105.41" width="0.1524" layer="91"/>
<label x="200.66" y="105.41" size="0.889" layer="95" rot="R180" xref="yes"/>
</segment>
<segment>
<pinref part="RP2040" gate="G$1" pin="31"/>
<wire x1="129.54" y1="134.62" x2="139.7" y2="134.62" width="0.1524" layer="91"/>
<label x="139.7" y="134.62" size="0.889" layer="95" xref="yes"/>
</segment>
</net>
<net name="N$7" class="0">
<segment>
<pinref part="D1" gate="G$1" pin="VDD"/>
<wire x1="55.88" y1="104.14" x2="63.5" y2="104.14" width="0.1524" layer="91"/>
<pinref part="R8" gate="G$1" pin="P$2"/>
</segment>
</net>
<net name="N$13" class="0">
<segment>
<pinref part="D2" gate="G$1" pin="VDD"/>
<wire x1="55.88" y1="116.84" x2="63.5" y2="116.84" width="0.1524" layer="91"/>
<pinref part="R9" gate="G$1" pin="P$2"/>
</segment>
</net>
<net name="N$15" class="0">
<segment>
<pinref part="RP2040" gate="G$1" pin="5"/>
<wire x1="99.06" y1="111.76" x2="81.28" y2="111.76" width="0.1524" layer="91"/>
<wire x1="81.28" y1="111.76" x2="81.28" y2="104.14" width="0.1524" layer="91"/>
<wire x1="81.28" y1="104.14" x2="78.74" y2="104.14" width="0.1524" layer="91"/>
<pinref part="R8" gate="G$1" pin="P$1"/>
</segment>
</net>
<net name="N$18" class="0">
<segment>
<pinref part="RP2040" gate="G$1" pin="4"/>
<wire x1="99.06" y1="116.84" x2="78.74" y2="116.84" width="0.1524" layer="91"/>
<pinref part="R9" gate="G$1" pin="P$1"/>
</segment>
</net>
<net name="4V0" class="0">
<segment>
<pinref part="RP2040" gate="G$1" pin="VSYS"/>
<wire x1="99.06" y1="142.24" x2="91.44" y2="142.24" width="0.1524" layer="91"/>
<wire x1="91.44" y1="142.24" x2="91.44" y2="147.32" width="0.1524" layer="91"/>
<pinref part="U$10" gate="G$1" pin="4V0"/>
</segment>
<segment>
<pinref part="U$25" gate="G$1" pin="4V0"/>
<wire x1="35.56" y1="154.94" x2="35.56" y2="152.4" width="0.1524" layer="91"/>
<wire x1="35.56" y1="149.86" x2="35.56" y2="152.4" width="0.1524" layer="91"/>
<wire x1="35.56" y1="152.4" x2="45.72" y2="152.4" width="0.1524" layer="91"/>
<wire x1="45.72" y1="152.4" x2="45.72" y2="149.86" width="0.1524" layer="91"/>
<junction x="35.56" y="152.4"/>
<pinref part="C28" gate="G$1" pin="P$2"/>
<pinref part="C29" gate="G$1" pin="P$2"/>
</segment>
</net>
<net name="LI1" class="0">
<segment>
<pinref part="RP2040" gate="G$1" pin="14"/>
<wire x1="129.54" y1="93.98" x2="139.7" y2="93.98" width="0.1524" layer="91"/>
<label x="139.7" y="93.98" size="0.889" layer="95" xref="yes"/>
</segment>
</net>
<net name="LI2" class="0">
<segment>
<pinref part="RP2040" gate="G$1" pin="15"/>
<wire x1="129.54" y1="96.52" x2="139.7" y2="96.52" width="0.1524" layer="91"/>
<label x="139.7" y="96.52" size="0.889" layer="95" xref="yes"/>
</segment>
</net>
<net name="LI3" class="0">
<segment>
<pinref part="RP2040" gate="G$1" pin="16"/>
<wire x1="129.54" y1="99.06" x2="139.7" y2="99.06" width="0.1524" layer="91"/>
<label x="139.7" y="99.06" size="0.889" layer="95" xref="yes"/>
</segment>
</net>
<net name="D1" class="0">
<segment>
<pinref part="RP2040" gate="G$1" pin="6"/>
<wire x1="99.06" y1="109.22" x2="83.82" y2="109.22" width="0.1524" layer="91"/>
<wire x1="83.82" y1="109.22" x2="83.82" y2="99.06" width="0.1524" layer="91"/>
<wire x1="83.82" y1="99.06" x2="73.66" y2="99.06" width="0.1524" layer="91"/>
<label x="73.66" y="99.06" size="0.889" layer="95" rot="R180" xref="yes"/>
</segment>
<segment>
<pinref part="H4" gate="G$1" pin="2"/>
<wire x1="17.78" y1="27.94" x2="17.78" y2="53.34" width="0.1524" layer="91"/>
<wire x1="17.78" y1="53.34" x2="22.86" y2="53.34" width="0.1524" layer="91"/>
<wire x1="22.86" y1="53.34" x2="22.86" y2="50.8" width="0.1524" layer="91"/>
<wire x1="17.78" y1="53.34" x2="17.78" y2="58.42" width="0.1524" layer="91"/>
<junction x="17.78" y="53.34"/>
<label x="17.78" y="58.42" size="0.889" layer="95" rot="R90" xref="yes"/>
<pinref part="R10" gate="G$1" pin="P$2"/>
</segment>
</net>
<net name="D2" class="0">
<segment>
<pinref part="RP2040" gate="G$1" pin="7"/>
<wire x1="99.06" y1="106.68" x2="86.36" y2="106.68" width="0.1524" layer="91"/>
<wire x1="86.36" y1="106.68" x2="86.36" y2="96.52" width="0.1524" layer="91"/>
<wire x1="86.36" y1="96.52" x2="73.66" y2="96.52" width="0.1524" layer="91"/>
<label x="73.66" y="96.52" size="0.889" layer="95" rot="R180" xref="yes"/>
</segment>
<segment>
<pinref part="H5" gate="G$1" pin="2"/>
<wire x1="35.56" y1="27.94" x2="35.56" y2="53.34" width="0.1524" layer="91"/>
<wire x1="35.56" y1="53.34" x2="40.64" y2="53.34" width="0.1524" layer="91"/>
<wire x1="40.64" y1="53.34" x2="40.64" y2="50.8" width="0.1524" layer="91"/>
<wire x1="35.56" y1="53.34" x2="35.56" y2="58.42" width="0.1524" layer="91"/>
<junction x="35.56" y="53.34"/>
<label x="35.56" y="58.42" size="0.889" layer="95" rot="R90" xref="yes"/>
<pinref part="R11" gate="G$1" pin="P$2"/>
</segment>
</net>
<net name="D3" class="0">
<segment>
<pinref part="RP2040" gate="G$1" pin="9"/>
<wire x1="99.06" y1="101.6" x2="88.9" y2="101.6" width="0.1524" layer="91"/>
<wire x1="88.9" y1="101.6" x2="88.9" y2="93.98" width="0.1524" layer="91"/>
<wire x1="88.9" y1="93.98" x2="73.66" y2="93.98" width="0.1524" layer="91"/>
<label x="73.66" y="93.98" size="0.889" layer="95" rot="R180" xref="yes"/>
</segment>
<segment>
<pinref part="H6" gate="G$1" pin="2"/>
<wire x1="53.34" y1="27.94" x2="53.34" y2="53.34" width="0.1524" layer="91"/>
<wire x1="53.34" y1="53.34" x2="58.42" y2="53.34" width="0.1524" layer="91"/>
<wire x1="58.42" y1="53.34" x2="58.42" y2="50.8" width="0.1524" layer="91"/>
<wire x1="53.34" y1="53.34" x2="53.34" y2="58.42" width="0.1524" layer="91"/>
<junction x="53.34" y="53.34"/>
<label x="53.34" y="58.42" size="0.889" layer="95" rot="R90" xref="yes"/>
<pinref part="R12" gate="G$1" pin="P$2"/>
</segment>
</net>
<net name="D4" class="0">
<segment>
<pinref part="RP2040" gate="G$1" pin="10"/>
<wire x1="99.06" y1="99.06" x2="91.44" y2="99.06" width="0.1524" layer="91"/>
<wire x1="91.44" y1="99.06" x2="91.44" y2="91.44" width="0.1524" layer="91"/>
<wire x1="91.44" y1="91.44" x2="73.66" y2="91.44" width="0.1524" layer="91"/>
<label x="73.66" y="91.44" size="0.889" layer="95" rot="R180" xref="yes"/>
</segment>
<segment>
<pinref part="H7" gate="G$1" pin="2"/>
<wire x1="71.12" y1="27.94" x2="71.12" y2="53.34" width="0.1524" layer="91"/>
<wire x1="71.12" y1="53.34" x2="76.2" y2="53.34" width="0.1524" layer="91"/>
<wire x1="76.2" y1="53.34" x2="76.2" y2="50.8" width="0.1524" layer="91"/>
<wire x1="71.12" y1="53.34" x2="71.12" y2="58.42" width="0.1524" layer="91"/>
<junction x="71.12" y="53.34"/>
<label x="71.12" y="58.42" size="0.889" layer="95" rot="R90" xref="yes"/>
<pinref part="R13" gate="G$1" pin="P$2"/>
</segment>
</net>
<net name="D5" class="0">
<segment>
<pinref part="RP2040" gate="G$1" pin="11"/>
<wire x1="99.06" y1="96.52" x2="93.98" y2="96.52" width="0.1524" layer="91"/>
<wire x1="93.98" y1="96.52" x2="93.98" y2="88.9" width="0.1524" layer="91"/>
<wire x1="73.66" y1="88.9" x2="93.98" y2="88.9" width="0.1524" layer="91"/>
<label x="73.66" y="88.9" size="0.889" layer="95" rot="R180" xref="yes"/>
</segment>
<segment>
<pinref part="H8" gate="G$1" pin="2"/>
<wire x1="88.9" y1="27.94" x2="88.9" y2="53.34" width="0.1524" layer="91"/>
<wire x1="88.9" y1="53.34" x2="93.98" y2="53.34" width="0.1524" layer="91"/>
<wire x1="93.98" y1="53.34" x2="93.98" y2="50.8" width="0.1524" layer="91"/>
<wire x1="88.9" y1="53.34" x2="88.9" y2="58.42" width="0.1524" layer="91"/>
<junction x="88.9" y="53.34"/>
<label x="88.9" y="58.42" size="0.889" layer="95" rot="R90" xref="yes"/>
<pinref part="R14" gate="G$1" pin="P$2"/>
</segment>
</net>
<net name="D6" class="0">
<segment>
<pinref part="RP2040" gate="G$1" pin="12"/>
<wire x1="99.06" y1="93.98" x2="96.52" y2="93.98" width="0.1524" layer="91"/>
<wire x1="96.52" y1="93.98" x2="96.52" y2="86.36" width="0.1524" layer="91"/>
<wire x1="96.52" y1="86.36" x2="73.66" y2="86.36" width="0.1524" layer="91"/>
<label x="73.66" y="86.36" size="0.889" layer="95" rot="R180" xref="yes"/>
</segment>
<segment>
<pinref part="H9" gate="G$1" pin="2"/>
<wire x1="106.68" y1="27.94" x2="106.68" y2="53.34" width="0.1524" layer="91"/>
<wire x1="106.68" y1="53.34" x2="111.76" y2="53.34" width="0.1524" layer="91"/>
<wire x1="111.76" y1="53.34" x2="111.76" y2="50.8" width="0.1524" layer="91"/>
<wire x1="106.68" y1="53.34" x2="106.68" y2="58.42" width="0.1524" layer="91"/>
<junction x="106.68" y="53.34"/>
<label x="106.68" y="58.42" size="0.889" layer="95" rot="R90" xref="yes"/>
<pinref part="R15" gate="G$1" pin="P$2"/>
</segment>
</net>
<net name="1WS_DATA" class="0">
<segment>
<pinref part="RP2040" gate="G$1" pin="29"/>
<wire x1="129.54" y1="132.08" x2="149.86" y2="132.08" width="0.1524" layer="91"/>
<label x="154.94" y="132.08" size="0.889" layer="95" xref="yes"/>
<wire x1="149.86" y1="132.08" x2="154.94" y2="132.08" width="0.1524" layer="91"/>
<wire x1="149.86" y1="134.62" x2="149.86" y2="132.08" width="0.1524" layer="91" style="longdash"/>
<junction x="149.86" y="132.08"/>
<pinref part="R16" gate="G$1" pin="P$1"/>
</segment>
</net>
<net name="T1+" class="0">
<segment>
<pinref part="H10" gate="G$1" pin="2"/>
<wire x1="149.86" y1="55.88" x2="160.02" y2="55.88" width="0.1524" layer="91" style="longdash"/>
<label x="160.02" y="55.88" size="0.889" layer="95" xref="yes"/>
</segment>
</net>
<net name="T1-" class="0">
<segment>
<pinref part="H10" gate="G$1" pin="1"/>
<wire x1="149.86" y1="50.8" x2="160.02" y2="50.8" width="0.1524" layer="91" style="longdash"/>
<label x="160.02" y="50.8" size="0.889" layer="95" xref="yes"/>
</segment>
</net>
<net name="T2-" class="0">
<segment>
<pinref part="H11" gate="G$1" pin="1"/>
<wire x1="149.86" y1="33.02" x2="160.02" y2="33.02" width="0.1524" layer="91" style="longdash"/>
<label x="160.02" y="33.02" size="0.889" layer="95" xref="yes"/>
</segment>
</net>
<net name="T2+" class="0">
<segment>
<pinref part="H11" gate="G$1" pin="2"/>
<wire x1="149.86" y1="38.1" x2="160.02" y2="38.1" width="0.1524" layer="91" style="longdash"/>
<label x="160.02" y="38.1" size="0.889" layer="95" xref="yes"/>
</segment>
</net>
<net name="T3+" class="0">
<segment>
<pinref part="H12" gate="G$1" pin="2"/>
<wire x1="149.86" y1="20.32" x2="160.02" y2="20.32" width="0.1524" layer="91" style="longdash"/>
<label x="160.02" y="20.32" size="0.889" layer="95" xref="yes"/>
</segment>
</net>
<net name="T3-" class="0">
<segment>
<pinref part="H12" gate="G$1" pin="1"/>
<wire x1="149.86" y1="15.24" x2="160.02" y2="15.24" width="0.1524" layer="91" style="longdash"/>
<label x="160.02" y="15.24" size="0.889" layer="95" xref="yes"/>
</segment>
</net>
</nets>
</sheet>
<sheet>
<description>THERMOCOUPLE ADC</description>
<plain>
<text x="5.08" y="172.72" size="2.54" layer="94">THERMOCOUPLE ADC</text>
</plain>
<instances>
<instance part="U5" gate="G$1" x="213.36" y="107.95" smashed="yes" rot="R90">
<attribute name="NAME" x="200.66" y="107.95" size="1.778" layer="95" rot="R90" align="center"/>
<attribute name="VALUE" x="226.06" y="107.95" size="1.778" layer="96" rot="R90" align="center"/>
</instance>
<instance part="C32" gate="G$1" x="198.12" y="125.73" smashed="yes" rot="R180">
<attribute name="VALUE" x="198.12" y="129.54" size="1.778" layer="96" rot="R180" align="center"/>
<attribute name="NAME" x="198.12" y="121.92" size="1.778" layer="95" rot="R180" align="center"/>
</instance>
<instance part="C33" gate="G$1" x="198.12" y="90.17" smashed="yes" rot="R180">
<attribute name="VALUE" x="198.12" y="93.98" size="1.778" layer="96" rot="R180" align="center"/>
<attribute name="NAME" x="198.12" y="86.36" size="1.778" layer="95" rot="R180" align="center"/>
</instance>
<instance part="A3L" gate="G$1" x="231.14" y="138.43" smashed="yes" rot="R180">
<attribute name="NAME" x="231.14" y="135.89" size="1.778" layer="95" rot="R180" align="center"/>
<attribute name="VALUE" x="231.14" y="140.97" size="1.778" layer="96" rot="R180" align="center"/>
</instance>
<instance part="A3H" gate="G$1" x="203.2" y="138.43" smashed="yes" rot="R180">
<attribute name="NAME" x="203.2" y="135.89" size="1.778" layer="95" rot="R180" align="center"/>
<attribute name="VALUE" x="203.2" y="140.97" size="1.778" layer="96" rot="R180" align="center"/>
</instance>
<instance part="A2L" gate="G$1" x="231.14" y="146.05" smashed="yes" rot="R180">
<attribute name="NAME" x="231.14" y="143.51" size="1.778" layer="95" rot="R180" align="center"/>
<attribute name="VALUE" x="231.14" y="148.59" size="1.778" layer="96" rot="R180" align="center"/>
</instance>
<instance part="A2H" gate="G$1" x="203.2" y="146.05" smashed="yes" rot="R180">
<attribute name="NAME" x="203.2" y="143.51" size="1.778" layer="95" rot="R180" align="center"/>
<attribute name="VALUE" x="203.2" y="148.59" size="1.778" layer="96" rot="R180" align="center"/>
</instance>
<instance part="A1L" gate="G$1" x="231.14" y="153.67" smashed="yes" rot="R180">
<attribute name="NAME" x="231.14" y="151.13" size="1.778" layer="95" rot="R180" align="center"/>
<attribute name="VALUE" x="231.14" y="156.21" size="1.778" layer="96" rot="R180" align="center"/>
</instance>
<instance part="A1H" gate="G$1" x="203.2" y="153.67" smashed="yes" rot="R180">
<attribute name="NAME" x="203.2" y="151.13" size="1.778" layer="95" rot="R180" align="center"/>
<attribute name="VALUE" x="203.2" y="156.21" size="1.778" layer="96" rot="R180" align="center"/>
</instance>
<instance part="A0L" gate="G$1" x="231.14" y="161.29" smashed="yes" rot="R180">
<attribute name="NAME" x="231.14" y="158.75" size="1.778" layer="95" rot="R180" align="center"/>
<attribute name="VALUE" x="231.14" y="163.83" size="1.778" layer="96" rot="R180" align="center"/>
</instance>
<instance part="U$27" gate="G$1" x="241.3" y="90.17" smashed="yes"/>
<instance part="C34" gate="G$1" x="198.12" y="80.01" smashed="yes" rot="R180">
<attribute name="VALUE" x="198.12" y="83.82" size="1.778" layer="96" rot="R180" align="center"/>
<attribute name="NAME" x="198.12" y="76.2" size="1.778" layer="95" rot="R180" align="center"/>
</instance>
<instance part="C35" gate="G$1" x="203.2" y="44.45" smashed="yes" rot="R180">
<attribute name="VALUE" x="203.2" y="48.26" size="1.778" layer="96" rot="R180" align="center"/>
<attribute name="NAME" x="203.2" y="40.64" size="1.778" layer="95" rot="R180" align="center"/>
</instance>
<instance part="VR1" gate="G$1" x="203.2" y="62.23" smashed="yes" rot="R90">
<attribute name="NAME" x="194.31" y="62.23" size="1.778" layer="95" rot="R90" align="center"/>
<attribute name="VALUE" x="212.09" y="62.23" size="1.778" layer="96" rot="R90" align="center"/>
</instance>
<instance part="U$28" gate="G$1" x="190.5" y="52.07" smashed="yes"/>
<instance part="U$29" gate="G$1" x="217.17" y="74.93" smashed="yes"/>
<instance part="U$30" gate="G$1" x="213.36" y="39.37" smashed="yes"/>
<instance part="A0H" gate="G$1" x="203.2" y="161.29" smashed="yes" rot="R180">
<attribute name="NAME" x="203.2" y="158.75" size="1.778" layer="95" rot="R180" align="center"/>
<attribute name="VALUE" x="203.2" y="163.83" size="1.778" layer="96" rot="R180" align="center"/>
</instance>
<instance part="U6" gate="G$1" x="134.62" y="107.95" smashed="yes" rot="R90">
<attribute name="NAME" x="121.92" y="107.95" size="1.778" layer="95" rot="R90" align="center"/>
<attribute name="VALUE" x="147.32" y="107.95" size="1.778" layer="96" rot="R90" align="center"/>
</instance>
<instance part="C36" gate="G$1" x="119.38" y="125.73" smashed="yes" rot="R180">
<attribute name="VALUE" x="119.38" y="129.54" size="1.778" layer="96" rot="R180" align="center"/>
<attribute name="NAME" x="119.38" y="121.92" size="1.778" layer="95" rot="R180" align="center"/>
</instance>
<instance part="C37" gate="G$1" x="119.38" y="90.17" smashed="yes" rot="R180">
<attribute name="VALUE" x="119.38" y="93.98" size="1.778" layer="96" rot="R180" align="center"/>
<attribute name="NAME" x="119.38" y="86.36" size="1.778" layer="95" rot="R180" align="center"/>
</instance>
<instance part="A3L1" gate="G$1" x="152.4" y="138.43" smashed="yes" rot="R180">
<attribute name="NAME" x="152.4" y="135.89" size="1.778" layer="95" rot="R180" align="center"/>
<attribute name="VALUE" x="152.4" y="140.97" size="1.778" layer="96" rot="R180" align="center"/>
</instance>
<instance part="A3H1" gate="G$1" x="124.46" y="138.43" smashed="yes" rot="R180">
<attribute name="NAME" x="124.46" y="135.89" size="1.778" layer="95" rot="R180" align="center"/>
<attribute name="VALUE" x="124.46" y="140.97" size="1.778" layer="96" rot="R180" align="center"/>
</instance>
<instance part="A2L1" gate="G$1" x="152.4" y="146.05" smashed="yes" rot="R180">
<attribute name="NAME" x="152.4" y="143.51" size="1.778" layer="95" rot="R180" align="center"/>
<attribute name="VALUE" x="152.4" y="148.59" size="1.778" layer="96" rot="R180" align="center"/>
</instance>
<instance part="A2H1" gate="G$1" x="124.46" y="146.05" smashed="yes" rot="R180">
<attribute name="NAME" x="124.46" y="143.51" size="1.778" layer="95" rot="R180" align="center"/>
<attribute name="VALUE" x="124.46" y="148.59" size="1.778" layer="96" rot="R180" align="center"/>
</instance>
<instance part="A1L1" gate="G$1" x="152.4" y="153.67" smashed="yes" rot="R180">
<attribute name="NAME" x="152.4" y="151.13" size="1.778" layer="95" rot="R180" align="center"/>
<attribute name="VALUE" x="152.4" y="156.21" size="1.778" layer="96" rot="R180" align="center"/>
</instance>
<instance part="A1H1" gate="G$1" x="124.46" y="153.67" smashed="yes" rot="R180">
<attribute name="NAME" x="124.46" y="151.13" size="1.778" layer="95" rot="R180" align="center"/>
<attribute name="VALUE" x="124.46" y="156.21" size="1.778" layer="96" rot="R180" align="center"/>
</instance>
<instance part="A0L1" gate="G$1" x="152.4" y="161.29" smashed="yes" rot="R180">
<attribute name="NAME" x="152.4" y="158.75" size="1.778" layer="95" rot="R180" align="center"/>
<attribute name="VALUE" x="152.4" y="163.83" size="1.778" layer="96" rot="R180" align="center"/>
</instance>
<instance part="U$32" gate="G$1" x="162.56" y="90.17" smashed="yes"/>
<instance part="C38" gate="G$1" x="119.38" y="80.01" smashed="yes" rot="R180">
<attribute name="VALUE" x="119.38" y="83.82" size="1.778" layer="96" rot="R180" align="center"/>
<attribute name="NAME" x="119.38" y="76.2" size="1.778" layer="95" rot="R180" align="center"/>
</instance>
<instance part="C39" gate="G$1" x="124.46" y="44.45" smashed="yes" rot="R180">
<attribute name="VALUE" x="124.46" y="48.26" size="1.778" layer="96" rot="R180" align="center"/>
<attribute name="NAME" x="124.46" y="40.64" size="1.778" layer="95" rot="R180" align="center"/>
</instance>
<instance part="VR2" gate="G$1" x="124.46" y="62.23" smashed="yes" rot="R90">
<attribute name="NAME" x="115.57" y="62.23" size="1.778" layer="95" rot="R90" align="center"/>
<attribute name="VALUE" x="133.35" y="62.23" size="1.778" layer="96" rot="R90" align="center"/>
</instance>
<instance part="U$33" gate="G$1" x="111.76" y="52.07" smashed="yes"/>
<instance part="U$34" gate="G$1" x="138.43" y="74.93" smashed="yes"/>
<instance part="U$35" gate="G$1" x="134.62" y="39.37" smashed="yes"/>
<instance part="A0H1" gate="G$1" x="124.46" y="161.29" smashed="yes" rot="R180">
<attribute name="NAME" x="124.46" y="158.75" size="1.778" layer="95" rot="R180" align="center"/>
<attribute name="VALUE" x="124.46" y="163.83" size="1.778" layer="96" rot="R180" align="center"/>
</instance>
<instance part="U7" gate="G$1" x="54.61" y="107.95" smashed="yes" rot="R90">
<attribute name="NAME" x="41.91" y="107.95" size="1.778" layer="95" rot="R90" align="center"/>
<attribute name="VALUE" x="67.31" y="107.95" size="1.778" layer="96" rot="R90" align="center"/>
</instance>
<instance part="C40" gate="G$1" x="39.37" y="125.73" smashed="yes" rot="R180">
<attribute name="VALUE" x="39.37" y="129.54" size="1.778" layer="96" rot="R180" align="center"/>
<attribute name="NAME" x="39.37" y="121.92" size="1.778" layer="95" rot="R180" align="center"/>
</instance>
<instance part="C41" gate="G$1" x="39.37" y="90.17" smashed="yes" rot="R180">
<attribute name="VALUE" x="39.37" y="93.98" size="1.778" layer="96" rot="R180" align="center"/>
<attribute name="NAME" x="39.37" y="86.36" size="1.778" layer="95" rot="R180" align="center"/>
</instance>
<instance part="A3L2" gate="G$1" x="72.39" y="138.43" smashed="yes" rot="R180">
<attribute name="NAME" x="72.39" y="135.89" size="1.778" layer="95" rot="R180" align="center"/>
<attribute name="VALUE" x="72.39" y="140.97" size="1.778" layer="96" rot="R180" align="center"/>
</instance>
<instance part="A3H2" gate="G$1" x="44.45" y="138.43" smashed="yes" rot="R180">
<attribute name="NAME" x="44.45" y="135.89" size="1.778" layer="95" rot="R180" align="center"/>
<attribute name="VALUE" x="44.45" y="140.97" size="1.778" layer="96" rot="R180" align="center"/>
</instance>
<instance part="A2L2" gate="G$1" x="72.39" y="146.05" smashed="yes" rot="R180">
<attribute name="NAME" x="72.39" y="143.51" size="1.778" layer="95" rot="R180" align="center"/>
<attribute name="VALUE" x="72.39" y="148.59" size="1.778" layer="96" rot="R180" align="center"/>
</instance>
<instance part="A2H2" gate="G$1" x="44.45" y="146.05" smashed="yes" rot="R180">
<attribute name="NAME" x="44.45" y="143.51" size="1.778" layer="95" rot="R180" align="center"/>
<attribute name="VALUE" x="44.45" y="148.59" size="1.778" layer="96" rot="R180" align="center"/>
</instance>
<instance part="A1L2" gate="G$1" x="72.39" y="153.67" smashed="yes" rot="R180">
<attribute name="NAME" x="72.39" y="151.13" size="1.778" layer="95" rot="R180" align="center"/>
<attribute name="VALUE" x="72.39" y="156.21" size="1.778" layer="96" rot="R180" align="center"/>
</instance>
<instance part="A1H2" gate="G$1" x="44.45" y="153.67" smashed="yes" rot="R180">
<attribute name="NAME" x="44.45" y="151.13" size="1.778" layer="95" rot="R180" align="center"/>
<attribute name="VALUE" x="44.45" y="156.21" size="1.778" layer="96" rot="R180" align="center"/>
</instance>
<instance part="A0L2" gate="G$1" x="72.39" y="161.29" smashed="yes" rot="R180">
<attribute name="NAME" x="72.39" y="158.75" size="1.778" layer="95" rot="R180" align="center"/>
<attribute name="VALUE" x="72.39" y="163.83" size="1.778" layer="96" rot="R180" align="center"/>
</instance>
<instance part="U$36" gate="G$1" x="82.55" y="90.17" smashed="yes"/>
<instance part="C42" gate="G$1" x="39.37" y="80.01" smashed="yes" rot="R180">
<attribute name="VALUE" x="39.37" y="83.82" size="1.778" layer="96" rot="R180" align="center"/>
<attribute name="NAME" x="39.37" y="76.2" size="1.778" layer="95" rot="R180" align="center"/>
</instance>
<instance part="C43" gate="G$1" x="44.45" y="44.45" smashed="yes" rot="R180">
<attribute name="VALUE" x="44.45" y="48.26" size="1.778" layer="96" rot="R180" align="center"/>
<attribute name="NAME" x="44.45" y="40.64" size="1.778" layer="95" rot="R180" align="center"/>
</instance>
<instance part="VR3" gate="G$1" x="44.45" y="62.23" smashed="yes" rot="R90">
<attribute name="NAME" x="35.56" y="62.23" size="1.778" layer="95" rot="R90" align="center"/>
<attribute name="VALUE" x="53.34" y="62.23" size="1.778" layer="96" rot="R90" align="center"/>
</instance>
<instance part="U$37" gate="G$1" x="31.75" y="52.07" smashed="yes"/>
<instance part="U$38" gate="G$1" x="58.42" y="74.93" smashed="yes"/>
<instance part="U$39" gate="G$1" x="54.61" y="39.37" smashed="yes"/>
<instance part="A0H2" gate="G$1" x="44.45" y="161.29" smashed="yes" rot="R180">
<attribute name="NAME" x="44.45" y="158.75" size="1.778" layer="95" rot="R180" align="center"/>
<attribute name="VALUE" x="44.45" y="163.83" size="1.778" layer="96" rot="R180" align="center"/>
</instance>
</instances>
<busses>
</busses>
<nets>
<net name="GND" class="0">
<segment>
<wire x1="238.76" y1="161.29" x2="241.3" y2="161.29" width="0.1524" layer="91"/>
<wire x1="241.3" y1="161.29" x2="241.3" y2="153.67" width="0.1524" layer="91"/>
<wire x1="241.3" y1="153.67" x2="238.76" y2="153.67" width="0.1524" layer="91"/>
<wire x1="241.3" y1="153.67" x2="241.3" y2="146.05" width="0.1524" layer="91"/>
<wire x1="241.3" y1="146.05" x2="238.76" y2="146.05" width="0.1524" layer="91"/>
<wire x1="241.3" y1="146.05" x2="241.3" y2="138.43" width="0.1524" layer="91"/>
<wire x1="241.3" y1="138.43" x2="238.76" y2="138.43" width="0.1524" layer="91"/>
<wire x1="241.3" y1="138.43" x2="241.3" y2="95.25" width="0.1524" layer="91"/>
<wire x1="241.3" y1="95.25" x2="220.98" y2="95.25" width="0.1524" layer="91"/>
<wire x1="220.98" y1="95.25" x2="220.98" y2="97.79" width="0.1524" layer="91"/>
<pinref part="U5" gate="G$1" pin="EP"/>
<wire x1="241.3" y1="95.25" x2="241.3" y2="92.71" width="0.1524" layer="91"/>
<pinref part="U$27" gate="G$1" pin="GND"/>
<junction x="241.3" y="153.67"/>
<junction x="241.3" y="146.05"/>
<junction x="241.3" y="138.43"/>
<junction x="241.3" y="95.25"/>
<pinref part="A3L" gate="G$1" pin="P$1"/>
<pinref part="A2L" gate="G$1" pin="P$1"/>
<pinref part="A1L" gate="G$1" pin="P$1"/>
<pinref part="A0L" gate="G$1" pin="P$1"/>
</segment>
<segment>
<wire x1="208.28" y1="72.39" x2="208.28" y2="80.01" width="0.1524" layer="91"/>
<wire x1="208.28" y1="80.01" x2="217.17" y2="80.01" width="0.1524" layer="91"/>
<wire x1="217.17" y1="80.01" x2="217.17" y2="77.47" width="0.1524" layer="91"/>
<pinref part="U$29" gate="G$1" pin="GND"/>
<wire x1="205.74" y1="80.01" x2="208.28" y2="80.01" width="0.1524" layer="91"/>
<pinref part="U5" gate="G$1" pin="GND"/>
<wire x1="208.28" y1="97.79" x2="208.28" y2="90.17" width="0.1524" layer="91"/>
<wire x1="208.28" y1="90.17" x2="205.74" y2="90.17" width="0.1524" layer="91"/>
<wire x1="208.28" y1="90.17" x2="208.28" y2="80.01" width="0.1524" layer="91"/>
<junction x="208.28" y="80.01"/>
<junction x="208.28" y="90.17"/>
<pinref part="C33" gate="G$1" pin="P$1"/>
<pinref part="C34" gate="G$1" pin="P$1"/>
<pinref part="VR1" gate="G$1" pin="VSS"/>
</segment>
<segment>
<pinref part="U$30" gate="G$1" pin="GND"/>
<wire x1="213.36" y1="41.91" x2="213.36" y2="44.45" width="0.1524" layer="91"/>
<wire x1="210.82" y1="44.45" x2="213.36" y2="44.45" width="0.1524" layer="91"/>
<wire x1="213.36" y1="44.45" x2="213.36" y2="49.53" width="0.1524" layer="91"/>
<wire x1="213.36" y1="49.53" x2="208.28" y2="49.53" width="0.1524" layer="91"/>
<wire x1="208.28" y1="49.53" x2="208.28" y2="52.07" width="0.1524" layer="91"/>
<junction x="213.36" y="44.45"/>
<pinref part="C35" gate="G$1" pin="P$1"/>
<pinref part="VR1" gate="G$1" pin="EN"/>
</segment>
<segment>
<wire x1="160.02" y1="161.29" x2="162.56" y2="161.29" width="0.1524" layer="91"/>
<wire x1="162.56" y1="161.29" x2="162.56" y2="153.67" width="0.1524" layer="91"/>
<wire x1="162.56" y1="153.67" x2="160.02" y2="153.67" width="0.1524" layer="91"/>
<wire x1="162.56" y1="153.67" x2="162.56" y2="146.05" width="0.1524" layer="91"/>
<wire x1="162.56" y1="146.05" x2="160.02" y2="146.05" width="0.1524" layer="91"/>
<wire x1="162.56" y1="146.05" x2="162.56" y2="138.43" width="0.1524" layer="91"/>
<wire x1="162.56" y1="138.43" x2="160.02" y2="138.43" width="0.1524" layer="91"/>
<wire x1="162.56" y1="138.43" x2="162.56" y2="95.25" width="0.1524" layer="91"/>
<wire x1="162.56" y1="95.25" x2="142.24" y2="95.25" width="0.1524" layer="91"/>
<wire x1="142.24" y1="95.25" x2="142.24" y2="97.79" width="0.1524" layer="91"/>
<pinref part="U6" gate="G$1" pin="EP"/>
<wire x1="162.56" y1="95.25" x2="162.56" y2="92.71" width="0.1524" layer="91"/>
<pinref part="U$32" gate="G$1" pin="GND"/>
<junction x="162.56" y="153.67"/>
<junction x="162.56" y="146.05"/>
<junction x="162.56" y="138.43"/>
<junction x="162.56" y="95.25"/>
<pinref part="A3L1" gate="G$1" pin="P$1"/>
<pinref part="A2L1" gate="G$1" pin="P$1"/>
<pinref part="A1L1" gate="G$1" pin="P$1"/>
<pinref part="A0L1" gate="G$1" pin="P$1"/>
</segment>
<segment>
<wire x1="129.54" y1="72.39" x2="129.54" y2="80.01" width="0.1524" layer="91"/>
<wire x1="129.54" y1="80.01" x2="138.43" y2="80.01" width="0.1524" layer="91"/>
<wire x1="138.43" y1="80.01" x2="138.43" y2="77.47" width="0.1524" layer="91"/>
<pinref part="U$34" gate="G$1" pin="GND"/>
<wire x1="127" y1="80.01" x2="129.54" y2="80.01" width="0.1524" layer="91"/>
<pinref part="U6" gate="G$1" pin="GND"/>
<wire x1="129.54" y1="97.79" x2="129.54" y2="90.17" width="0.1524" layer="91"/>
<wire x1="129.54" y1="90.17" x2="127" y2="90.17" width="0.1524" layer="91"/>
<wire x1="129.54" y1="90.17" x2="129.54" y2="80.01" width="0.1524" layer="91"/>
<junction x="129.54" y="80.01"/>
<junction x="129.54" y="90.17"/>
<pinref part="C37" gate="G$1" pin="P$1"/>
<pinref part="C38" gate="G$1" pin="P$1"/>
<pinref part="VR2" gate="G$1" pin="VSS"/>
</segment>
<segment>
<pinref part="U$35" gate="G$1" pin="GND"/>
<wire x1="134.62" y1="41.91" x2="134.62" y2="44.45" width="0.1524" layer="91"/>
<wire x1="132.08" y1="44.45" x2="134.62" y2="44.45" width="0.1524" layer="91"/>
<wire x1="134.62" y1="44.45" x2="134.62" y2="49.53" width="0.1524" layer="91"/>
<wire x1="134.62" y1="49.53" x2="129.54" y2="49.53" width="0.1524" layer="91"/>
<wire x1="129.54" y1="49.53" x2="129.54" y2="52.07" width="0.1524" layer="91"/>
<junction x="134.62" y="44.45"/>
<pinref part="C39" gate="G$1" pin="P$1"/>
<pinref part="VR2" gate="G$1" pin="EN"/>
</segment>
<segment>
<wire x1="80.01" y1="161.29" x2="82.55" y2="161.29" width="0.1524" layer="91"/>
<wire x1="82.55" y1="161.29" x2="82.55" y2="153.67" width="0.1524" layer="91"/>
<wire x1="82.55" y1="153.67" x2="80.01" y2="153.67" width="0.1524" layer="91"/>
<wire x1="82.55" y1="153.67" x2="82.55" y2="146.05" width="0.1524" layer="91"/>
<wire x1="82.55" y1="146.05" x2="80.01" y2="146.05" width="0.1524" layer="91"/>
<wire x1="82.55" y1="146.05" x2="82.55" y2="138.43" width="0.1524" layer="91"/>
<wire x1="82.55" y1="138.43" x2="80.01" y2="138.43" width="0.1524" layer="91"/>
<wire x1="82.55" y1="138.43" x2="82.55" y2="95.25" width="0.1524" layer="91"/>
<wire x1="82.55" y1="95.25" x2="62.23" y2="95.25" width="0.1524" layer="91"/>
<wire x1="62.23" y1="95.25" x2="62.23" y2="97.79" width="0.1524" layer="91"/>
<pinref part="U7" gate="G$1" pin="EP"/>
<wire x1="82.55" y1="95.25" x2="82.55" y2="92.71" width="0.1524" layer="91"/>
<pinref part="U$36" gate="G$1" pin="GND"/>
<junction x="82.55" y="153.67"/>
<junction x="82.55" y="146.05"/>
<junction x="82.55" y="138.43"/>
<junction x="82.55" y="95.25"/>
<pinref part="A3L2" gate="G$1" pin="P$1"/>
<pinref part="A2L2" gate="G$1" pin="P$1"/>
<pinref part="A1L2" gate="G$1" pin="P$1"/>
<pinref part="A0L2" gate="G$1" pin="P$1"/>
</segment>
<segment>
<wire x1="49.53" y1="72.39" x2="49.53" y2="80.01" width="0.1524" layer="91"/>
<wire x1="49.53" y1="80.01" x2="58.42" y2="80.01" width="0.1524" layer="91"/>
<wire x1="58.42" y1="80.01" x2="58.42" y2="77.47" width="0.1524" layer="91"/>
<pinref part="U$38" gate="G$1" pin="GND"/>
<wire x1="46.99" y1="80.01" x2="49.53" y2="80.01" width="0.1524" layer="91"/>
<pinref part="U7" gate="G$1" pin="GND"/>
<wire x1="49.53" y1="97.79" x2="49.53" y2="90.17" width="0.1524" layer="91"/>
<wire x1="49.53" y1="90.17" x2="46.99" y2="90.17" width="0.1524" layer="91"/>
<wire x1="49.53" y1="90.17" x2="49.53" y2="80.01" width="0.1524" layer="91"/>
<junction x="49.53" y="80.01"/>
<junction x="49.53" y="90.17"/>
<pinref part="C41" gate="G$1" pin="P$1"/>
<pinref part="C42" gate="G$1" pin="P$1"/>
<pinref part="VR3" gate="G$1" pin="VSS"/>
</segment>
<segment>
<pinref part="U$39" gate="G$1" pin="GND"/>
<wire x1="54.61" y1="41.91" x2="54.61" y2="44.45" width="0.1524" layer="91"/>
<wire x1="52.07" y1="44.45" x2="54.61" y2="44.45" width="0.1524" layer="91"/>
<wire x1="54.61" y1="44.45" x2="54.61" y2="49.53" width="0.1524" layer="91"/>
<wire x1="54.61" y1="49.53" x2="49.53" y2="49.53" width="0.1524" layer="91"/>
<wire x1="49.53" y1="49.53" x2="49.53" y2="52.07" width="0.1524" layer="91"/>
<junction x="54.61" y="44.45"/>
<pinref part="C43" gate="G$1" pin="P$1"/>
<pinref part="VR3" gate="G$1" pin="EN"/>
</segment>
</net>
<net name="4V0" class="0">
<segment>
<pinref part="U$28" gate="G$1" pin="4V0"/>
<wire x1="190.5" y1="52.07" x2="190.5" y2="49.53" width="0.1524" layer="91"/>
<wire x1="190.5" y1="44.45" x2="195.58" y2="44.45" width="0.1524" layer="91"/>
<wire x1="190.5" y1="44.45" x2="190.5" y2="49.53" width="0.1524" layer="91"/>
<wire x1="190.5" y1="49.53" x2="198.12" y2="49.53" width="0.1524" layer="91"/>
<wire x1="198.12" y1="49.53" x2="198.12" y2="52.07" width="0.1524" layer="91"/>
<junction x="190.5" y="49.53"/>
<pinref part="C35" gate="G$1" pin="P$2"/>
<pinref part="VR1" gate="G$1" pin="VDD"/>
</segment>
<segment>
<pinref part="U$33" gate="G$1" pin="4V0"/>
<wire x1="111.76" y1="52.07" x2="111.76" y2="49.53" width="0.1524" layer="91"/>
<wire x1="111.76" y1="44.45" x2="116.84" y2="44.45" width="0.1524" layer="91"/>
<wire x1="111.76" y1="44.45" x2="111.76" y2="49.53" width="0.1524" layer="91"/>
<wire x1="111.76" y1="49.53" x2="119.38" y2="49.53" width="0.1524" layer="91"/>
<wire x1="119.38" y1="49.53" x2="119.38" y2="52.07" width="0.1524" layer="91"/>
<junction x="111.76" y="49.53"/>
<pinref part="C39" gate="G$1" pin="P$2"/>
<pinref part="VR2" gate="G$1" pin="VDD"/>
</segment>
<segment>
<pinref part="U$37" gate="G$1" pin="4V0"/>
<wire x1="31.75" y1="52.07" x2="31.75" y2="49.53" width="0.1524" layer="91"/>
<wire x1="31.75" y1="44.45" x2="36.83" y2="44.45" width="0.1524" layer="91"/>
<wire x1="31.75" y1="44.45" x2="31.75" y2="49.53" width="0.1524" layer="91"/>
<wire x1="31.75" y1="49.53" x2="39.37" y2="49.53" width="0.1524" layer="91"/>
<wire x1="39.37" y1="49.53" x2="39.37" y2="52.07" width="0.1524" layer="91"/>
<junction x="31.75" y="49.53"/>
<pinref part="C43" gate="G$1" pin="P$2"/>
<pinref part="VR3" gate="G$1" pin="VDD"/>
</segment>
</net>
<net name="N$19" class="0">
<segment>
<pinref part="U5" gate="G$1" pin="A0"/>
<wire x1="213.36" y1="118.11" x2="213.36" y2="161.29" width="0.1524" layer="91"/>
<wire x1="213.36" y1="161.29" x2="223.52" y2="161.29" width="0.1524" layer="91"/>
<wire x1="213.36" y1="161.29" x2="210.82" y2="161.29" width="0.1524" layer="91"/>
<junction x="213.36" y="161.29"/>
<pinref part="A0L" gate="G$1" pin="P$2"/>
<pinref part="A0H" gate="G$1" pin="P$1"/>
</segment>
</net>
<net name="N$20" class="0">
<segment>
<pinref part="U5" gate="G$1" pin="A1"/>
<wire x1="215.9" y1="118.11" x2="215.9" y2="153.67" width="0.1524" layer="91"/>
<wire x1="215.9" y1="153.67" x2="223.52" y2="153.67" width="0.1524" layer="91"/>
<wire x1="215.9" y1="153.67" x2="210.82" y2="153.67" width="0.1524" layer="91"/>
<junction x="215.9" y="153.67"/>
<pinref part="A1L" gate="G$1" pin="P$2"/>
<pinref part="A1H" gate="G$1" pin="P$1"/>
</segment>
</net>
<net name="N$22" class="0">
<segment>
<pinref part="U5" gate="G$1" pin="A2"/>
<wire x1="218.44" y1="118.11" x2="218.44" y2="146.05" width="0.1524" layer="91"/>
<wire x1="218.44" y1="146.05" x2="223.52" y2="146.05" width="0.1524" layer="91"/>
<wire x1="218.44" y1="146.05" x2="210.82" y2="146.05" width="0.1524" layer="91"/>
<junction x="218.44" y="146.05"/>
<pinref part="A2L" gate="G$1" pin="P$2"/>
<pinref part="A2H" gate="G$1" pin="P$1"/>
</segment>
</net>
<net name="N$23" class="0">
<segment>
<pinref part="U5" gate="G$1" pin="A3"/>
<wire x1="220.98" y1="118.11" x2="220.98" y2="138.43" width="0.1524" layer="91"/>
<wire x1="220.98" y1="138.43" x2="223.52" y2="138.43" width="0.1524" layer="91"/>
<wire x1="220.98" y1="138.43" x2="210.82" y2="138.43" width="0.1524" layer="91"/>
<junction x="220.98" y="138.43"/>
<pinref part="A3L" gate="G$1" pin="P$2"/>
<pinref part="A3H" gate="G$1" pin="P$1"/>
</segment>
</net>
<net name="1WS_DATA" class="0">
<segment>
<pinref part="U5" gate="G$1" pin="DQ"/>
<wire x1="218.44" y1="97.79" x2="218.44" y2="95.25" width="0.1524" layer="91"/>
<label x="218.44" y="95.25" size="0.889" layer="95" rot="R270" xref="yes"/>
</segment>
<segment>
<wire x1="195.58" y1="138.43" x2="193.04" y2="138.43" width="0.1524" layer="91"/>
<wire x1="193.04" y1="138.43" x2="193.04" y2="146.05" width="0.1524" layer="91"/>
<wire x1="195.58" y1="146.05" x2="193.04" y2="146.05" width="0.1524" layer="91"/>
<wire x1="193.04" y1="146.05" x2="193.04" y2="153.67" width="0.1524" layer="91"/>
<wire x1="193.04" y1="153.67" x2="195.58" y2="153.67" width="0.1524" layer="91"/>
<junction x="193.04" y="146.05"/>
<wire x1="193.04" y1="153.67" x2="193.04" y2="161.29" width="0.1524" layer="91"/>
<wire x1="193.04" y1="161.29" x2="195.58" y2="161.29" width="0.1524" layer="91"/>
<junction x="193.04" y="153.67"/>
<wire x1="193.04" y1="138.43" x2="190.5" y2="138.43" width="0.1524" layer="91"/>
<junction x="193.04" y="138.43"/>
<label x="190.5" y="138.43" size="0.889" layer="95" rot="R180" xref="yes"/>
<pinref part="A3H" gate="G$1" pin="P$2"/>
<pinref part="A2H" gate="G$1" pin="P$2"/>
<pinref part="A1H" gate="G$1" pin="P$2"/>
<pinref part="A0H" gate="G$1" pin="P$2"/>
</segment>
<segment>
<pinref part="U6" gate="G$1" pin="DQ"/>
<wire x1="139.7" y1="97.79" x2="139.7" y2="95.25" width="0.1524" layer="91"/>
<label x="139.7" y="95.25" size="0.889" layer="95" rot="R270" xref="yes"/>
</segment>
<segment>
<wire x1="116.84" y1="138.43" x2="114.3" y2="138.43" width="0.1524" layer="91"/>
<wire x1="114.3" y1="138.43" x2="114.3" y2="146.05" width="0.1524" layer="91"/>
<wire x1="116.84" y1="146.05" x2="114.3" y2="146.05" width="0.1524" layer="91"/>
<wire x1="114.3" y1="146.05" x2="114.3" y2="153.67" width="0.1524" layer="91"/>
<wire x1="114.3" y1="153.67" x2="116.84" y2="153.67" width="0.1524" layer="91"/>
<junction x="114.3" y="146.05"/>
<wire x1="114.3" y1="153.67" x2="114.3" y2="161.29" width="0.1524" layer="91"/>
<wire x1="114.3" y1="161.29" x2="116.84" y2="161.29" width="0.1524" layer="91"/>
<junction x="114.3" y="153.67"/>
<wire x1="114.3" y1="138.43" x2="111.76" y2="138.43" width="0.1524" layer="91"/>
<junction x="114.3" y="138.43"/>
<label x="111.76" y="138.43" size="0.889" layer="95" rot="R180" xref="yes"/>
<pinref part="A3H1" gate="G$1" pin="P$2"/>
<pinref part="A2H1" gate="G$1" pin="P$2"/>
<pinref part="A1H1" gate="G$1" pin="P$2"/>
<pinref part="A0H1" gate="G$1" pin="P$2"/>
</segment>
<segment>
<pinref part="U7" gate="G$1" pin="DQ"/>
<wire x1="59.69" y1="97.79" x2="59.69" y2="95.25" width="0.1524" layer="91"/>
<label x="59.69" y="95.25" size="0.889" layer="95" rot="R270" xref="yes"/>
</segment>
<segment>
<wire x1="36.83" y1="138.43" x2="34.29" y2="138.43" width="0.1524" layer="91"/>
<wire x1="34.29" y1="138.43" x2="34.29" y2="146.05" width="0.1524" layer="91"/>
<wire x1="36.83" y1="146.05" x2="34.29" y2="146.05" width="0.1524" layer="91"/>
<wire x1="34.29" y1="146.05" x2="34.29" y2="153.67" width="0.1524" layer="91"/>
<wire x1="34.29" y1="153.67" x2="36.83" y2="153.67" width="0.1524" layer="91"/>
<junction x="34.29" y="146.05"/>
<wire x1="34.29" y1="153.67" x2="34.29" y2="161.29" width="0.1524" layer="91"/>
<wire x1="34.29" y1="161.29" x2="36.83" y2="161.29" width="0.1524" layer="91"/>
<junction x="34.29" y="153.67"/>
<wire x1="34.29" y1="138.43" x2="31.75" y2="138.43" width="0.1524" layer="91"/>
<junction x="34.29" y="138.43"/>
<label x="31.75" y="138.43" size="0.889" layer="95" rot="R180" xref="yes"/>
<pinref part="A3H2" gate="G$1" pin="P$2"/>
<pinref part="A2H2" gate="G$1" pin="P$2"/>
<pinref part="A1H2" gate="G$1" pin="P$2"/>
<pinref part="A0H2" gate="G$1" pin="P$2"/>
</segment>
</net>
<net name="T1+" class="0">
<segment>
<pinref part="U5" gate="G$1" pin="T+"/>
<wire x1="205.74" y1="118.11" x2="205.74" y2="120.65" width="0.1524" layer="91"/>
<wire x1="205.74" y1="120.65" x2="187.96" y2="120.65" width="0.1524" layer="91"/>
<wire x1="187.96" y1="120.65" x2="187.96" y2="125.73" width="0.1524" layer="91"/>
<wire x1="187.96" y1="125.73" x2="190.5" y2="125.73" width="0.1524" layer="91"/>
<wire x1="187.96" y1="125.73" x2="185.42" y2="125.73" width="0.1524" layer="91"/>
<junction x="187.96" y="125.73"/>
<label x="185.42" y="125.73" size="0.889" layer="95" rot="R180" xref="yes"/>
<pinref part="C32" gate="G$1" pin="P$2"/>
</segment>
</net>
<net name="T1-" class="0">
<segment>
<pinref part="U5" gate="G$1" pin="T-"/>
<wire x1="208.28" y1="118.11" x2="208.28" y2="125.73" width="0.1524" layer="91"/>
<wire x1="208.28" y1="125.73" x2="205.74" y2="125.73" width="0.1524" layer="91"/>
<wire x1="208.28" y1="125.73" x2="208.28" y2="130.81" width="0.1524" layer="91"/>
<wire x1="208.28" y1="130.81" x2="185.42" y2="130.81" width="0.1524" layer="91"/>
<junction x="208.28" y="125.73"/>
<label x="185.42" y="130.81" size="0.889" layer="95" rot="R180" xref="yes"/>
<pinref part="C32" gate="G$1" pin="P$1"/>
</segment>
</net>
<net name="N$28" class="0">
<segment>
<wire x1="198.12" y1="72.39" x2="198.12" y2="74.93" width="0.1524" layer="91"/>
<wire x1="198.12" y1="74.93" x2="187.96" y2="74.93" width="0.1524" layer="91"/>
<wire x1="187.96" y1="74.93" x2="187.96" y2="80.01" width="0.1524" layer="91"/>
<wire x1="187.96" y1="80.01" x2="190.5" y2="80.01" width="0.1524" layer="91"/>
<wire x1="187.96" y1="80.01" x2="187.96" y2="90.17" width="0.1524" layer="91"/>
<junction x="187.96" y="80.01"/>
<pinref part="U5" gate="G$1" pin="VDD"/>
<wire x1="205.74" y1="97.79" x2="205.74" y2="95.25" width="0.1524" layer="91"/>
<wire x1="205.74" y1="95.25" x2="187.96" y2="95.25" width="0.1524" layer="91"/>
<wire x1="187.96" y1="95.25" x2="187.96" y2="90.17" width="0.1524" layer="91"/>
<wire x1="187.96" y1="90.17" x2="190.5" y2="90.17" width="0.1524" layer="91"/>
<junction x="187.96" y="90.17"/>
<pinref part="C33" gate="G$1" pin="P$2"/>
<pinref part="C34" gate="G$1" pin="P$2"/>
<pinref part="VR1" gate="G$1" pin="VOUT"/>
</segment>
</net>
<net name="T2-" class="0">
<segment>
<pinref part="U6" gate="G$1" pin="T-"/>
<wire x1="129.54" y1="118.11" x2="129.54" y2="125.73" width="0.1524" layer="91"/>
<wire x1="129.54" y1="125.73" x2="127" y2="125.73" width="0.1524" layer="91"/>
<wire x1="129.54" y1="125.73" x2="129.54" y2="130.81" width="0.1524" layer="91"/>
<wire x1="129.54" y1="130.81" x2="106.68" y2="130.81" width="0.1524" layer="91"/>
<junction x="129.54" y="125.73"/>
<label x="106.68" y="130.81" size="0.889" layer="95" rot="R180" xref="yes"/>
<pinref part="C36" gate="G$1" pin="P$1"/>
</segment>
</net>
<net name="T2+" class="0">
<segment>
<pinref part="U6" gate="G$1" pin="T+"/>
<wire x1="127" y1="118.11" x2="127" y2="120.65" width="0.1524" layer="91"/>
<wire x1="127" y1="120.65" x2="109.22" y2="120.65" width="0.1524" layer="91"/>
<wire x1="109.22" y1="120.65" x2="109.22" y2="125.73" width="0.1524" layer="91"/>
<wire x1="109.22" y1="125.73" x2="111.76" y2="125.73" width="0.1524" layer="91"/>
<wire x1="109.22" y1="125.73" x2="106.68" y2="125.73" width="0.1524" layer="91"/>
<junction x="109.22" y="125.73"/>
<label x="106.68" y="125.73" size="0.889" layer="95" rot="R180" xref="yes"/>
<pinref part="C36" gate="G$1" pin="P$2"/>
</segment>
</net>
<net name="T3+" class="0">
<segment>
<pinref part="U7" gate="G$1" pin="T+"/>
<wire x1="46.99" y1="118.11" x2="46.99" y2="120.65" width="0.1524" layer="91"/>
<wire x1="46.99" y1="120.65" x2="29.21" y2="120.65" width="0.1524" layer="91"/>
<wire x1="29.21" y1="120.65" x2="29.21" y2="125.73" width="0.1524" layer="91"/>
<wire x1="29.21" y1="125.73" x2="31.75" y2="125.73" width="0.1524" layer="91"/>
<wire x1="29.21" y1="125.73" x2="26.67" y2="125.73" width="0.1524" layer="91"/>
<junction x="29.21" y="125.73"/>
<label x="26.67" y="125.73" size="0.889" layer="95" rot="R180" xref="yes"/>
<pinref part="C40" gate="G$1" pin="P$2"/>
</segment>
</net>
<net name="T3-" class="0">
<segment>
<pinref part="U7" gate="G$1" pin="T-"/>
<wire x1="49.53" y1="118.11" x2="49.53" y2="125.73" width="0.1524" layer="91"/>
<wire x1="49.53" y1="125.73" x2="46.99" y2="125.73" width="0.1524" layer="91"/>
<wire x1="49.53" y1="125.73" x2="49.53" y2="130.81" width="0.1524" layer="91"/>
<wire x1="49.53" y1="130.81" x2="26.67" y2="130.81" width="0.1524" layer="91"/>
<junction x="49.53" y="125.73"/>
<label x="26.67" y="130.81" size="0.889" layer="95" rot="R180" xref="yes"/>
<pinref part="C40" gate="G$1" pin="P$1"/>
</segment>
</net>
<net name="N$24" class="0">
<segment>
<pinref part="U6" gate="G$1" pin="A0"/>
<wire x1="134.62" y1="118.11" x2="134.62" y2="161.29" width="0.1524" layer="91"/>
<wire x1="134.62" y1="161.29" x2="144.78" y2="161.29" width="0.1524" layer="91"/>
<wire x1="134.62" y1="161.29" x2="132.08" y2="161.29" width="0.1524" layer="91"/>
<junction x="134.62" y="161.29"/>
<pinref part="A0L1" gate="G$1" pin="P$2"/>
<pinref part="A0H1" gate="G$1" pin="P$1"/>
</segment>
</net>
<net name="N$25" class="0">
<segment>
<pinref part="U6" gate="G$1" pin="A1"/>
<wire x1="137.16" y1="118.11" x2="137.16" y2="153.67" width="0.1524" layer="91"/>
<wire x1="137.16" y1="153.67" x2="144.78" y2="153.67" width="0.1524" layer="91"/>
<wire x1="137.16" y1="153.67" x2="132.08" y2="153.67" width="0.1524" layer="91"/>
<junction x="137.16" y="153.67"/>
<pinref part="A1L1" gate="G$1" pin="P$2"/>
<pinref part="A1H1" gate="G$1" pin="P$1"/>
</segment>
</net>
<net name="N$26" class="0">
<segment>
<pinref part="U6" gate="G$1" pin="A2"/>
<wire x1="139.7" y1="118.11" x2="139.7" y2="146.05" width="0.1524" layer="91"/>
<wire x1="139.7" y1="146.05" x2="144.78" y2="146.05" width="0.1524" layer="91"/>
<wire x1="139.7" y1="146.05" x2="132.08" y2="146.05" width="0.1524" layer="91"/>
<junction x="139.7" y="146.05"/>
<pinref part="A2L1" gate="G$1" pin="P$2"/>
<pinref part="A2H1" gate="G$1" pin="P$1"/>
</segment>
</net>
<net name="N$27" class="0">
<segment>
<pinref part="U6" gate="G$1" pin="A3"/>
<wire x1="142.24" y1="118.11" x2="142.24" y2="138.43" width="0.1524" layer="91"/>
<wire x1="142.24" y1="138.43" x2="144.78" y2="138.43" width="0.1524" layer="91"/>
<wire x1="142.24" y1="138.43" x2="132.08" y2="138.43" width="0.1524" layer="91"/>
<junction x="142.24" y="138.43"/>
<pinref part="A3L1" gate="G$1" pin="P$2"/>
<pinref part="A3H1" gate="G$1" pin="P$1"/>
</segment>
</net>
<net name="N$29" class="0">
<segment>
<wire x1="119.38" y1="72.39" x2="119.38" y2="74.93" width="0.1524" layer="91"/>
<wire x1="119.38" y1="74.93" x2="109.22" y2="74.93" width="0.1524" layer="91"/>
<wire x1="109.22" y1="74.93" x2="109.22" y2="80.01" width="0.1524" layer="91"/>
<wire x1="109.22" y1="80.01" x2="111.76" y2="80.01" width="0.1524" layer="91"/>
<wire x1="109.22" y1="80.01" x2="109.22" y2="90.17" width="0.1524" layer="91"/>
<junction x="109.22" y="80.01"/>
<pinref part="U6" gate="G$1" pin="VDD"/>
<wire x1="127" y1="97.79" x2="127" y2="95.25" width="0.1524" layer="91"/>
<wire x1="127" y1="95.25" x2="109.22" y2="95.25" width="0.1524" layer="91"/>
<wire x1="109.22" y1="95.25" x2="109.22" y2="90.17" width="0.1524" layer="91"/>
<wire x1="109.22" y1="90.17" x2="111.76" y2="90.17" width="0.1524" layer="91"/>
<junction x="109.22" y="90.17"/>
<pinref part="C37" gate="G$1" pin="P$2"/>
<pinref part="C38" gate="G$1" pin="P$2"/>
<pinref part="VR2" gate="G$1" pin="VOUT"/>
</segment>
</net>
<net name="N$30" class="0">
<segment>
<pinref part="U7" gate="G$1" pin="A0"/>
<wire x1="54.61" y1="118.11" x2="54.61" y2="161.29" width="0.1524" layer="91"/>
<wire x1="54.61" y1="161.29" x2="64.77" y2="161.29" width="0.1524" layer="91"/>
<wire x1="54.61" y1="161.29" x2="52.07" y2="161.29" width="0.1524" layer="91"/>
<junction x="54.61" y="161.29"/>
<pinref part="A0L2" gate="G$1" pin="P$2"/>
<pinref part="A0H2" gate="G$1" pin="P$1"/>
</segment>
</net>
<net name="N$31" class="0">
<segment>
<pinref part="U7" gate="G$1" pin="A1"/>
<wire x1="57.15" y1="118.11" x2="57.15" y2="153.67" width="0.1524" layer="91"/>
<wire x1="57.15" y1="153.67" x2="64.77" y2="153.67" width="0.1524" layer="91"/>
<wire x1="57.15" y1="153.67" x2="52.07" y2="153.67" width="0.1524" layer="91"/>
<junction x="57.15" y="153.67"/>
<pinref part="A1L2" gate="G$1" pin="P$2"/>
<pinref part="A1H2" gate="G$1" pin="P$1"/>
</segment>
</net>
<net name="N$32" class="0">
<segment>
<pinref part="U7" gate="G$1" pin="A2"/>
<wire x1="59.69" y1="118.11" x2="59.69" y2="146.05" width="0.1524" layer="91"/>
<wire x1="59.69" y1="146.05" x2="64.77" y2="146.05" width="0.1524" layer="91"/>
<wire x1="59.69" y1="146.05" x2="52.07" y2="146.05" width="0.1524" layer="91"/>
<junction x="59.69" y="146.05"/>
<pinref part="A2L2" gate="G$1" pin="P$2"/>
<pinref part="A2H2" gate="G$1" pin="P$1"/>
</segment>
</net>
<net name="N$33" class="0">
<segment>
<pinref part="U7" gate="G$1" pin="A3"/>
<wire x1="62.23" y1="118.11" x2="62.23" y2="138.43" width="0.1524" layer="91"/>
<wire x1="62.23" y1="138.43" x2="64.77" y2="138.43" width="0.1524" layer="91"/>
<wire x1="62.23" y1="138.43" x2="52.07" y2="138.43" width="0.1524" layer="91"/>
<junction x="62.23" y="138.43"/>
<pinref part="A3L2" gate="G$1" pin="P$2"/>
<pinref part="A3H2" gate="G$1" pin="P$1"/>
</segment>
</net>
<net name="N$34" class="0">
<segment>
<wire x1="39.37" y1="72.39" x2="39.37" y2="74.93" width="0.1524" layer="91"/>
<wire x1="39.37" y1="74.93" x2="29.21" y2="74.93" width="0.1524" layer="91"/>
<wire x1="29.21" y1="74.93" x2="29.21" y2="80.01" width="0.1524" layer="91"/>
<wire x1="29.21" y1="80.01" x2="31.75" y2="80.01" width="0.1524" layer="91"/>
<wire x1="29.21" y1="80.01" x2="29.21" y2="90.17" width="0.1524" layer="91"/>
<junction x="29.21" y="80.01"/>
<pinref part="U7" gate="G$1" pin="VDD"/>
<wire x1="46.99" y1="97.79" x2="46.99" y2="95.25" width="0.1524" layer="91"/>
<wire x1="46.99" y1="95.25" x2="29.21" y2="95.25" width="0.1524" layer="91"/>
<wire x1="29.21" y1="95.25" x2="29.21" y2="90.17" width="0.1524" layer="91"/>
<wire x1="29.21" y1="90.17" x2="31.75" y2="90.17" width="0.1524" layer="91"/>
<junction x="29.21" y="90.17"/>
<pinref part="C41" gate="G$1" pin="P$2"/>
<pinref part="C42" gate="G$1" pin="P$2"/>
<pinref part="VR3" gate="G$1" pin="VOUT"/>
</segment>
</net>
</nets>
</sheet>
</sheets>
</schematic>
</drawing>
<compatibility>
<note version="8.2" severity="warning">
Since Version 8.2, EAGLE supports online libraries. The ids
of those online libraries will not be understood (or retained)
with this version.
</note>
<note version="8.3" severity="warning">
Since Version 8.3, EAGLE supports the association of 3D packages
with devices in libraries, schematics, and board files. Those 3D
packages will not be understood (or retained) with this version.
</note>
</compatibility>
</eagle>

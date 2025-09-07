# Sbírka pokusů s transkripty z Poslanecké sněmovny ČR

.py skripty v hlavním adresáři jsou AI-generované skritpy pro základní scrapování stenoprotokolů.

Složka **parliament_transcripts** obsahuje přímo vyscrapovaná data tak, [jak jsou dostupná](https://www.psp.cz/eknih/2021ps/stenprot/127schuz/s127001.htm#r1).
Důvody, proč je tady mít jsou dva:
 - PS má poměrně nepříjemný rate limit pro stahování a tak mi scraping chvíli zabral
 - data jsou sice poskytována i v .zip archivech (po rozbalení bohužel z nějakého důvodu ve stejném .htm formátu) nicméně archivy jsou nekompletní - použil jsem je jako základ a potom je musel doplnit pomocí scraperu.

Složka **parliament_speeches** už obsahuje jednotlivé proslovy ve formátu kterým se dá příčetně nakrmit umělá inteligence. Pro lepší zpracování si je můžete překlopit třeba do jsonu, ale tahle struktura už je pro počítač poměrně stravitelná.
Zajímavé je například pomocí **concatenate_files.py** sesypat dohromady data z celého dne(nebo i celého zasedání, je-li vícedenní) 

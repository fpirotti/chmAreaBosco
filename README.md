# Da CHM a Area Bosco
![alt text](logo.png)


[Descrizione](#Descrizione) |
[INPUT](#Metodi) |
[Installazione](#Installazione) |
[Benchmark](#benchmark) |
[Esempio 1](#Esempio_1) |
[Esempio 2](#Esempio_2)

## Descrizione  

Il plugin CHM => Bosco converte un livello raster con il modello delle 
chiome (CHM - Canopy Height Model) in un raster binario dove 0=non bosco 
e 1=bosco. Vengono utilizzati diversi parametri per definire 
le caratteristiche del bosco.

Il peso del plugin è circa 110 MB in quanto include la libreria 
grafica [OpenCV - *Open Source Computer Vision Library*](https://it.wikipedia.org/wiki/OpenCV) (109 MB)
che consente elaborazioni ottimizzate su immagini raster.

## Metodi

### Input 

 - Un livello raster contenente il CHM ovvero un modello delle chiome. 
Questo raster deve necessariamente essere accurato, 
in quanto fornisce l'informazione di base per la 
creazione dell'area a bosco.
 - Un raster binario BOSCO* (pixel con valore 1 = pixel bosco) \[OPZIONALE\]: 
il valore 1 del pixel di questo raster verrà considerato bosco a prescindere 
dal risultato del plugin, ovvero questa informazione avrà priorità
nella definizione bosco. [vedi schema in immagine 1](#immagine_1)
 - Un raster binario NON BOSCO* (pixel con valore 1 = pixel NON bosco) \[OPZIONALE\]: 
il valore 1 del pixel di questo raster verrà considerato non bosco a prescindere 
dal risultato del plugin, ovvero questa informazione avrà priorità
nella definizione di aree da escludere dall'area bosco. [vedi schema in immagine 1](#immagine_1)
- Soglia altezza chioma (m) - l'altezza della chioma minima per definire il pixel
come appartenente ad un albero.
- Densità copertura (%) - La proporzione minima coperta da chioma perchè l'area venga inclusa
come bosco.
- Area minima (m2) - L'area minima per definire un'area a bosco.
- Larghezza minima (m) - L'area minima per definire un'area a bosco.

### Output

Come output c'
Gli output sotto sono entrambi opzionali - nel senso che si possono creare entrambi o nessuno dei due.

- Raster output - L'area minima per definire un'area a bosco.
- Vettoriale output - Il file vettoriale delle aree a bosco, tematizzato e con una colonna "area_ha" con 
l'area in ettari.


        * Attenzione - i due raster binari Bosco e Non Bosco devono avere
        valori zero (0) per i pixel non appartenenti alla cateogria, 
        e un numero diverso da zero (preferibilmente 1) per i pixel 
        appartenenti alla categoria. Ad esempio si può ottenere un raster 
        "Non Bosco" da poligoni che rappresentano le aree urbanizzate 
        facendo la conversione da formato vettoriale a raster 
        (mediante il comando nel menù raster==>Conversione==>Rasterizza)
        
**NB:** nel caso di utilizzo di entrambi i raster "binari", in caso di 
valori in conflitto ovvero discordanti, viene data priorità al raster non-bosco
[vedi schema in immagine 1](#immagine_1)

<a name="immagine_1"></a>
![Esempio di bosco e non bosco](img/mask.png)

## Installazione  

Scaricare il file compresso "chmAreaBosco-xxxx.zip" dell'ultima versione
[al link GITHUB](https://github.com/cirgeo/chmAreaBosco/releases) dove 
xxx indica il sistema operativo

Andare sul menù QGIS "Plugins"=>"Gestisci ed Installa Plugins" e selezionare 
"Installa da ZIP" nella parte sinistra della finestra ed il file compresso scaricato.
Premere il pulsante "installa" ed aspettare la fine dell'installazione.


![installa plugin](img/install.jpg)


## Benchmark

Three CHM rasters with the following size have been tested. All CHMs 
have 0.5 m resolution - time for processing using a normal laptop with 8 MB RAM 
and a i7 processor 3 GHz is reported.
is reported  
- X: 3845 Y: 2838 - (50 MB)  - 2 secondi
- X: 4506 Y: 5770 - (180 MB) - 13 secondi
- X: 27413 Y: 19240 (4.6 GB)-

NB 
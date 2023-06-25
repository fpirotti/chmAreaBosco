# Da CHM a Area Bosco
![alt text](logo.png)

## Descrizione  

Il plugin CHM => Bosco converte un livello raster con il modello delle 
chiome (CHM - Canopy Height Model) in un raster binario dove 0=non bosco 
e 1=bosco. Vengono utilizzati diversi parametri per definire 
le caratteristiche del bosco.

Il peso del plugin è circa 110 MB in quanto include la libreria 
grafica [OpenCV - *Open Source Computer Vision Library*](https://it.wikipedia.org/wiki/OpenCV) (109 MB)
che consente elaborazioni ottimizzate su immagini raster.

## INPUT
 - Un raster CHM ovvero i modelli delle chiome. 
Questo raster deve necessariamente essere accurato, 
in quanto fornisce l'informazione di base per la 
creazione dell'area a bosco.
 - Un raster binario BOSCO* (pixel con valore 1 = pixel bosco) [OPZIONALE]: 
il valore 1 del pixel di questo raster verrà considerato bosco a prescindere 
dal risultato del plugin, ovvero questa informazione avrà priorità
nella definizione bosco. 
 - Un raster binario NON BOSCO* (pixel con valore 1 = pixel NON bosco) [OPZIONALE]: 
il valore 1 del pixel di questo raster verrà considerato non bosco a prescindere 
dal risultato del plugin, ovvero questa informazione avrà priorità
nella definizione di aree da escludere dall'area bosco. 
- Soglia altezza chioma (m) - l'altezza della chioma minima per definire il pixel
come appartenente ad un albero.
- Densità copertura (%) - La proporzione minima coperta da chioma perchè l'area venga inclusa
come bosco.
- Area minima (m2) - L'area minima per definire un'area a bosco.
- Larghezza minima (m) - L'area minima per definire un'area a bosco.


        * Attenzione - i due raster binari Bosco e Non Bosco devono avere
        valori zero (0) per i pixel non appartenenti alla cateogria, 
        e un numero diverso da zero (preferibilmente 1) per i pixel 
        appartenenti alla categoria. Ad esempio si può ottenere un raster 
        "Non Bosco" da poligoni che rappresentano le aree urbanizzate 
        facendo la conversione da formato vettoriale a raster 
        (mediante il comando nel menù raster==>Conversione==>Rasterizza)
        
**NB:** nel caso di utilizzo di entrambi i raster "binari", in caso di 
valori in conflitto ovvero discordanti, viene data priorità al raster non-bosco
(vedi esempio sotto)

![Esempio di bosco e non bosco](img/mask.png)

## Installazione  

Scaricare il file compresso [al link GITHUB](https://github.com/fpirotti/chmAreaBosco/releases)

Andare sul menù QGIS "Plugins"=>"Gestisci ed Installa Plugins" e selezionare 
"Installa da ZIP" nella parte sinistra della finestra ed il file compresso scaricato.
Premere il pulsante "installa" ed aspettare la fine dell'installazione.

![installa plugin](img/install.png)
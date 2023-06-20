# Da CHM a Area Bosco
![alt text](logo.png)

Il plugin CHM => Bosco 

INPUT
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
- Soglia altezza chioma (m) - l'altezza della chioma per definire il pixel appartenente ad un albero.


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

![Esempio di bosco e non bosco](mask.png)
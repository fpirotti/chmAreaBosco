# Da CHM a Area Bosco

Il plugin CHM => Bosco 

INPUT
 - Un raster CHM ovvero i modelli delle chiome. 
Questo raster deve necessariamente essere accurato, 
in quanto fornisce l'informazione di base per la 
creazione dell'area a bosco.
 - Un raster binario BOSCO (pixel con valore 1 = pixel bosco) [OPZIONALE]: 
il valore 1 del pixel di questo raster verrà considerato bosco a prescindere 
dal risultato del plugin, ovvero questa informazione avrà priorità
nella definizione bosco. 
 - Un raster binario NON BOSCO (pixel con valore 1 = pixel NON bosco) [OPZIONALE]: 
il valore 1 del pixel di questo raster verrà considerato non bosco a prescindere 
dal risultato del plugin, ovvero questa informazione avrà priorità
nella definizione di aree da escludere dall'area bosco. 
- Altezza minima definizione albero - l'altezza della chioma per definire il pixel appartenente ad un albero.
- 
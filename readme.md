# TNTVillage Searcher
Questo plugin permette di cercare i film su [TNTVillage](http://tntvillage.scambioetico.org) tramite CouchPotato

## SETUP
Prima di tutto occorre sapere la cartella in cui sono contenuti i file di CouchPotato. Potete trovarla in Settings -> About -> Directories

Per questo esempio la mia sarà `/opt/CouchPotato`
```
cd /opt/CouchPotato/custom_plugins
git clone https://github.com/andyts93/CouchPotato-TNTVillage.git tntvillage
# restart CouchPotato
sudo service couchpotato restart
```

Il plugin ha una fuzione di traduzione dei titoli dei film dal titolo originale all'italiano tramite le api di TMDB. Per far sì che venga tentata la traduzione prima della ricerca su TNTVillage aggiungere nelle impostazioni del searcher la propria [api key di tmdb](https://www.themoviedb.org/faq/api)



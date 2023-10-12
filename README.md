# Commande en ligne pour l'API SNCF avec Home Assistant

## Requis : 
 - Avoir une clé pour l'<a href="https://numerique.sncf.com/startup/api/">API SNCF </a> : https://numerique.sncf.com/startup/api/token-developpeur/
 - Pour la création de tableau dans le tableau de bord : <a href="https://github.com/PiotrMachowski/Home-Assistant-Lovelace-HTML-Jinja2-Template-card">Lovelace HTML Jinja2 Template card </a>

## Adaptation
 - Définir les gares de départ ville1 et d'arrivée ville2, à partir du données dans "gares.csv". Par exemple, "Paris - Montparnasse - Hall 1 & 2" est noté avec l'ID stop_area:SNCF:87391003. Comme toutes les gares commencent par "stop_area:SNCF:", ville1 n'a à définir qu'avec son numéro ; ici 87391003
 - Pour un train spécifique, il faut aussi indiquer son numéro.
 
## Utilisation
 - Ajouter le code de command_line dans votre config.yaml
 - Ajouter le tableau d'affichage dans le tableau de bord à partir de l'exemple fourni
	- Remplacer le 'sensor.prochains_ter_ville1_ville2' par celui correspondant à celui créé par le command_line précédent.

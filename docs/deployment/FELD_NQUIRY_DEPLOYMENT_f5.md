# FELDDEFINITION
## NQUIRY auf Zielserver ausbringen

```text
FASSUNG DIESER DATEI:
f5, 26.09.2026, 00:40
ES GILT IMMER DIE HOECHSTE FASSUNG. Aeltere Fassungen sind erledigt,
auch wenn sie noch herumliegen.
AENDERUNGEN GEGEN f4:
A5 beantwortet, aus dem Repository, nicht durch Entscheidung
A8 beantwortet, mit einem benannten Delta und einem Rueckfallweg
ein Befund aus f1 bis f4 war falsch und ist unter 19c berichtigt
Doppelungen in 9.3 gestrichen
```

Nach SYSTEM FIELD ENGINEERING OPERATING MANUAL v1.4, Teil II.
Erstellt aus der Rekonstruktion des Repositories, nicht aus Annahme.

Diese Datei ist der Handlungsraum, nicht die Handlungsanweisung. Was hier
nicht steht und sich aus dem Feld ableiten lässt, entscheidet der
ausführende Agent selbst. Was sich nicht ableiten lässt, steht unter
AUTORITÄTSFRAGEN und ist vor Beginn zu klären.

---

## 0. WAS BEREITS REKONSTRUIERT IST

Aus dem Repository abgeleitet. Nicht erneut zu erfragen.

```text
REPOSITORY:
https://github.com/SYNTX-SYSTEM/NQUIRY
STACK:
Python 3.13 / FastAPI, TypeScript / Next.js 16, PostgreSQL 17
AUFBAU:
Monorepo. apps/api, apps/web, apps/worker, packages, migrations
ORCHESTRIERUNG:
docker-compose.yml. postgres ohne Profil, api/worker/web unter Profil app
BILDER:
infra/local/{api,web,worker}.Dockerfile
MIGRATIONEN:
Alembic, Prüfung über scripts/verify_migrations.py
AUTORITATIVE BETRIEBSBESCHREIBUNG:
docs/RUNTIME_OPERATION.md
DAS REPOSITORY FOLGT SELBST SFE:
docs/architecture/20_SYSTEM_FIELD_ENGINEERING.md
```

### 0.1 Was das Repository über sich selbst sagt

Das ist der wichtigste Befund der Rekonstruktion und verändert das Feld.

```text
STATUS LAUT README:
ARCHITECTURAL PROTOTYPE
KEINE BEHAUPTUNG VON:
Produktionsreife, Regulierungskonformität, Datenschutzfreigabe,
Providerfreigabe, Sicherheitszertifizierung, Systemvalidierung
```

Materielle Folgen, alle aus dem Repository belegt:

```text
apps/web wird im Containerbild mit npm run dev gestartet
apps/worker startet, protokolliert und endet mit 0, es gibt keine
  laufende Produktionsschleife
es gibt keine Produktionsauthentifizierung, nur einen lokalen
  Credential-Adapter, GAP-14-001 ist offen
der einzige KI-Provider ist MockProviderAdapter
die voreingestellten Zugangsdaten heissen woertlich
  nquiry_local_dev_only
infra/ enthaelt ausschliesslich local/, infra/ci/ ist leer
```

Gesetz:

```text
LAUFFÄHIG
!=
PRODUKTIONSREIF
```

Das Feld heisst deshalb nicht "NQUIRY in Produktion nehmen". Es heisst
"einen erklärten Prototypen auf einem geteilten Server lauffähig machen,
ohne den Server zu beschädigen und ohne den Prototypen als etwas
auszugeben, was er nicht ist".

### 0.2 Was aus öffentlichen Verzeichnissen ermittelt ist

Passive Auflösung und Reverse-Eintrag, am 25.09.2026. Keine Probe am
Host, kein Port, kein Scan. Nicht erneut zu erfragen, aber am Server zu
bestätigen, weil eine öffentliche Auflösung nicht beweist, welche
Maschine hinter der Adresse antwortet.

```text
condyn.eu, www.condyn.eu:
loesen beide auf 49.13.3.21 auf
REVERSE-EINTRAG VON 49.13.3.21:
static.21.3.13.49.clients.your-server.de
DARAUS ABLEITBAR:
ein Hetzner-Server, Kundenbereich, Standort Deutschland.
Kein geteiltes Hosting, sondern eine eigene Maschine. Das deckt sich
mit der Angabe, dass dort bereits viele Anwendungen laufen.
AUTORITATIVE NAMENSSERVER VON condyn.eu:
ns71.domaincontrol.com, ns72.domaincontrol.com
DARAUS ABLEITBAR:
die Zone wird nicht auf dem Server verwaltet, sondern beim Registrar.
Ein DNS-Eintrag ist deshalb ueber SSH nicht setzbar.
nquiry.condyn.eu:
loest auf 49.13.3.21 auf, A-Eintrag, TTL 1800. Der Eintrag ist am
25.09.2026 vom Eigentuemer beim Registrar angelegt und oeffentlich
bestaetigt worden. Er zeigt auf dieselbe Adresse wie condyn.eu, also
auf denselben Rechner. Damit ist die Vorbedingung fuer die
Zertifikatsausstellung erfuellt.
EIN PLATZHALTEREINTRAG DER ZONE:
existiert nicht. Eine erfundene Unteradresse ergibt NXDOMAIN. Die
Auflösung von nquiry.condyn.eu ist also ein echter Eintrag und kein
Nebeneffekt eines Platzhalters.
KEIN AAAA-EINTRAG:
condyn.eu hat keinen. Der Dienst wird ueber IPv4 erreicht, die
Subdomain ebenso. Ein AAAA-Eintrag ist nicht anzulegen.
```

Gesetz:

```text
DER NAME LIEGT AUSSERHALB DES SERVERS
!=
DER NAME LIEGT AUSSERHALB DES FELDES
```

Der Name ist Teil des Feldes, denn ohne ihn wird MUST BECOME TRUE nicht
wahr. Er ist nur nicht mit dem Werkzeug des Agenten erreichbar. Das ist
genau der Unterschied zwischen einer Aufgabe und einem Haltegrund.

---

## 1. FIELD

```text
Die Ausbringung des Repositories NQUIRY als eigenständige, isolierte
Anwendung auf einem bereits genutzten Zielserver, in einem eigenen
Verzeichnis unter /opt, mit eigenem Docker-Projekt, eigener Datenbank
und eigenen Ports.
```

## 2. ZWECK

```text
Der Prototyp soll auf dem Zielserver erreichbar laufen, damit an ihm
weitergearbeitet und er vorgeführt werden kann.
```

## 3. SCOPE

```text
/opt/nquiry als Anwendungsverzeichnis
der Git-Klon und seine Aktualisierung
ein eigenes Docker-Compose-Projekt mit eigenem Projektnamen
ein eigener PostgreSQL-Container mit eigenem Volume
die Alembic-Migrationen dieses Projekts
die .env-Datei dieses Projekts
die Erreichbarkeit dieser Anwendung
```

## 4. NICHT IM SCOPE

```text
jede andere Anwendung auf dem Server
jede gemeinsam genutzte Datenbankinstanz
die Konfiguration des vorhandenen Reverse Proxy, ausser einem
  ausdruecklich freigegebenen zusaetzlichen Eintrag
Zertifikate anderer Anwendungen
Systemdienste, Kernelparameter, Firewallregeln ausser einer
  ausdruecklich freigegebenen Portfreigabe
jede Änderung am Quellcode des Repositories
jede Behebung der offenen HARD-DEP und GAP des Repositories
```

Gesetz:

```text
DEPLOYMENT DES FELDES
!=
ÄNDERUNG DES ANWENDUNGSFELDES
```

Stellt der Agent fest, dass das Repository geändert werden müsste, endet
dieses Feld. Die Änderung ist ein eigenes Delta mit eigener Work Unit.

## 5. AUTORITATIVER ZUSTAND

```text
Der Zustand des Zielservers vor der ersten materiellen Handlung, wie er
unter REKONSTRUKTIONSAUFTRAG erhoben wird. Nicht die Erinnerung daran,
nicht die Beschreibung in dieser Datei.
```

## 6. PRODUCER UND CONSUMER

```text
PRODUCER:
das Repository, die Containerbilder, die Migrationen, die .env
CONSUMER:
der Browser über den Reverse Proxy, die anderen Anwendungen des Servers
  ausschliesslich über gemeinsame Ressourcen wie Port, Platte, Speicher
```

## 7. MATERIELLE RELATIONEN

```text
Anwendung zu Port
Anwendung zu Reverse Proxy
Anwendung zu eigener Datenbank
Anwendung zu Plattenplatz und Speicher
Anwendung zu Docker-Daemon
Docker-Daemon zu allen anderen Anwendungen des Servers
```

Die letzte Relation ist die gefährlichste des ganzen Feldes. Der
Docker-Daemon ist geteilt. Jeder Befehl ohne Projektbindung wirkt auf
alles.

## 8. ERLAUBTES DELTA

```text
Verzeichnis /opt/nquiry anlegen
Repository hineinklonen oder aktualisieren
.env aus infra/local/.env.example ableiten und mit eigenen Werten fuellen
Containerbilder dieses Projekts bauen
Container dieses Projekts starten, stoppen, neu starten
Alembic-Migrationen gegen die eigene Datenbank ausfuehren
einen zusaetzlichen Eintrag im Reverse Proxy anlegen, nur nach Freigabe
infra/local/web.Dockerfile auf Produktionsbau umstellen, freigegeben,
  Umfang und Rueckfall stehen unter A8. Keine andere Datei des
  Repositories, auch nicht zur Behebung eines Baufehlers
```

## 9. BOUNDARY

Die Boundary ist nach dem Schaden geordnet, den sie verhindert, nicht
nach dem Ablauf. Die ersten drei Gruppen koennen den Server als Ganzen
treffen. Sie gelten deshalb vor allen anderen.

### 9.1 Der Reverse Proxy

Der gefaehrlichste Schritt der ganzen Ausbringung. Ein fehlerhafter
Eintrag nimmt nicht diese Anwendung vom Netz, sondern alle.

Die Zusage, aus der alles Weitere folgt:

```text
JEDER FEHLVERSUCH AM PROXY LAESST DIE VORIGE KONFIGURATION BEDIENEN
Schlaegt ein Versuch fehl, antwortet danach dieselbe Konfiguration wie
vorher, und zwar von selbst, ohne einen weiteren Eingriff.
```

Die Boundary, die daraus nicht folgt und deshalb hier steht:

```text
nur eine neue eigene Datei, niemals eine bestehende Datei
kein Eingriff in die Hauptkonfiguration, auch nicht additiv
keine Veraenderung bestehender Eintraege, auch nicht ihrer Reihenfolge
nach jedem Uebernehmen ist condyn.eu abzurufen, bevor irgendetwas
  anderes geschieht
```

Welcher Befehl die Zusage einhaelt, steht hier nicht. Der Agent leitet
es ab, aus der Betriebsart des vorhandenen Proxy und aus seinen
Protokollen. Er hat dabei nur eine Richtung: eine Eskalation geht zum
schwaecheren Eingriff, nicht zum staerkeren. Ein Versuch, der den
laufenden Zustand aufgibt, um einen fehlgeschlagenen Versuch zu
beheben, verletzt die Zusage, gleich wie gut er gemeint ist. Das ist
keine Vorliebe, sondern nachrechenbar: ein Eingriff, der die laufende
Konfiguration verwirft, hat sie nicht mehr, wenn die neue nicht
annimmt.

Gesetz:

```text
ESKALATION NACH OBEN
!=
ESKALATION
```

### 9.2 Das Zertifikat

```text
keine Veraenderung bestehender Zertifikate
kein Erneuerungszwang, in keiner Variante
kein Zertifikatswerkzeug in einem Modus, der Proxy-Eintraege selbst
  umschreibt. Nur Ausstellung, nicht Einbau. Der Einbau steht in der
  eigenen Datei aus 9.1
keine Umleitung, die das Werkzeug von sich aus in fremde Eintraege setzt
hoechstens zwei Ausstellungsversuche. Ein drittes Fehlschlagen ist ein
  Haltegrund
```

### 9.3 Der Rechner selbst

Systempakete, Firewall, Benutzer und Gruppen, systemd, crontab,
authorized_keys und der Docker-Daemon stehen nicht hier, sondern in
Abschnitt 12, als Zusage, dass sie unveraendert bleiben. Eine Zusage
ist die staerkere Form, weil sie pruefbar ist und ein Verbot nicht.
Dasselbe zweimal aufzuschreiben, einmal als Invariante und einmal als
Verbot, macht die Datei laenger und das Feld nicht enger.

Hier bleibt nur, wofuer es keine Aufnahme eines Vorzustands gibt:

```text
keine Aenderung an Rechnername, Zeitzone, Sprachumgebung
kein Eintrag in /etc/hosts und kein DNS-Eintrag. Ein Name, der nicht
  aufloest, wird nicht oertlich vorgetaeuscht
```

### 9.4 Fremde Anwendungen und pm2

```text
jeder docker- und docker-compose-Befehl traegt -p nquiry
kein docker system prune, kein docker volume prune, kein docker
  container prune, in keiner Variante
kein Neustart, Stopp oder Eingriff an einem Container, der nicht zum
  Projekt nquiry gehoert
kein Anschluss an ein bestehendes fremdes Docker-Netz
kein network_mode host
kein pm2-Prozess wird gestoppt, neu gestartet, geloescht, umbenannt
  oder in seiner Konfiguration beruehrt
kein pm2 save und kein pm2 startup
NQUIRY wird nicht unter pm2 eingetragen, solange A11 nicht beantwortet
  ist
```

### 9.5 Ports und Sichtbarkeit

```text
keine Belegung eines Ports, der bereits belegt ist
die Ports dieses Projekts binden auf 127.0.0.1, nicht auf 0.0.0.0
```

Die zweite Zeile ist keine Feinheit. Der Prototyp hat keine
Produktionsauthentifizierung, GAP-14-001 ist offen. Bindet er auf alle
Schnittstellen, ist er unter der nackten Adresse und seinem Port
erreichbar, und zwar an jedem Schutz vorbei, den der Proxy traegt. Die
Bindung auf die Rueckschleife ist der Grund, warum eine Antwort auf A5
den Zugang tatsaechlich regelt und nicht nur den Vorderweg.

### 9.6 Das Repository

```text
kein git push, kein Anlegen einer Marke oder eines Zweiges auf der
  Gegenseite
keine Aenderung am Quelltext, solange kein eigenes Delta freigegeben ist
kein git config --global
```

### 9.7 Geheimnisse

```text
kein Geheimnis in einer versionierten Datei
kein Geheimnis im Bericht, in einer Protokollzeile, in einem
  Befehlsecho und in keiner Fehlermeldung
keine Voreinstellung des Repositories wird als Kennwort uebernommen
```

### 9.8 Schreiben und Loeschen

```text
kein Schreiben ausserhalb von /opt/nquiry, ausser der einen
  freigegebenen Proxy-Datei
kein Loeschen ausserhalb von /opt/nquiry, ohne Ausnahme
kein Rueckbau mit Volumenverlust. Ein Abbau nimmt die Container, nicht
  das Volumen. Das Volumen wird nur auf ausdrueckliche Weisung entfernt
```

### 9.9 Was hier absichtlich nicht steht

Eine Boundary, die der Agent auf dem Server sehen kann, ist keine
Boundary, sondern eine Erhebung. Sie gehoert in Abschnitt 15 und nicht
hierher. Die Pruefung fuer jede Zeile oben lautet deshalb:

```text
KANN FABLE DAS AUF DEM SERVER SEHEN
→ JA  → Erhebung, Abschnitt 15, hier streichen
→ NEIN → Boundary, hier stehen lassen
```

Nach dieser Pruefung sind bewusst nicht aufgenommen, obwohl sie
zunaechst hier standen:

```text
die Schreibweise des Proxy-Eintrags
  sichtbar am Muster der vorhandenen Eintraege
der Weg, auf dem Zertifikate bezogen werden
  sichtbar an der vorhandenen Einrichtung
die Rechte der eigenen Dateien
  ableitbar aus dem Umstand, dass ein Kennwort darin steht
die Begrenzung der Protokollgroesse
  ableitbar aus der Zusage, dass der Plattenplatz oberhalb der Grenze
  bleibt
die Pflicht, nichts als Erfolg zu melden, was nicht gezeigt wurde
  steht in Abschnitt 21 und gilt fuer jedes Feld dieser Methode
```

Gesetz:

```text
EINE ABLEITBARE REGEL IM FELD
!=
EINE REGEL
```

Sie ist dort Ballast. Sie macht die Datei laenger, das Feld nicht
enger, und sie erzeugt den Eindruck von Vollstaendigkeit an einer
Stelle, an der Vollstaendigkeit nicht das Ziel ist.

## 10. AUTHORITY

```text
Der Eigentuemer des Servers. Alles unter AUTORITÄTSFRAGEN ist seine
Entscheidung und nicht die des Agenten. Das Fehlen einer Antwort ist
keine Erlaubnis.
```

### 10.1 Was der Agent frei waehlt

Alles, was hier nicht eingeschraenkt ist. Ausdruecklich und ohne
Rueckfrage:

```text
die beiden Ports, die Namen der Container, der Netze und des Volumens
den Aufbau der eigenen Compose-Datei
die Reihenfolge der Schritte innerhalb des Ablaufs
die Werkzeuge der Erhebung
die Behandlung jedes Fehlers, der nur dieses Projekt betrifft
```

### 10.2 Wann er waehlt und wann das Feld waehlt

Es gibt nur ein Kriterium, und es ist nicht Wichtigkeit und nicht
Gefahr, sondern die Bezahlbarkeit des Fehlversuchs:

```text
IST DER FEHLVERSUCH BILLIG UND UMKEHRBAR
→ JA  → der Agent probiert es aus, waehlt selbst, berichtet danach
→ NEIN → das Feld nennt die Zusage, nicht den Befehl. Der Agent leitet
         den Weg ab, der sie einhaelt, und probiert nicht an ihr vorbei
```

Ein belegter Port ist ein billiger Fehlversuch. Die Bindung schlaegt
fehl, nichts ist geschehen, der Agent nimmt den naechsten. Deshalb
steht im Feld kein Port, sondern nur die Zusage, dass kein belegter
belegt wird.

Am Proxy ist der erste Versuch billig und der zweite teuer, und beide
sehen von aussen gleich aus. Deshalb darf der Agent probieren, aber die
Probe darf den laufenden Zustand nicht als Pfand einsetzen. Ein Versuch,
der die laufende Konfiguration verwirft, ist kein Versuch mehr: gelingt
die neue nicht, ist auch die alte fort, und der Fehlschlag laesst sich
nicht mehr durch Zuruecknehmen beheben, sondern nur noch durch
Reparieren unter Zeitdruck. Das ist der Unterschied zwischen einer
Probe und einer Wette.

Dasselbe Muster beim Zertifikatsantrag, dessen Fehlschlag ein
Kontingent verbraucht, das niemand zurueckgibt, und bei jeder Aenderung
am System, die sich nicht in einem Schritt zuruecknehmen laesst.

Der Agent darf jedes Protokoll lesen, jederzeit, und er soll es auch.
Ein Protokoll erklaert einen Fehlschlag. Es macht keinen Versuch
umkehrbar, der es nicht ist. Die Lesbarkeit der Ursache und die
Bezahlbarkeit des Versuchs sind zwei verschiedene Dinge, und nur das
zweite entscheidet, ob eine Probe erlaubt ist.

Gesetz:

```text
ES GELINGT
!=
ES WAR ERLAUBT
```

---

## 11. MUST BECOME TRUE

```text
/opt/nquiry existiert und enthaelt den Klon des Repositories
ein Docker-Compose-Projekt namens nquiry laeuft
die eigene PostgreSQL-Instanz ist gesund und traegt das aktuelle Schema
die API antwortet auf /healthz
die Weboberflaeche liefert ihre Startseite aus
die gewaehlte Erreichbarkeit ist hergestellt und nachgewiesen
die verwendeten Ports, Namen und Pfade sind schriftlich festgehalten
```

## 12. MUST REMAIN TRUE

Der wichtigste Abschnitt dieser Datei. Der Server traegt fremde
Anwendungen, und deren Weiterlaufen ist keine Nebenbedingung, sondern
das eigentliche Schutzgut.

Namentlich und vor allem anderen:

```text
condyn.eu liefert vor, waehrend und nach der Ausbringung aus
die Structural Analysis Engine dort bleibt bedienbar, einschliesslich
  ihrer PDF-Ausgabe
das Zertifikat von condyn.eu bleibt unveraendert und gueltig
der Reverse-Proxy-Eintrag von condyn.eu bleibt byteweise unveraendert
der Container oder Dienst hinter condyn.eu wird nicht gestoppt, nicht
  neu gestartet, nicht neu gebaut
```

Dies ist ein Feld mit einem laufenden, oeffentlich erreichbaren Dienst
darin. Eine Ausbringung, die NQUIRY zum Laufen bringt und condyn.eu auch
nur fuer eine Minute unterbricht, ist gescheitert, gleich wie gut NQUIRY
danach laeuft.

Darueber hinaus:

```text
jede andere Anwendung des Servers laeuft nach der Ausbringung
  unveraendert weiter
kein fremder Container wurde gestoppt, neu gestartet oder entfernt
kein pm2-Prozess wurde gestoppt, neu gestartet, geloescht oder in
  seiner Konfiguration veraendert
pm2 save wurde nicht aufgerufen, solange fremde Prozesse in der Liste
  stehen
kein fremdes Volume wurde beruehrt
kein fremdes Netzwerk wurde beruehrt
jeder vorher belegte Port ist danach von derselben Anwendung belegt
jeder bestehende Reverse-Proxy-Eintrag ist unveraendert
jedes bestehende Zertifikat ist unveraendert
der Docker-Daemon lief durchgehend
freier Plattenplatz bleibt oberhalb der vor Beginn festgelegten Grenze
die Firewall-Regeln sind unveraendert
die Liste der systemd-Einheiten ist unveraendert
die Liste der crontab-Eintraege ist unveraendert
Benutzer, Gruppen und Gruppenzugehoerigkeiten sind unveraendert
die installierten Systempakete sind unveraendert
authorized_keys und die SSH-Konfiguration sind unveraendert
kein Port dieses Projekts ist von aussen erreichbar. Erreichbar ist
  allein der Weg ueber den Proxy
```

Jede dieser Zeilen ist nur pruefbar, wenn ihr Vorzustand festgehalten
wurde. Deshalb steht in Abschnitt 16 fuer jede von ihnen eine Aufnahme.
Eine Erhaltungszusage ohne Vorzustand ist eine Behauptung.

## 13. MUST REMAIN IMPOSSIBLE

```text
ein Befehl wirkt unbeabsichtigt auf ein fremdes Docker-Projekt
die Anwendung ist oeffentlich erreichbar, ohne dass das freigegeben wurde
die Voreinstellungen aus dem Repository gelangen in den Betrieb
eine fremde Datenbank wird migriert
ein Geheimnis liegt in Git oder in einer Weltleserechte-Datei
die Demo-Fixtur wird als Nachweis richtigen Verhaltens ausgegeben
```

## 14. FALSIFIER

```text
condyn.eu antwortet nach dem Start nicht mehr oder langsamer als
  in der Baseline
nach dem Start antwortet eine fremde Anwendung nicht mehr
docker ps zeigt vor und nach der Ausbringung eine unterschiedliche
  Menge fremder Container
ein Portscan zeigt einen vorher freien Port als belegt, ohne dass er
  diesem Projekt zugewiesen wurde
die Datenbank enthaelt Tabellen, die nicht aus den Migrationen dieses
  Repositories stammen
/healthz antwortet, die Weboberflaeche aber nicht, oder umgekehrt
```

---

## 15. REKONSTRUKTIONSAUFTRAG

Diese Angaben sind auf dem Server ableitbar. Sie werden nicht erfragt,
sondern erhoben, und zwar vollstaendig, bevor irgendetwas geschrieben
wird. Das Ergebnis wird als Baseline abgelegt.

```text
1. Betriebssystem, Version, Architektur
2. Docker- und Compose-Version, laeuft der Daemon ueberhaupt. Der
   Server wird mit pm2 betrieben; es ist nicht vorausgesetzt, dass
   Docker vorhanden ist. Ist es nicht vorhanden, ist das ein Haltegrund
   und keine Installationsaufgabe.
2a. pm2 list und pm2 status, vollstaendig, mit Prozessnamen und Ports
2b. unter welchem Benutzer pm2 laeuft und ob es beim Systemstart
    wiederhergestellt wird
3. docker ps -a, vollstaendig, mit Projektbezeichnern
4. docker volume ls und docker network ls, vollstaendig
5. alle belegten TCP-Ports mit dem jeweiligen Prozess, aus der Sicht
   des Hosts und aus der Sicht der Container. Auf 3000 laeuft nach
   Angabe des Eigentuemers bereits etwas; das ist zu bestaetigen und
   nicht zu unterstellen. Es wird kein belegter Port belegt.
5a. ob nquiry.condyn.eu vom Server aus aufloest und worauf. Erwartet
    wird 49.13.3.21, so wie es am 25.09.2026 oeffentlich bestaetigt
    wurde, siehe 0.2. Loest der Name nicht auf oder zeigt er
    anderswohin, ist das ein Haltegrund und keine Umleitungsaufgabe.
    Der Agent legt keinen DNS-Eintrag an und aendert keinen, auch nicht
    in /etc/hosts.
5b. ob die oeffentliche Adresse des Servers mit 49.13.3.21
    uebereinstimmt. Weicht sie ab, ist der Zielrechner nicht der
    Rechner, der condyn.eu ausliefert, und A1 ist erneut offen.
6. welcher Reverse Proxy tatsaechlich laeuft, mit Konfigurationspfad
7. wie die vorhandenen Anwendungen dort eingetragen sind, als Muster,
   und welcher Container oder Dienst genau condyn.eu ausliefert
8. wie Zertifikate bezogen und erneuert werden, mit welchem Werkzeug,
   in welchem Modus, und ob fuer condyn.eu bereits ein Zertifikat
   vorliegt, mit welcher Laufzeit und welcher Erneuerungsart
8a. wie die vorhandenen Anwendungen ihre Ports binden, auf alle
    Schnittstellen oder auf die Rueckschleife. Das Muster ist zu
    uebernehmen, sofern es die Rueckschleife ist
9. freier Plattenplatz, freier Arbeitsspeicher
10. Inhalt von /opt, welche Namen bereits vergeben sind
11. laeuft bereits ein PostgreSQL auf dem Server, in welcher Form
12. wer darf schreiben, unter welchem Benutzer laeuft Docker
```

Aus dieser Erhebung leitet der Agent selbst ab und fragt nicht nach:

```text
zwei freie Ports fuer Web und API
den Projektnamen, falls nquiry in /opt bereits vergeben ist
die Schreibweise des Proxy-Eintrags, nach dem Muster der vorhandenen
ob genug Platz und Speicher vorhanden ist
```

Gesetz:

```text
NICHT ABLEITBAR FÜR DEN AUTOR DIESER DATEI
!=
NICHT ABLEITBAR AUF DEM SERVER
```

## 16. BASELINE EVIDENCE

Vor der ersten materiellen Handlung abzulegen unter
`/opt/nquiry/_baseline/` mit Zeitstempel:

```text
docker ps -a
docker volume ls
docker network ls
die vollstaendige Portbelegung
die Konfigurationsdateien des Reverse Proxy, unveraendert kopiert
df -h und free -m
eine Abrufprobe von condyn.eu mit Statuscode und Antwortzeit
pm2 list und pm2 status, vollstaendig
die Firewall-Regeln, vollstaendig
die Liste der systemd-Einheiten und der crontab-Eintraege
die Gruppenzugehoerigkeiten der handelnden Kennung
die Liste der installierten Systempakete
die Pruefsumme von authorized_keys und der SSH-Konfiguration
die Liste der vorhandenen Zertifikate mit ihren Laufzeiten
```

Zu jeder Aufnahme wird eine Pruefsumme abgelegt. Die Aufnahme allein
zeigt den Vorzustand; erst die Pruefsumme macht die Aussage
"unveraendert" pruefbar, ohne beide Zustaende von Hand zu vergleichen.

Gesetz:

```text
EINE ERHALTUNGSZUSAGE OHNE VORZUSTAND
!=
EINE ERHALTUNGSZUSAGE
```

## 17. RECOVERABLE PREDECESSOR STATE

```text
Der Vorgaengerzustand dieses Feldes ist: NQUIRY ist auf diesem Server
nicht vorhanden. Er ist wiederherstellbar durch Stoppen und Entfernen
des Projekts nquiry, Loeschen von /opt/nquiry und Ruecknahme des einen
Proxy-Eintrags.
```

Wird der Reverse Proxy angefasst, gilt zusaetzlich:

```text
die betroffene Konfigurationsdatei wird vor der Aenderung kopiert
die Kopie liegt in _baseline und wird im Abschlussbericht genannt
```

## 18. STATE ISOLATION

```text
eigener Compose-Projektname nquiry
eigenes Volume, eigenes Netzwerk
die PostgreSQL-Instanz wird nicht auf den Host veroeffentlicht, sie ist
  nur im Projektnetz erreichbar
kein Seed der Demo-Fixtur, ausser er ist ausdruecklich freigegeben
```

---

## 19. VORWEGGENOMMENE AUTORITÄTSFRAGEN

Diese Punkte folgen aus nichts. Weder aus dem Repository noch aus dem
Server. Sie sind vor Beginn zu beantworten. Ohne Antwort beginnt keine
materielle Handlung.

```text
A1 ZIEL: BEANTWORTET
Der Rechner, der condyn.eu ausliefert. Der oeffentliche Schluessel des
ausfuehrenden Rechners liegt dort bereits. Host, Benutzer und Port sind
damit nicht zu erfragen, sondern abzuleiten: aus ~/.ssh/config, sonst
aus der oeffentlichen Aufloesung von condyn.eu. Gibt es mehrere
Kandidaten, ist das ein Haltegrund und keine Wahl des Agenten.

A2 ERREICHBARKEIT:
nur ueber SSH-Tunnel, nur im internen Netz, oder oeffentlich

A3 NAME: BEANTWORTET
https://nquiry.condyn.eu, eine eigene Subdomain. Damit ist A12 mit
Weg a beantwortet und der Befund aus 19a aufgeloest. Siehe 19b.
Die Schreibweise ist am 25.09.2026 vom Eigentuemer festgelegt worden
und lautet nquiry, wie das Repository. Frueher genannte Schreibweisen
inquery und inquiry sind damit erledigt und stehen nirgends mehr in
dieser Datei. Der ausfuehrende Agent traegt genau diesen Namen ein und
leitet keine Abwandlung davon ab.
Der DNS-Eintrag war die einzige Vorbedingung, die der Agent nicht
selbst erfuellen kann, weil die Zone bei ns71/ns72.domaincontrol.com
liegt und nicht auf dem Server. Sie ist erfuellt: A-Eintrag
nquiry -> 49.13.3.21, am 25.09.2026 vom Eigentuemer angelegt und
oeffentlich bestaetigt. Siehe 0.2.
Damit ist der Wartezustand vor der Zertifikatsausstellung aufgehoben.
Der Agent bestaetigt die Aufloesung dennoch selbst, vom Server aus,
bevor er ein Zertifikat anfordert. Ein Eintrag, der aus dem Netz
sichtbar ist, muss es aus der Sicht des Servers nicht sein, und ein
fehlgeschlagener Zertifikatsantrag zaehlt bei der ausstellenden Stelle
gegen ein Kontingent. Bestaetigt wird also vorher, nicht hinterher.

A4 TLS:
ueber den vorhandenen Proxy mit vorhandenem Verfahren, oder gar nicht

A5 ZUGANGSSCHUTZ: BEANTWORTET, UND ZWAR VOM REPOSITORY
Die Anwendung bringt eine echte Anmeldung mit. Kein zusaetzlicher
Schutz am Proxy. Die Frage war auf einem falschen Befund gebaut, siehe
19c. Es bleibt allein:

```text
NQUIRY_COOKIE_SECURE=1 ist zu setzen, sonst sendet der Browser das
  Sitzungsmerkmal ueber HTTPS nicht
es gibt keinen offenen Weg, sich selbst ein Konto anzulegen. Wer ein
  Konto braucht, bekommt es ueber die vorgesehene Einrichtung. Der
  Agent legt kein Konto an, solange niemand danach fragt
```

A6 DATENBANK:
eigener Container mit eigenem Volume, wie hier vorgeschlagen, oder eine
vorhandene Instanz. Bei vorhandener Instanz ist das ein anderes Feld

A7 GEHEIMNISSE:
wer erzeugt das Datenbankkennwort und wo wird es abgelegt. Die
Voreinstellung des Repositories heisst nquiry_local_dev_only und darf
nicht uebernommen werden

A8 WEB-BETRIEBSART: BEANTWORTET MIT WEG b, MIT RUECKFALL
Produktionsbau. Der Eigentuemer hat das Delta freigegeben und die
Ausfuehrung dem Agenten ueberlassen. Es ist ein Delta, aber ein
benanntes und ein kleines:

```text
GEAENDERT WIRD GENAU EINE DATEI:
infra/local/web.Dockerfile
WAS DARIN GEAENDERT WIRD:
aus npm run dev wird npm run build beim Bauen und npm run start beim
Starten. Die Anwendung selbst wird nicht angefasst, keine Zeile unter
apps/web/, keine unter apps/api/, keine unter packages/.
```

Zwei Dinge, die daran haengen und die nicht ableitbar sind, weil sie
Next.js eigen sind:

```text
NEXT_PUBLIC_API_BASE_URL wird beim BAUEN eingesetzt, nicht beim
  Starten. Der Wert muss also dem Bau mitgegeben werden. Wird er nur
  als Laufzeitwert gesetzt, ruft die Oberflaeche im Browser weiter
  localhost:8000 auf, und zwar ohne Fehlermeldung im Server
npm run build ist streng, wo npm run dev nachsichtig ist. Ein Prototyp
  kann daran scheitern, an Typen, an Regeln, an einer Seite, die sich
  nicht vorab erzeugen laesst. Das ist kein Mangel der Ausbringung
```

Der Rueckfall, und er folgt aus 10.2, nicht aus einer Erlaubnis: der
Bau ist ein billiger Fehlversuch. Er findet statt, bevor irgendetwas
laeuft, und sein Fehlschlag hinterlaesst nichts.

```text
BAU GELINGT      → Produktionsbild wird ausgebracht
BAU SCHLAEGT FEHL → die eine geaenderte Datei wird zurueckgenommen, es
                    wird mit dem Entwicklungsserver ausgebracht, und
                    der Fehlschlag steht im Bericht mit seiner Ursache
```

Nicht erlaubt ist der dritte Weg, den ein Agent an dieser Stelle
gern nimmt: den Bau gelingen lassen, indem er die Anwendung anpasst.
Eine Regel abschalten, einen Typ aufweichen, eine Seite umschreiben.
Das ist ein anderes Delta und es ist nicht freigegeben.

A9 DEMO-FIXTUR:
soll scripts/seed_local_demo.py laufen. Die erzeugten Daten sind
laut Repository ausdruecklich NON_PROOF und nicht ueber gueltige
Uebergaenge erreichbar

A11 BETRIEBSART AUF DEM SERVER:
Der Server laeuft mit pm2. Das Repository liefert docker-compose.
Soll NQUIRY sein eigenes Docker-Projekt mitbringen, sofern Docker
vorhanden ist, oder soll es der Konvention des Servers folgen und unter
pm2 laufen. Das Zweite waere eine erhebliche Aenderung am Repository
und ein eigenes Feld.

A12 UMGANG MIT DEM BEFUND AUS 19a: BEANTWORTET MIT a
Die Auswahl steht als Provenienz. Siehe 19b fuer die Folgen.
  a) Subdomain nquiry.condyn.eu statt Pfad. Kein basePath noetig,
     kein Cookie-Pfad noetig, der Eintrag von condyn.eu bleibt
     unberuehrt. Es bleiben die zwei Aenderungen, die ohnehin noetig
     sind.
  b) Pfad wie gewuenscht, mit ausdruecklicher Freigabe der vier
     Aenderungen am Repository. Diese Aenderungen sind ein eigenes
     Delta mit eigener Work Unit, vor der Ausbringung, mit eigenem
     Proof.
  c) Pfad, aber zunaechst nur die API unter /nquiry/api, ohne Web.
     Kein basePath, Cookie-Pfad trotzdem noetig.
  d) Ausbringung ohne oeffentliche Erreichbarkeit, nur ueber
     SSH-Tunnel. Kein Eingriff am Proxy, keine Aenderung am
     Repository ausser der API-Basis.

A10 KENNZEICHNUNG:
soll auf der ausgebrachten Oberflaeche sichtbar stehen, dass es sich um
einen ARCHITECTURAL PROTOTYPE handelt
```

---

## 19b. AUFLOESUNG: DIE SUBDOMAIN BRAUCHT KEINE REPO-AENDERUNG

A12 ist mit Weg a beantwortet. Damit entfaellt der gesamte Befund aus
19a. Abschnitt 19a bleibt als Provenienz stehen und gilt nicht mehr.

Die Pruefung des Repositories ergibt: unter der Subdomain ist **keine
einzige Aenderung am Quellcode noetig**, wenn die folgende Topologie
gewaehlt wird. Jede der vier Stellen aus 19a loest sich auf.

### Die Topologie

```text
nquiry.condyn.eu/       → Webdienst dieses Projekts
nquiry.condyn.eu/api/   → API dieses Projekts, Praefix wird beim
                           Weiterreichen entfernt
```

### Warum damit alles wegfaellt

```text
BASEPATH:
entfaellt. Das Web liegt auf der Wurzel seiner eigenen Subdomain.
API-BASIS:
bereits konfigurierbar. apps/web/lib/api/client.ts hat apiBaseUrl(),
das process.env.NEXT_PUBLIC_API_BASE_URL liest und nur ersatzweise auf
localhost zurueckfaellt. Setzen genuegt.
CORS:
entfaellt. Web und API liegen unter derselben Herkunft. Der Browser
stellt keine herkunftsfremde Anfrage, also wird die festgeschriebene
Liste nie befragt.
COOKIE:
entfaellt. Ein Cookie ohne Domain-Angabe gilt nur fuer den Host, der
es setzt. nquiry.condyn.eu erreicht condyn.eu nicht. Die Relation
zwischen den beiden Anwendungen entsteht gar nicht erst.
```

Gesetz:

```text
TOPOLOGIE
!=
QUELLTEXT
```

Eine gut gewaehlte Topologie kann eine Aenderung am Quelltext
ueberfluessig machen. Vier festgeschriebene Stellen, und keine davon
muss angefasst werden.

### Die zu setzenden Umgebungswerte

```text
NEXT_PUBLIC_API_BASE_URL=https://nquiry.condyn.eu/api
NQUIRY_COOKIE_SECURE=1
POSTGRES_PASSWORD=<erzeugt, nicht die Voreinstellung>
DATABASE_URL=<daraus abgeleitet, Host ist der Compose-Dienstname>
```

Hinweis fuer den Agenten: NEXT_PUBLIC_ Werte liest Next beim Start des
Dienstes. Sie gehoeren in die Umgebung des Webdienstes, bevor er
startet. Wird spaeter ein Produktionsbild gebaut, gehoeren sie in den
Bauvorgang.

### Die Proxy-Zusage ist damit wiederhergestellt

```text
condyn.eu bekommt einen eigenen, neuen Serverblock fuer
  nquiry.condyn.eu
der bestehende Serverblock von condyn.eu bleibt byteweise unveraendert
das bestehende Zertifikat von condyn.eu bleibt unberuehrt
fuer die Subdomain wird ein eigenes Zertifikat bezogen, nach dem
  Verfahren, das auf dem Server ohnehin verwendet wird
```

---

## 19d. WEGE OHNE ANTWORT

Beantwortet sind A1, A3, A5, A8 und A12. Fuer die uebrigen gilt: sie
haben einen Weg, den der Agent nehmen darf, wenn keine Antwort kommt,
und dieser Weg ist nicht gewaehlt, weil er bequem ist, sondern weil er
sich aus dem Feld selbst ergibt oder weil er die ruecknehmbare Seite
ist.

```text
A2 ERREICHBARKEIT
  beantwortet durch A3. Eine oeffentliche Subdomain ist die Antwort.
A4 TLS
  dem Verfahren des Servers folgen, das die Erhebung zeigt. Ein
  zweites Verfahren wird nicht daneben gestellt.
A6 DATENBANK
  eigener Container, eigenes Volume. Steht schon in Abschnitt 1 und 3
  und ist damit keine offene Frage, sondern eine gesetzte.
A7 GEHEIMNISSE
  der Agent erzeugt das Kennwort, legt es nach 9.7 ab und nennt es
  niemandem. Ableitbar, keine Entscheidung.
A9 DEMO-FIXTUR
  nein. Keine Fixtur. Nichtstun ist hier die ruecknehmbare Seite, und
  die erzeugten Daten sind laut Repository NON_PROOF.
A10 KENNZEICHNUNG
  keine Aenderung an der Oberflaeche, denn das waere ein Delta, das
  niemand freigegeben hat. Der Prototypenstatus steht im Bericht.
A11 BETRIEBSART
  Docker, eigenes Projekt. Ergibt sich aus Abschnitt 1. pm2 waere ein
  eigenes Feld und ist keines der Wahlmoeglichkeiten hier.
```

Damit hat dieses Feld keine offene Frage mehr, die den Anfang hindert.
Es bleibt genau ein Haltegrund ausserhalb der Reichweite des Agenten,
und der ist erfuellt: der Name loest auf.

Gesetz:

```text
EIN WEG OHNE ANTWORT
!=
EINE ANTWORT
```

Der Weg ohne Antwort ist zu berichten, nicht zu verschweigen. Wer
spaeter liest, muss sehen, welche Entscheidung nie getroffen und
welche nur hingenommen wurde.

---

## 19c. BERICHTIGUNG EINES FALSCHEN BEFUNDES

Die Fassungen f1 bis f4 dieser Datei haben behauptet, das Repository
habe keine Authentifizierung. Das ist falsch. Der Eigentuemer hat
widersprochen, die Nachpruefung hat ihm recht gegeben.

Was tatsaechlich vorliegt:

```text
POST /auth/login mit E-Mail und Kennwort, 401 bei falschem Kennwort
Kennwortpruefung mit PBKDF2-HMAC-SHA256, eigenem Zufallssalz je
  Zugangsdatum, Vergleich in gleichbleibender Zeit
Sitzungsmerkmal aus 256 Bit Zufall, in der Datenbank nur als Streuwert
Sitzungsmerkmal im Browser als HttpOnly-Cookie, fuer Seitenskripte
  unlesbar, SameSite Lax
kein offener Weg, sich selbst ein Konto anzulegen
```

Woher der Fehler kam:

```text
GAP-14-001 ist offen und heisst "kein Produktionsanbieter fuer
Identitaet", also kein OIDC. Daraus habe ich "keine Authentifizierung"
gemacht. Das eine ist die Herkunft der Identitaet, das andere ist
ihre Pruefung. Nur das Erste fehlt.
Dazu kam, dass im Repository ein MockProviderAdapter liegt. Der
gehoert zum KI-Zugang, nicht zur Anmeldung. Ich habe zwei Adapter
zusammengezogen, die nichts miteinander zu tun haben.
```

Gesetz:

```text
EIN OFFENER GAP
!=
EIN FEHLENDES VERFAHREN
```

Die Folge fuer das Feld: A5 braucht keinen zusaetzlichen Schutz. Der
Prototyp stand nie offen, ich hatte ihn offen gelesen. Geblieben ist
aus dem Befund genau eine Zeile, und die ist echt:
`NQUIRY_COOKIE_SECURE=1`, ohne die die Anmeldung hinter HTTPS nicht
funktioniert.

Dieser Abschnitt bleibt stehen. Ein berichtigter Befund, der
verschwindet, ist ein Befund, der wiederkommt.

---

## 19a. BEFUND AUS A3, AUFGELOEST DURCH 19b

Dieser Abschnitt gilt nicht mehr. Er bleibt stehen, weil er zeigt,
warum die Subdomain gewaehlt wurde. Er betraf die zuerst gewuenschte
Ausbringung unter einem Pfad.

### Bruch 1: die Proxy-Zusage

Die Wahl `https://condyn.eu/nquiry` ist kein zusaetzlicher Eintrag
neben den bestehenden. Sie ist ein Eingriff in den bestehenden Eintrag
von condyn.eu und sie verlangt Aenderungen am Repository. Beides steht
dieser Felddefinition ausdruecklich entgegen.

### Bruch 1: die Proxy-Zusage

```text
BISHER ZUGESAGT:
der Reverse-Proxy-Eintrag von condyn.eu bleibt byteweise unveraendert
WAS A3 VERLANGT:
ein neuer Location-Block innerhalb genau dieses Eintrags
```

Das ist kein Grund, A3 abzulehnen. Es ist ein Grund, die Zusage neu zu
fassen, damit sie stimmt. Neue Fassung, sofern A12 den Pfad bestaetigt:

```text
der bestehende Serverblock von condyn.eu wird um genau einen
  Location-Block fuer /nquiry erweitert
jede andere Zeile dieser Datei bleibt byteweise gleich
die Datei wird vor der Aenderung nach _baseline kopiert
der Proxy wird neu geladen, nicht neu gestartet
condyn.eu wird unmittelbar vor und nach dem Reload abgerufen
schlaegt der Abruf fehl, wird die Kopie sofort zurueckgespielt
```

### Bruch 2: die Scope-Zusage

```text
BISHER ZUGESAGT:
jede Aenderung am Quellcode des Repositories ist nicht im Scope
```

Vier Stellen des Repositories sind auf die lokale Entwicklung
festgeschrieben. Ohne Aenderung ist `condyn.eu/nquiry` nicht
erreichbar. Alle vier sind belegt, nicht vermutet:

```text
apps/web/next.config.ts
  kein basePath gesetzt. Unter einem Pfad fordert Next seine eigenen
  Dateien unter /_next an und bekommt sie nicht.
apps/web/lib/api/client.ts
  DEFAULT_API_BASE_URL ist auf http://localhost:8000 festgeschrieben.
  Der Browser des Besuchers wuerde seinen eigenen Rechner anfragen.
  Ob eine Umgebungsvariable das ueberschreiben kann, ist in der
  Rekonstruktion zu pruefen.
apps/api/src/nquiry_api/main.py
  CORS allow_origins ist auf http://localhost:3000 festgeschrieben.
apps/api/src/nquiry_api/http/auth.py
  das Sitzungscookie wird mit path="/" gesetzt.
```

### Der schaerfste Punkt: das Cookie

```text
NQUIRY setzt nquiry_session mit path="/" auf der Domain condyn.eu.
Damit sendet der Browser dieses Cookie bei jedem Aufruf von ConDyn mit.
```

Gesetz:

```text
EIGENES FIELD
!=
EIGENE DOMAIN
```

Zwei Anwendungen auf einer Domain teilen sich den Cookie-Raum. Das ist
eine Relation zwischen NQUIRY und ConDyn, die es vorher nicht gab. Sie
ist mit `path="/nquiry"` sauber zu schliessen, aber das ist wieder eine
Aenderung am Repository.

### Was der Pfad im Gegenzug loest

```text
Web und API liegen unter derselben Herkunft. Damit entfaellt CORS
zwischen beiden vollstaendig, statt es fuer eine fremde Herkunft
oeffnen zu muessen. Das ist der Vorteil dieser Wahl.
```

### Was fuer jede Ausbringung ohnehin zu aendern ist

Unabhaengig von Pfad oder Subdomain, sobald das Web ausgebracht wird:

```text
die API-Basis im Frontend
die CORS-Herkunft, sofern nicht dieselbe Herkunft
```

Diese beiden haengen nicht an A3. Sie haengen daran, dass der Browser
des Besuchers nicht localhost ist.

Gesetz:

```text
NEUE ANFORDERUNG
!=
ERWEITERTER AUFTRAG
```

Der Agent erweitert seinen Reparatursatz nicht selbst. Die Entscheidung
liegt bei der Authority. Siehe A12.

---

## 20. ABLAUF

```text
1. Rekonstruktionsauftrag vollstaendig ausfuehren
2. Baseline Evidence ablegen
3. Antworten auf A1 bis A10 gegen die Rekonstruktion pruefen
4. Ports, Projektname und Proxy-Muster ableiten und festhalten
5. /opt/nquiry anlegen, Repository klonen, Commit festhalten
6. .env erzeugen, Geheimnisse setzen, Rechte auf 600
7. Bilder bauen, ausschliesslich mit -p nquiry
8. postgres starten, Gesundheit abwarten
9. Migrationen ausfuehren, mit verify_migrations.py pruefen
10. api starten, /healthz nachweisen
11. web starten, Startseite nachweisen
12. Erreichbarkeit nach A2 bis A5 herstellen und nachweisen
13. Preservation Proof fuehren, siehe 21
14. Abschlussbericht schreiben, siehe 23
```

## 21. PROOF

```text
LOCAL PROOF:
/healthz antwortet, Startseite wird ausgeliefert, Datenbank ist gesund
INTEGRATION PROOF:
Web erreicht API, API erreicht Datenbank, Migrationsstand stimmt
PRESERVATION PROOF:
condyn.eu wird vor, waehrend und nach dem Lauf abgerufen und antwortet
  jedes Mal mit demselben Statuscode
docker ps -a vor und nach dem Lauf werden verglichen, jede fremde
  Anwendung antwortet wie zuvor, die Portbelegung ist bis auf die
  zugewiesenen Ports identisch, die Proxy-Konfiguration ist bis auf
  den einen neuen Eintrag byteweise gleich
```

Die Abrufprobe von condyn.eu laeuft waehrend des gesamten Vorgangs
mit, nicht nur davor und danach. Ein Ausfall, der nur zwischen zwei
Messpunkten liegt, bleibt sonst unbemerkt.

Gesetz:

```text
NEUE ANWENDUNG LÄUFT
!=
SERVER UNVERÄNDERT
```

Beides ist zu zeigen. Der zweite Nachweis ist der wichtigere.

## 22. STOPPBEDINGUNGEN

```text
eine Autoritaetsfrage ist offen und hat unter 19d keinen Weg ohne
  Antwort
ein Port, den der Agent belegen will, ist belegt und es gibt keinen
  freien im vorgesehenen Bereich
der Reverse Proxy ist nicht eindeutig bestimmbar
der Docker-Daemon laeuft nicht oder der Benutzer darf ihn nicht bedienen
eine Migration schlaegt fehl
nquiry.condyn.eu loest vom Server aus nicht auf, oder auf eine andere
  Adresse als die oeffentliche Adresse des Zielservers
die oeffentliche Adresse des Zielservers ist nicht 49.13.3.21
condyn.eu antwortet nicht mehr oder anders als vor dem Lauf
eine andere fremde Anwendung antwortet waehrend des Laufs nicht mehr
der Plattenplatz faellt unter die festgelegte Grenze
das Repository muesste an einer anderen Datei geaendert werden als der
  einen unter A8 freigegebenen
```

Bei jeder dieser Bedingungen gilt:

```text
STOP
→ ZUSTAND SICHERN
→ BEFUND BERICHTEN
→ AUTHORITY
```

Eine Bedingung haelt genau den Schritt an, an dem sie greift, nicht
rueckwirkend das schon Erreichte. Ein Name, der nicht aufloest, haelt
die Zertifikatsausstellung und den Proxy-Eintrag an. Er haelt nicht den
Klon, den Bau, die Migration und den lokalen Anlauf an. Der Agent
bringt die Anwendung dann bis zur lokalen Lauffaehigkeit, weist sie
ueber SSH-Tunnel nach und berichtet den einen offenen Punkt. Dasselbe
gilt fuer jede andere Bedingung: angehalten wird der Schritt, nicht
der Lauf, und zurueckgebaut wird nur, was ohne den angehaltenen
Schritt nicht bestehen kann.

Gesetz:

```text
EIN HALTEGRUND
!=
EIN RUECKBAU
```

Gesetz:

```text
FEHLENDE ANTWORT
!=
ERLAUBNIS
```

## 23. REKONSTRUKTION UND ABSCHLUSS

Der Abschlussbericht enthaelt:

```text
den ausgebrachten Commit
Projektname, Verzeichnis, Ports, Volumes, Netzwerk
den Proxy-Eintrag im Wortlaut
den Migrationsstand
alle drei Proofs mit ihrer Ausgabe
den Vergleich der Baseline vor und nach dem Lauf
den Rueckweg in einem Satz, ausfuehrbar
die verbleibenden offenen Punkte aus A1 bis A10
```

Abschlusszustand:

```text
READY_FOR_REVIEW
```

Nicht "fertig", nicht "laeuft", nicht "sauber".

---

## 24. LEITSATZ FÜR DIESES FELD

> Auf einem Server, der schon trägt, ist die erste Pflicht nicht, dass
> das Neue läuft, sondern dass das Alte weiterläuft.
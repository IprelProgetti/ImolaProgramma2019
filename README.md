# ImolaProgramma2019

Codice e presentazione del talk sui chatbots svolto ad Imola Programma 2019.

## Setup

### Step 1
+ [Installare **Python3** e **virtualenv**.](https://packaging.python.org/guides/installing-using-pip-and-virtualenv/)
+ Creare un ambiente virtuale (chiamandolo a piacere) seguendo la guida soprastante.
	+ Supponiamo di chiamarlo `imolaprogramma`
+ Attivare l'ambiente virtuale

### Step 2
+ Clonare il presente Repository  
```
    git clone https://github.com/IprelProgetti/ImolaProgramma2019.git
```
+ Entrare nella directory che verrà generata  
```
    cd ImolaProgramma2019/
```
+ Installare i requisiti Python (le librerie da cui il codice dipende)
```
    pip install -r requirements.txt
```

## Contenuto

La directory principale contiene già il `Jupyter Notebook` visto durante il talk, contentente il codice e la descrizione della versione base del chatbot. E' possibile:

+ visualizzarlo online
	+ dalla pagina GitHub, cliccare su `Imola Programma 2019.ipynb`
+ eseguirlo
	+ per eseguirlo:
		+ assicurarsi di essere nella cartella `ImolaProgramma2019/`
		+ digitare da terminale il comando `jupyter notebook`
		+ selezionare il notebook `Imola Programma 2019.ipynb` dall'editor che si aprirà nel browser


Nella cartella `/Presentazione` sono disponibili le slide del talk, in formato `.pdf` e `.pptx`.

Nella cartella `/Codice` è presente il file `code.py`, con alcune funzionalità chatbot più "avanzate" quali:

+ utilizzo di una rete neurale per prevedere il numero successivo ad uno fornito dall'utente
+ lettura dell'agenda di Imola Programma 2018, direttamente dal relativo sito web

## Avviare i chatbot

### Per il chatbot base

Eseguire tutte le celle di `Imola Programma 2019.ipynb` seguendo le indicazioni soprastanti

### Per il chatbot avanzato

Da terminale, dalla cartella `ImolaProgramma2019/`, digitare:

```
    cd Codice
    python code.py
```

## Usare i chatbot

Aprire l'applicazione [**Telegram**](https://telegram.org/) (disponibile via app smartphone, web browser o app desktop).

Dalla lente di ingrandimento, cercare:

+ *IprelAtImolaProgramma2019* (bot base) --> [**LINK DIRETTO**](https://t.me/IprelAtImolaProgramma2019_bot)
+ *adv_imolaprogramma2019* (bot avanzato) --> [**LINK DIRETTO**](https://t.me/adv_imolaprogramma2019_bot) 


## Nota finale

Il token presente online verrà aggiornato dopo il talk, in questo modo **non** sarà possibile per gli utilizzatori esterni ad IPREL Progetti S.r.l. modificare direttamente il chatbot presentato durante Imola Programma 2019.  
Sarà però possibile utilizzare le stesse funzionalità (totalmente o parzialmente), o una loro versione modificata, collegandole ad un nuovo chatbot (creabile tramite [**@BotFather**](https://t.me/botfather)).

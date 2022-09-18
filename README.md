# SmartHealth - SmartPregnancy IoT System
"Programming for IoT Applications" project, A.Y. 2021-2022

### Our Team
- Aime Elisa (s289512);
- Codagnone Giulia (s292257);
- Cubeddu Laura (s284277);
- De Luca Antonio (s282133).

### What does the system do?
We designed an IoT microservices-based system that helps pregnant patients and their doctors during pregnancy. 
The doctor can interact with the system via a dedicated telegram bot, which allows to:
- Register themselves;
- Register new patients;
- View plots of sampled measures, for each patient, on NodeRed;
- Increase the sampling rate of sensors for a more punctual monitoring of patients at risk.

The patient can interact with the system via another dedicated telegram bot. It allows to:
- Submit her weight;
- Reply to a survey on *Google Forms*, related to her health status.

Sensed data is matched against thresholds that are dynamic and change across the weeks of pregnancy.
Statistics about each patient are computed weekly, in order to provide the doctor with a global view of the health status of the patient.
The current version of the system is made up of multiple microservices, listed below.

### What microservices are there, currently?
1) Device Connector;
2) Data Analysis;
3) ThingSpeak Adaptor;
4) Weekly Statistics;
5) Patient Bot;
6) Telegram Bot;
7) Nodered Adaptor;
8) Google Form Adaptor;
9) FrontEnd.

![Proposal](/materiale_readme/proposal.jpg)

### How do I deploy the system?
The steps for deploying the system are easy, you just need to:
1) Import this repo;
2) Install Python and Python3 interpreters;
3) Install Docker (latest version, if possible);
4) Be sure that the Docker Daemon is started;
5) Reach the directory where you imported the repo, locally;
6) In the Catalog folder, open file 'ServicesAndResourcesCatalogue.json', scroll to ' "service_name": "TelegramDoctor" ' and change "host" entry, setting it to your localhost IP address;
7) Issue the bash command ``docker-compose up --build`` \*.

### Useful Links and Material
- Link to the promotional video of the system: https://www.youtube.com/watch?v=tDhO8cAT1S8 ;
- Link to the demo video of the system: https://www.youtube.com/watch?v=urVWMBEqnns ;
- Presentation Material: you can find the PDF in readme_material folder.

### Known Issues
Most of our problems during the development of this project were due to Docker. Sometimes the engine stops without any particular reason, or it fails due to a timeout. A workaround consists in just running the system multiple times. 

### Credits
Special thanks go to Gianfranco Giorgianni ("Gianni") for lending his voice to the promo video of the project.

#### Release Version
1.0, 18/09/2022.

\* The provided catalogue starts with patients 1 and 2. This is a choice of ours due to the fact that NodeRed, an external service that is very little dynamic, takes into account data of at least two patients. The reset function for the catalogue doesn't empty it up because it would delete them, but on the other hand the user can feel free to customize the starting catalogue as they wish, even leaving it empty for a fresh start.
In the latter case, the only needed action is just go to the Catalog/ServicesAndResourcesCatalogue.json and set the list called "Resources = []" (row 374).
Also, whenever you read "deviceID", regarding an unique ID for the raspberry device, you can put whichever string or integer, no checks are performed on it.

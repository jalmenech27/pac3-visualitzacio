# Visualització Interactiva: Cancel·lacions hoteleres (PAC3)

Aquest projecte presenta una narrativa visual interactiva basada en l'anàlisi de cancel·lacions hoteleres a partir del dataset `hotel_bookings.csv`.

## 📌 Objectiu

Analitzar els patrons de cancel·lació en hotels urbans i resorts, identificant factors com el lead time, el canal de reserva i el tipus de client per proposar accions que minimitzin les pèrdues.

## 👤 Públic objectiu

Responsables de revenue management i gestors hotelers que busquen optimitzar polítiques de reserva.

## 🚀 Com executar l'app localment

1. Clona aquest repositori:

`git clone https://github.com/jalmenech27/pac3-visualitzacio.git`

`cd pac3-visualitzacio`


2. Crea un entorn virtual (opcional però recomanat):

`python -m venv venv`

3. Instal·la les dependències:

`pip install -r requirements.txt`

4. Executa l’aplicació Shiny:

`shiny run --reload app.py`


## 🌍 Publicació a shinyapps.io

L’aplicació ha estat publicada a:
➡️ [https://jalmenech27.shinyapps.io/pac3-visualitzacio](https://jalmenech27.shinyapps.io/pac3-visualitzacio)

## 📁 Estructura del projecte

- `app.py`: codi principal de l’app amb pestanyes temàtiques.
- `hotel_bookings.csv`: dataset d’entrada.
- `recursos/`: storyboard, guió del vídeo i materials visuals.
- `output/`: fitxers finals i enllaç públic.

## 📦 Llibreries usades

- `pandas`
- `plotly`
- `shiny`
- `rsconnect-python`

## ✍️ Autoria

Creat per @jalmenech27 en el marc de la PAC3 Visualització de Dades – UOC.


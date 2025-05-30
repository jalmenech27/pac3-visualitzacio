# Visualització Interactiva: Cancel·lacions hoteleres (PAC3)

Aquest projecte presenta una narrativa visual interactiva basada en l'anàlisi de cancel·lacions hoteleres a partir del dataset `hotel_bookings.csv`. Actualment està implementat amb **Streamlit**, amb una versió alternativa en **Dash** dins de la carpeta `dash/`.

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

4. Executa l’aplicació Streamlit:

`streamlit run app.py`

## 🚀 Versió Dash

La versió Dash es troba a la carpeta dash/. El branch específic de Dash està tancat i el codi es manté dins d’aquella carpeta per a qualsevol referència.

## 📁 Estructura del projecte

├── app_tabs.py          # Codi principal de l’app Streamlit versió pestanyes
├── app_pages.py         # Codi principal de l’app Streamlit versió pàgina sencera
├── hotel_bookings.csv   # Dataset original
├── requirements.txt     # Llibreries per a Streamlit
├── dash/                # Versió alternativa en Dash
│   ├── app_pages.py     # Dash layout amb pages
│   ├── app_tabs.py      # Dash layout amb tabs
│   └── requirements.txt # Llibreries per a Dash
└── README.md



## 🌍 Publicació a [streamlit.app](https://www.streamlit.app)

L’aplicació ha estat publicada a:
- Versió "pestanyes (tabs)":
➡️ [https://jalmenech27.shinyapps.io/pac3-visualitzacio](https://pac3-visualitzacio-tabs.streamlit.app)
- Versió "pàgina sencera (pages)":
https://pac3-visualitzacio-pages.streamlit.app


## 📦 Llibreries usades ([requirements.txt](https://github.com/jalmenech27/pac3-visualitzacio/blob/main/requirements.txt))

- `pandas`
- `numpy`
- `plotly`
- `streamlit`
- `dash`

## ✍️ Autoria

Creat per [@jalmenech27](https://github.com/jalmenech27/) en el marc de la PAC3 Visualització de Dades – UOC.


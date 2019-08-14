import wget
import zipfile
import os
import shutil
import pandas as pd
from datetime import datetime
from datetime import timedelta
from geopy.geocoders import Nominatim

import pandas as pd
from datetime import datetime
from datetime import timedelta

#input
ort = 'Nürnberg'
flug1 = '20190101'
flug2 = '20190806'
name ='FC Köln'

#ort -> geocoords
geolocator = Nominatim(user_agent="GGS")
location = geolocator.geocode(ort)
# print((location.latitude, location.longitude))

#next station to geocoords

col_widths = [[0,5],[6,14],[15,23],[35,39],[43,51],[53,60],[61,101],[102,201]]
col_names = ['Stations_id','von_datum','bis_datum','Stationshoehe','geoBreite','geoLaenge','Stationsname','Bundesland']

df = pd.read_fwf('/c/code/klima/KL_Tageswerte_Beschreibung_Stationen.txt', colspecs=col_widths, names=col_names)
df = df.drop([0,1])
df = df[['Stations_id','geoBreite','geoLaenge','Stationsname']]
df['Stations_id'] = df['Stations_id'].astype('str')
df['Stationsname'] = df['Stationsname'].astype('str')
df['geoBreite'] = df['geoBreite'].astype('float')
df['geoLaenge'] = df['geoLaenge'].astype('float')
#print(df.head())

#print(df.head())
#print(df.info())

geolocator = Nominatim(user_agent="GGS")
location = geolocator.geocode(ort)
lat = location.latitude
lon = location.longitude

# print(lat, lon)

df = df.iloc[(df['geoBreite']-lat).abs().argsort()[:10]]
df = df.iloc[(df['geoLaenge']-lon).abs().argsort()[:10]]
#print(df) 
#print(station)

#ftp download klimadaten
for index, row in df.iterrows():
    try:
        station = (row['Stations_id'])
        url = 'https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/daily/kl/recent/tageswerte_KL_'+station+'_akt.zip'
        filename = wget.download(url)
        old = 'tageswerte_KL_'+station+'_akt.zip' 
        if os.path.isfile(old) == True:
            break
            print("file success")
    except:
        print("file not found")
new = 'klima.zip'
os.rename(old, new)
with zipfile.ZipFile('klima.zip', 'r') as zip_ref:
    zip_ref.extractall('data')
os.remove('klima.zip')
localpath = "./data"
for file in os.listdir(localpath):
    if file.startswith('produkt'):
        if file.endswith('.txt'):
            old = os.path.join(localpath, file)
            new = os.path.join(localpath, 'klima.txt')
            os.rename(old, new)

klima = pd.read_csv(new, sep=';')
shutil.rmtree(localpath)
#überschriften
klima.columns = ['Station', 'Datum', 'Qualität', 'Wind_max', 'Windgeschwindigkeit', 'Qualität2', 'Niederschlag', 'Niederschlagsform', 'Sonnenscheindauer', 'Schnehöhe', 'Bedeckungsgrad', 'Dampfdruck', 'Luftdruck', 'Temperatur', 'Relative Feuchte', 'Temperatur_max', 'Temperatur_min', 'Erdtemperatur_min', 'Ende']

#datum formatieren
klima['Datum'] = pd.to_datetime(klima['Datum'], format='%Y%m%d')
flug1 = datetime.strptime(flug1, '%Y%m%d')
flug2 = datetime.strptime(flug2, '%Y%m%d')
start = flug1 - timedelta(days=14)
ende  = flug2 + timedelta(days=14)

#subset klima
klima = klima[['Datum', 'Niederschlag', 'Temperatur']]
mask  = (klima['Datum'] >= start) & (klima['Datum'] <= ende)
klima = klima.loc[mask]

# print(klima.head())

from flask import Flask, render_template, request
import plotly
import plotly.graph_objs as go
import json

app = Flask(__name__)

@app.route('/')
def index():
    feature = 'Niederschlag'
    bar = create_plot(feature)
    return render_template('index.html', plot=bar)

def create_plot(feature):
    data = [
        go.Scatter(
            x=klima['Datum'],
            y=klima["Temperatur"],
            name='Temperatur',
            mode="lines",
            line=go.scatter.Line(color="red")
        ),
        go.Bar(
            x=klima['Datum'], # assign x as the dataframe column 'x'
            y=klima['Niederschlag'],
            name='Niederschlag',
            yaxis="y2",
            marker_color="blue"
        )
    ]

    layout = dict(title="Klimadiagramm "+ort, xaxis = dict(tickformat='%d.%m.'), yaxis=dict(title="Temperatur in °C",range=[-10,30]), yaxis2=dict(title="Niederschlag in mm",range=[-20,60],overlaying="y",side="right"))
    fig = dict(data=data, layout=layout)
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

@app.route('/bar', methods=['GET', 'POST'])
def change_features():

    feature = request.args['selected']
    graphJSON= create_plot(feature)

    return graphJSON

if __name__ == '__main__':
    app.run()
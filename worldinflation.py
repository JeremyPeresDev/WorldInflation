#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 13 11:39:01 2022

@author: Jérémy Peres
"""
import pandas as pd
import folium
import geopandas
import branca
from asyncio import gather
from folium.features import GeoJson, GeoJsonTooltip, GeoJsonPopup

def main():
    #data info
    dataCsv = pd.read_csv('worldinflation.csv')
    #world graphical data
    world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))
    #fixing broken iso_a3 codes
    world.loc[world['name'] == 'France', 'iso_a3'] = 'FRA'
    world.loc[world['name'] == 'Norway', 'iso_a3'] = 'NOR'
    world.loc[world['name'] == 'N. Cyprus', 'iso_a3'] = 'CYP'
    world.loc[world['name'] == 'Somaliland', 'iso_a3'] = 'SOM'
    world.loc[world['name'] == 'Kosovo', 'iso_a3'] = 'RKS'
    world.loc[world['name'] == 'Congo', 'iso_a3'] = 'COD'
    
    # Merge csv and world data
    table = world.merge(dataCsv, how="left", left_on=['iso_a3'], right_on=['iso_a3'])
    
    map = folium.Map([45, 13],zoom_start=3, maxZoom=6,minZoom=1.8)
    
    # Create a white image of 4 pixels, and embed it in a url.
    white_tile = branca.utilities.image_to_url([[1, 1], [1, 1]])

    m = folium.Map(zoom_control=True,
                   scrollWheelZoom=True,maxBounds=[[40, 68],[6, 97]],tiles=white_tile,attr='white tile',
                   dragging=True).add_to(map)
    #Add layers for Popup and Tooltips
    popup = GeoJsonPopup(
        fields=['name', 'Date', 'Last', 'Previous', 'Evolution'],
        aliases=["Pays","Mise à jour", "Inflation actuelle %", "Inflation précédente %", "Evolution en pt de %"], 
        localize=True,
        labels=True,
        style="background-color: white;",
    )

    #added threshold_scale for readability
    choropleth = folium.Choropleth(
        geo_data=table,
        name='choropleth',
        data=table,
        columns=['name', 'Last'],
        threshold_scale = (table['Last'].quantile((0, 0.025, 0.05, 0.075, 0.1, 0.2, 0.3, 0.5, 0.75, 1))).tolist(),
        key_on='feature.properties.name',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Inflation en %'
    ).add_to(map)


    for key in choropleth._children:
        if key.startswith('color_map'):
            del(choropleth._children[key])

    folium.GeoJson(
        table,
        style_function=lambda feature: {
            'fillColor': '#ffffff',
            'color': 'black',
            'weight': 0.2,
            'dashArray': '5, 5'
        },
        popup=popup
        ).add_to(choropleth)

    map.save('map.html')

if __name__ == "__main__":
    main()
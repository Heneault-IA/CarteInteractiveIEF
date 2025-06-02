import streamlit as st
import folium
import geopandas as gpd
from streamlit_folium import st_folium
from folium.features import GeoJsonTooltip

# Chargement du fichier fusionné avec géométrie
@st.cache_data
def load_data():
    return gpd.read_file("DataAcadémies.geojson")

gdf = load_data()

# Interface utilisateur
st.title("Carte interactive IEF par académie années 2023-2024")

motif_options = {
    "Total des motifs": "Total",
    "Motif 1 – Situation propre à l’enfant": "Motif 1",
    "Motif 2 – Projet éducatif": "Motif 2",
    "Motif 3 – Situation de handicap": "Motif 3",
    "Motif 4 – Autre situation particulière": "Motif 4",
    "Plein Droit" : "Plein Droit"
}

# Sélecteur : on affiche les clés, on récupère la valeur
motif_label = st.selectbox("Choisissez un motif :", list(motif_options.keys()))
motif = motif_options[motif_label]

variable = st.radio("Donnée à afficher :", ["Demandes", "Autorisations", "Refus"])

# Préparation des colonnes
col = f"{motif} : {variable}"
popup_fields = [
    "Académies",
    f"{motif} : {variable}"
]

# Créer la carte
m = folium.Map(location=[46.6, 2.5], zoom_start=6, tiles="CartoDB positron")

# Définir les couleurs dynamiquement (plus la valeur est élevée, plus c'est rouge)
def get_color(value, variable, vmax):
    if value is None:
        return "#cccccc"
    
    # Couleurs différentes selon la variable
    if variable == "Demandes":
        base_color = (0, 0, 255)  # Bleu
    elif variable == "Autorisations":
        base_color = (0, 180, 0)  # Vert
    else:  # Refus
        base_color = (255, 0, 0)  # Rouge

    # Intensité en fonction de la valeur
    intensity = min(value / vmax, 1)
    r = int(base_color[0] * intensity)
    g = int(base_color[1] * intensity)
    b = int(base_color[2] * intensity)

    return f'#{r:02x}{g:02x}{b:02x}'

# Trouver la valeur max pour échelle
vmax = gdf[col].max()

# Ajout des polygones
folium.GeoJson(
    gdf,
    style_function=lambda feature: {
        "fillColor": get_color(feature["properties"].get(col), variable, vmax),
        "color": "black",
        "weight": 1,
        "fillOpacity": 0.7,
    },
    tooltip=GeoJsonTooltip(
        fields=popup_fields,
        aliases=["Académies", variable],
        localize=True
    )
).add_to(m)

# Affichage dans Streamlit
st_data = st_folium(m, width=900, height=600)
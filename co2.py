import streamlit as st
# To make things easier later, we're also importing numpy and pandas for
# working with sample data.
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
st.set_option('deprecation.showPyplotGlobalUse', False) 
import plotly.express as px
# pour retirer les warning du plot
from matplotlib.ticker import MaxNLocator


st.title('GLOBAL CO2 EMISSION ANALYSIS')
st.write('This little dashboard is intended to present some statistic of CO2 emission for the all World and since 17th century')
st.write('Dataset is available on kaggle : https://www.kaggle.com/yoannboyere/co2-ghg-emissionsdata/notebooks ')

# LOAD DATA 
@st.cache
def load_data_co2():
    return  pd.read_csv('co2_emission.csv')
    
df = load_data_co2()

@st.cache
def load_data_pib():
    return pd.read_csv('final_pib.csv')

pib_data = load_data_pib()

@st.cache
def load_data_demographie():
    return pd.read_csv('final_demographie.csv')

demo_data = load_data_demographie()



# SELECT RELEVANT COUNTRY
st.header("In order to have more precise and more suitable data you can delete some countries to improve visualization")

delete = st.multiselect(
    "Choose countries", list(df.Entity.unique()), ['Americas (other)','World','Asia and Pacific (other)','Antarctic Fisheries','British Virgin Islands', 'Bonaire Sint Eustatius and Saba','Christmas Island','EU-28','Europe (other)','International transport', 'Statistical differences']
)

def select_data(delete):
    global df
    global pib_data
    global demo_data
    for i in delete:
        df = df[df['Entity'] != i]
        pib_data = pib_data[pib_data['Country'] != i]
        demo_data = demo_data[demo_data['Country'] != i]
     
select_data(delete)


st.write("We choose to remove entity as World, Christmas Islands ... because we don't want to see them while processing data. You can select other entity if you feel that they are not relevant")




# On choisi les differents pays a representer dans le graphe
st.header("First let's play whith curves to compare some countries and see there evolution trought time")
countries = st.multiselect(
    "Choose countries", list(df.Entity.unique()), ["France", "Germany"]
)

# Boucle qui parcours le tableau de pays pour créer les courbes
for pays in countries:
    mask = df['Entity'] == pays
    data = df[mask]
    year = pd.unique(data['Year'])
    plt.plot(year, data['Annual CO₂ emissions (tonnes )'], label = pays)

# Setup du plot
plt.xlabel('Year')
plt.ylabel('CO2 emissions (tones)')
plt.title('Evolution of CO2 emissions')
plt.legend()   
plt.show()

#  Plot le graphe final sur streamlit
st.pyplot()
st.write("For most countries we can observe an increase of co2 emission in the early 20's and a second spike in post-war period. This increase is very variable according to countries but we can see a global schema in most of the cases ")
st.write("In a second part we will try to see correlation between CO2 emission and demography/PIB in order to explain better this evolution")


# PIEPLOT 
st.header("Let's see countries wich pollute the most in a specific timerange  ")
year_value = st.slider("Select a year to study", 1750, 2017,(1960,2000))
top_value = st.selectbox('Select how many contry do you want ?', [3,5,8,10])

# manipulate data
@st.cache
def range_data():
    data_map = df[(df['Year'] >= year_value[0]) & (df['Year'] <= year_value[1]) ]
    sizes = data_map.groupby('Entity').agg({'Annual CO₂ emissions (tonnes )':'sum'})
    sizes = sizes.sort_values(by = 'Annual CO₂ emissions (tonnes )', ascending = False)
    return sizes.iloc[:top_value]

top = range_data()
labels = top.index

# plot code
plot = top.plot.pie(y='Annual CO₂ emissions (tonnes )' ,figsize=(16, 10))
plt.title('TOP '+str(top_value)+' POLLUTER IN '+str(year_value[0])+'-'+str(year_value[1]))
st.pyplot()



#  WORLD MAP
st.header("Now let's see the world map to understand more evolution of CO2 emission")
Timeline = st.slider("Year", 1750, 2017, 1960, 1)

data_map = df[df['Year'] == Timeline]
data_map = data_map.dropna()

fig = px.choropleth(data_map, locations="Code",
                    color="Annual CO₂ emissions (tonnes )",
                    hover_name="Code",
                    color_continuous_scale=px.colors.sequential.Plasma)
#dealing with the size of the plot 
fig.update_layout(
    autosize=False,
    width=1000,
    height=500,
    )
fig



"""
# Multivariable comparison: CO2 emission VS PIB VS Demography
## First let's compare evolution of data for those variable
"""
countries_comparaison = st.multiselect(
    "Choose countries", list(df.Entity.unique()), ["France", "Italy"]
)

ax = plt.figure(figsize=(19,6)).gca()
 
for pays in countries_comparaison:
    dataa = pib_data[pib_data['Country'] == pays]
    dataa['PIB'] = pd.to_numeric(dataa['PIB'])
    plt.subplot(1,3,1,title = 'PIB') 
    plt.plot(pd.unique(dataa['Year']), dataa['PIB'], label = pays)

# Setup du plot
ax.xaxis.set_major_locator(MaxNLocator(integer=True))
plt.xlabel('Year')
plt.ylabel('PIB')
plt.title('PIB EVOLUTION BY STATES')
plt.legend()
 


# Boucle qui parcours le tableau de pays pour créer les courbes
for pays in countries_comparaison:
    mask = df['Entity'] == pays
    data = df[mask]
    year = pd.unique(data['Year'])
    plt.subplot(1,3,2,title = 'CO2')
    plt.plot(year, data['Annual CO₂ emissions (tonnes )'], label = pays)

# Setup du plot
ax.xaxis.set_major_locator(MaxNLocator(integer=True))
plt.xlabel('Year')
plt.ylabel('CO2 emissions (tones)')
plt.title('Evolution of CO2 emissions')
plt.legend()   



# Boucle qui parcours le tableau de pays pour créer les courbes
for pays in countries_comparaison:
    dataa = demo_data[demo_data['Country'] == pays]
    dataa['Nombre habitants (en milliers)'] = pd.to_numeric(dataa['Nombre habitants (en milliers)'])
    dataa = dataa[dataa['Nombre habitants (en milliers)'] > 10000]
    plt.subplot(1,3,3,title = 'Demographie')
    plt.plot(pd.unique(dataa['Year']), dataa['Nombre habitants (en milliers)'], label = pays)

# Setup du plot
ax.xaxis.set_major_locator(MaxNLocator(integer=True))
plt.xlabel('Year')
plt.ylabel('Nombre habitants (en milliers)')
plt.title('DEMOGRAPHY EVOLUTION BY STATES')
plt.legend()   
  
plt.show()

#  Plot le graphe final sur streamlit
st.pyplot()

"""
## Now let's compare those data in maps
"""

Timeline_comparaison = st.slider("Year", 1820, 2008, 1950, 1)

data_map_pib = pib_data[pib_data['Year'] == Timeline_comparaison]
data_map_pib = data_map_pib.dropna()
data_map_pib['PIB'] = pd.to_numeric(data_map_pib['PIB'])

fig = px.choropleth(data_map_pib, locations="Code",
                    color="PIB",
                    hover_name="Code",
                    color_continuous_scale=px.colors.sequential.Plasma,
                    title = "PIB world distribition")

fig.update_layout(
    autosize=False,
    width=1000,
    height=450,
    )
fig



data_map_demo = demo_data[demo_data['Year'] == Timeline_comparaison]
data_map_demo = data_map_demo.dropna()
data_map_demo['Nombre habitants (en milliers)'] = pd.to_numeric(data_map_demo['Nombre habitants (en milliers)'])


fig = px.choropleth(data_map_demo, locations="Code",
                    color="Nombre habitants (en milliers)",
                    hover_name="Code",
                    color_continuous_scale=px.colors.sequential.Plasma, 
                    title = "Demography in the world")

fig.update_layout(
    autosize=False,
    width=1000,
    height=450,
    )
fig

data_map = df[df['Year'] == Timeline_comparaison]
data_map = data_map.dropna()

fig = px.choropleth(data_map, locations="Code",
                    color="Annual CO₂ emissions (tonnes )",
                    hover_name="Code",
                    color_continuous_scale=px.colors.sequential.Plasma,
                    title = "CO2 emission in the world")
#dealing with the size of the plot 
fig.update_layout(
    autosize=False,
    width=1000,
    height=450,
    )
fig

import streamlit as st
import streamlit.components.v1 as components
from textblob import TextBlob
from PIL import Image
import text2emotion as te
import plotly.graph_objects as go
import requests
import json
import modals
import pandas as pd

baseURL = 'https://imdb-api.com/en/API'
apiKey = 'k_9usdv193'
# apiKey = 'k_ua20om6k'

getEmoji = {
    "happy": "😊",
    "neutral": "😐",
    "sad": "😔",
    "disgust": "🤢",
    "surprise": "😲",
    "fear": "😨",
    "angry": "😡",
    "positive": "🙂",
    "neutral": "😐",
    "negative": "☹️",
}


def plotPie(labels, values):
    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=[value * 100 for value in values],
            hoverinfo="label+percent",
            textinfo="value"
        ))
    st.plotly_chart(fig, use_container_width=True)


lastSearched = ""
cacheData = {}


def getHotels(hotelName):
    response = pd.read_csv("Hotel.csv")
    response = response[response["Hotel_Name"] == hotelName]
    Hotels = [{"Hotel_Name": row['Hotel_Name'], "Hotel_Address": row['Hotel_Address']} for index, row in
              response.iterrows()]

    return Hotels

def getFirst700Words(string):
    if len(string) > 1000:
        return string[:1000]
    return string


def getReviews(name):
    items = pd.read_csv("Hotel.csv")
    reviews = list(getFirst700Words(items[items["Hotel_Name"] == name]["review"]))
    return reviews


def getData(HotelName):
    print("Sending request to get Hotels!!!!!!")
    Hotels = getHotels(HotelName)
    # reviews = getReviews(HotelName)
    # print('reviews')
    # print(reviews)
    data = []
    for Hotel in Hotels:
        reviews = getReviews(HotelName)
        data.append({"Hotel_Name": Hotel['Hotel_Name'], "Hotel_Address": Hotel['Hotel_Address'], "reviews": reviews})
        break
    return json.dumps({"userSearch": HotelName, "result": data})


def displayHotelContent(hotel):
    col1, col2 = st.columns([2, 3])
    with col2:
        st.components.v1.html("""
                                <h3 style="color: #1e293b; font-family: Source Sans Pro, sans-serif; font-size: 20px; margin-bottom: 10px; margin-top: 60px;">{}</h3>
                                <p style="color: #64748b; font-family: Source Sans Pro, sans-serif; font-size: 14px;">{}</p>
                                """.format(hotel["Hotel_Name"], hotel["Hotel_Address"]), height=150)


def getEmojiString(head):
    emojiHead = ""
    emotions = head.split("-")
    for emotion in emotions:
        emo = emotion.strip()
        emojiHead += getEmoji[emo.lower()]
    return head + " " + emojiHead


def process(HotelName, packageName):
    global lastSearched, cacheData
    if (lastSearched != HotelName):
        data = getData(HotelName)
        # print(data)
        lastSearched = HotelName
        cacheData = data

    else:
        data = cacheData
        # print(data)
    if len(data) > 0:
        st.text("")
        st.components.v1.html("""
                                <h3 style="color: #ef4444; font-family: Source Sans Pro, sans-serif; font-size: 22px; margin-bottom: 0px; margin-top: 40px;">API Response</h3>
                                <p style="color: #57534e; font-family: Source Sans Pro, sans-serif; font-size: 14px;">Expand below to see the API response received for the search</p>
                                """, height=100)
        with st.expander("See JSON Response"):
            with st.container():
                st.json(data)

        # Showcasing result
        st.components.v1.html("""
                                <h3 style="color: #0ea5e9; font-family: Source Sans Pro, sans-serif; font-size: 26px; margin-bottom: 10px; margin-top: 60px;">Result</h3>
                                <p style="color: #57534e; font-family: Source Sans Pro, sans-serif; font-size: 16px;">Below are the movies we received related to your search. We have analyzed each and every one for you. Enjoy!</p>
                                """, height=150)

        for hotel in list(json.loads(data)["result"]):

            with st.expander(hotel["Hotel_Name"]):
                with st.container():
                    result = applyModal(hotel, packageName)
                    #print(result)
                    keys = list(result.keys())
                    values = list(result.values())
                    st.write("")
                    st.write("")
                    displayHotelContent(hotel)
                    for i in range(0, len(keys), 4):
                        if ((i + 3) < len(keys)):

                            cols = st.columns(4)
                            cols[0].metric(getEmojiString(keys[i]), round(values[i], 2), None)
                            cols[1].metric(getEmojiString(keys[i + 1]), round(values[i + 1], 2), None)
                            cols[2].metric(getEmojiString(keys[i + 2]), round(values[i + 2], 2), None)
                            cols[3].metric(getEmojiString(keys[i + 3]), round(values[i + 3], 2), None)
                        else:
                            cols = st.columns(4)
                            for j in range(len(keys) - i):
                                #print("Range Values : ", j, len(keys))
                                cols[j].metric(getEmojiString(keys[i + j]), round(values[i + j], 2), None)

                    col1, col2 = st.columns([3, 1])
                    st.write("")
                    st.write("")
                    with col1:
                        st.subheader("Visual Representation")
                        plotPie(list(result.keys()), [value / len(hotel["reviews"]) for value in list(result.values())])


def applyModal(hotel, packageName):
    if (packageName == "Flair"):
        #print(hotel)
        predictionList = [modals.flair(review) for review in hotel["reviews"]]
        #print(predictionList)
        valueCounts = dict(pd.Series(predictionList).value_counts())
        #print(valueCounts)
        # print(valueCounts)
        return valueCounts
    elif (packageName == "TextBlob"):
        predictionList = [modals.textBlob(review) for review in hotel["reviews"]]
        valueCounts = dict(pd.Series(predictionList).value_counts())
        #print(valueCounts)
        return valueCounts
    elif (packageName == "Vader"):
        predictionList = [modals.vader(review) for review in hotel["reviews"]]
        valueCounts = dict(pd.Series(predictionList).value_counts())
        #print(valueCounts)
        return valueCounts
    elif (packageName == "Text2emotion"):
        predictionList = [modals.text2emotion(review) for review in hotel["reviews"]]
        valueCounts = dict(pd.Series(predictionList).value_counts())
        #print(valueCounts)
        return valueCounts
    else:
        return ""


def renderPage():
    st.title("Sentiment Analysis 😊😐😕😡")
    components.html("""<hr style="height:3px;border:none;color:#333;background-color:#333; margin-bottom: 10px" /> """)
    # st.markdown("### User Input Text Analysis")
    st.subheader("Hotel review analysis")
    st.text("Analyze Hotel reviews.")
    st.text("")
    lst=('11 Cadogan Gardens', '1K Hotel', '25hours Hotel beim MuseumsQuartier', '41', '45 Park Lane Dorchester Collection',
     '88 Studios', '9Hotel Republique', 'A La Villa Madame', 'ABaC Restaurant Hotel Barcelona GL Monumento',
     'AC Hotel Barcelona Forum a Marriott Lifestyle Hotel', 'AC Hotel Diagonal L Illa a Marriott Lifestyle Hotel',
     'AC Hotel Irla a Marriott Lifestyle Hotel', 'AC Hotel Milano a Marriott Lifestyle Hotel',
     'AC Hotel Paris Porte Maillot by Marriott', 'AC Hotel Sants a Marriott Lifestyle Hotel',
     'AC Hotel Victoria Suites a Marriott Lifestyle Hotel', 'ADI Doria Grand Hotel', 'ADI Hotel Poliziano Fiera',
     'ARCOTEL Kaiserwasser Superior', 'ARCOTEL Wimberger', 'AZIMUT Hotel Vienna', 'Abba Garden', 'Abba Sants',
     'Acad mie H tel Saint Germain', 'Acca Palace', 'Ace Hotel London Shoreditch', 'Acevi Villarroel',
     'Acta Atrium Palace', 'Acta CITY47', 'Admiral Hotel', 'Adria Boutique Hotel', 'Ako Suites Hotel',
     'Albus Hotel Amsterdam City Centre', 'Alexandra Barcelona A DoubleTree by Hilton', 'Alma Barcelona GL',
     'Alma Boutique Hotel', 'Aloft London Excel', 'Am Spiegeln', 'Amadi Panorama Hotel', 'Amadi Park Hotel',
     'Amarante Beau Manoir', 'Amarante Champs Elys es', 'Amba Hotel Charing Cross', 'Amba Hotel Marble Arch',
     'Ambassade Hotel', 'Ambassadors Bloomsbury', 'Amp re', 'Amsterdam Canal Residence', 'Amsterdam Marriott Hotel',
     'Andaz Amsterdam Prinsengracht A Hyatt Hotel', 'Andaz London Liverpool Street', 'Andreola Central Hotel',
     'Antares Hotel Accademia', 'Antares Hotel Rubens', 'Antica Locanda Dei Mercanti', 'Aparthotel Adagio Vienna City',
     'Aparthotel Arai 4 Superior', 'Aparthotel Atenea Barcelona', 'Aparthotel Mariano Cubi Barcelona',
     'Apex City Of London Hotel', 'Apex London Wall Hotel', 'Apex Temple Court Hotel', 'Apollo Hotel Amsterdam',
     'Apollofirst Boutique Hotel', 'Appartement Hotel an der Riemergasse', 'Arbor City', 'Arbor Hyde Park',
     'Arenas Atiram Hotels', 'Arion Cityhotel Vienna und Appartements', 'Arioso', 'Armani Hotel Milano',
     'Art Hotel Navigli', 'Arthotel ANA Boutique Six', 'Arthotel ANA Prime', 'Arthotel ANA Westbahn',
     'Artus Hotel by MH', 'Ashburn Hotel', 'Atahotel Contessa Jolanda', 'Atahotel Linea Uno', 'Atala Champs Elys es',
     'Atlantis Hotel Vienna', 'Attica 21 Barcelona Mar', 'Au Manoir Saint Germain', 'Austria Trend Hotel Ananas Wien',
     'Austria Trend Hotel Anatol Wien', 'Austria Trend Hotel Astoria Wien', 'Austria Trend Hotel Bosei Wien',
     'Austria Trend Hotel Doppio Wien', 'Austria Trend Hotel Europa Wien', 'Austria Trend Hotel Lassalle Wien',
     'Austria Trend Hotel Park Royal Palace Vienna', 'Austria Trend Hotel Rathauspark Wien',
     'Austria Trend Hotel Savoyen Vienna', 'Austria Trend Hotel Schloss Wilhelminenberg Wien',
     'Austria Trend Parkhotel Sch nbrunn Wien', 'Auteuil Tour Eiffel', 'Avenida Palace', 'Avo Hotel',
     'Axel Hotel Barcelona Urban Spa Adults Only', 'Ayre Hotel Caspe', 'Ayre Hotel Gran V a', 'Ayre Hotel Rosell n',
     'B Montmartre', 'BEST WESTERN Maitrise Hotel Maida Vale', 'BEST WESTERN PLUS Amedia Wien',
     'Baglioni Hotel Carlton The Leading Hotels of the World', 'Baglioni Hotel London The Leading Hotels of the World',
     'Balmoral Champs Elys es', 'Banke H tel', 'Banks Mansion All Inclusive Hotel', 'Barcel Milan', 'Barcel Raval',
     'Barcel Sants', 'Barcelona Hotel Colonial', 'Barcelona Princess', 'Bassano', 'Batty Langley s',
     'Bcn Urban Hotels Gran Rosellon', 'Belfast', 'Bentley London', 'Bermondsey Square Hotel A Bespoke Hotel',
     'Best Western Allegro Nation', 'Best Western Amiral Hotel', 'Best Western Antares Hotel Concorde',
     'Best Western Atlantic Hotel', 'Best Western Aulivia Op ra', 'Best Western Blue Tower Hotel',
     'Best Western Bretagne Montparnasse', 'Best Western Delphi Hotel', 'Best Western Ducs de Bourgogne',
     'Best Western Hotel Ascot', 'Best Western Hotel Astoria', 'Best Western Hotel City', 'Best Western Hotel Major',
     'Best Western Hotel Mirage', 'Best Western Hotel Montmartre Sacr Coeur',
     'Best Western Hotel Pension Arenberg Wien Zentrum', 'Best Western Hotel St George', 'Best Western Le 18 Paris',
     'Best Western Le Jardin de Cluny', 'Best Western Madison Hotel', 'Best Western Maitrise Hotel Edgware Road',
     'Best Western Mercedes Arc de Triomphe', 'Best Western Mornington Hotel Hyde Park',
     'Best Western Nouvel Orl ans Montparnasse', 'Best Western Op ra Batignolles', 'Best Western PLUS Epping Forest',
     'Best Western Palm Hotel', 'Best Western Paris Gare Saint Lazare', 'Best Western Plus 61 Paris Nation Hotel',
     'Best Western Plus Elys e Secret', 'Best Western Plus Hotel Blue Square', 'Best Western Plus Hotel Felice Casati',
     'Best Western Plus Hotel Galles', 'Best Western Plus Seraphine Hammersmith Hotel',
     'Best Western Plus de Neuville Arc de Triomphe', 'Best Western Premier Faubourg 88',
     'Best Western Premier Hotel Couture', 'Best Western Premier Hotel Dante', 'Best Western Premier Kaiserhof Wien',
     'Best Western Premier Kapital Op ra', 'Best Western Premier Le Swann', 'Best Western Premier Louvre Saint Honor ',
     'Best Western Premier Marais Grands Boulevards', 'Best Western Premier Op ra Faubourg Ex Hotel Jules ',
     'Best Western Premier Op ra Li ge', 'Best Western Premier Op ra Opal', 'Best Western Premier Trocadero La Tour',
     'Best Western S vres Montparnasse', 'Best Western Seraphine Kensington Olympia',
     'Best Western The Boltons Hotel London Kensington', 'Best Western Tour Eiffel Invalides',
     'Bianca Maria Palace Hotel', 'Bilderberg Garden Hotel', 'Bilderberg Hotel Jan Luyken', 'Blakemore Hyde Park',
     'Blakes Hotel', 'Bloomsbury Palace Hotel', 'BoB Hotel by Elegancia', 'Boscolo Milano Autograph Collection',
     'Boundary Rooms Suites', 'Boutique H tel Konfidentiel', 'Boutique Hotel Notting Hill', 'Boutiquehotel Das Tyrol',
     'Bradford Elys es Astotel', 'Britannia International Hotel Canary Wharf', 'Brunelleschi Hotel',
     'Buddha Bar Hotel Paris', 'Bulgari Hotel London', 'Bulgari Hotel Milano', 'COMO Metropolitan London',
     'COMO The Halkin', 'COQ Hotel Paris', 'Ca Bianca Hotel Corte Del Naviglio', 'Caesar Hotel',
     'Camperio House Suites Apartments', 'Canal House', 'Canary Riverside Plaza Hotel', 'Capri by Fraser Barcelona',
     'Carlyle Brera Hotel', 'Castille Paris Starhotels Collezione', 'Catalonia Atenas', 'Catalonia Barcelona 505',
     'Catalonia Barcelona Plaza', 'Catalonia Born', 'Catalonia Catedral', 'Catalonia Diagonal Centro',
     'Catalonia Eixample 1864', 'Catalonia La Pedrera', 'Catalonia Magdalenes', 'Catalonia Park Putxet',
     'Catalonia Passeig de Gr cia 4 Sup', 'Catalonia Plaza Catalunya', 'Catalonia Port', 'Catalonia Ramblas 4 Sup',
     'Catalonia Rigoletto', 'Catalonia Square 4 Sup', 'Ch teau Monfort Relais Ch teaux', 'Chambiges Elys es',
     'Charlotte Street Hotel', 'Chasse Hotel', 'Chateau Frontenac', 'Chiswick Rooms', 'City Hotel Deutschmeister',
     'City Rooms', 'Claridge s', 'Claris Hotel Spa GL', 'Clayton Crown Hotel London', 'Clayton Hotel Chiswick',
     'Club Hotel Cortina', 'Club Quarters Hotel Gracechurch', 'Club Quarters Hotel Lincoln s Inn Fields',
     'Club Quarters Hotel St Paul s', 'Club Quarters Hotel Trafalgar Square', 'Col n Hotel Barcelona', 'Colombia',
     'Comfort Inn Suites Kings Cross St Pancras', 'Commodore Hotel', 'Condes de Barcelona', 'Conrad London St James',
     'Conservatorium Hotel', 'Copthorne Tara Hotel London Kensington', 'Cordial Theaterhotel Wien',
     'Corendon Vitality Hotel Amsterdam', 'Corinthia Hotel London', 'Corus Hotel Hyde Park',
     'Cotton House Hotel Autograph Collection', 'Courthouse Hotel London', 'Courthouse Hotel Shoreditch',
     'Courtyard by Marriott Amsterdam Arena Atlas', 'Courtyard by Marriott Vienna Prater Messe',
     'Courtyard by Marriott Vienna Schoenbrunn', 'Covent Garden Hotel', 'Cram', 'Crowne Plaza Amsterdam South',
     'Crowne Plaza Barcelona Fira Center', 'Crowne Plaza London Battersea', 'Crowne Plaza London Docklands',
     'Crowne Plaza London Ealing', 'Crowne Plaza London Kensington', 'Crowne Plaza London Kings Cross',
     'Crowne Plaza London The City', 'Crowne Plaza Milan City', 'Crowne Plaza Paris R publique', 'D clic Hotel',
     'DO CO Hotel Vienna', 'Danubius Hotel Regents Park', 'Das Opernring Hotel', 'Das Triest Hotel',
     'De L Europe Amsterdam', 'De Vere Devonport House', 'Der Wilhelmshof',
     'Derag Livinghotel Kaiser Franz Joseph Vienna', 'Derby Alma', 'Dikker en Thijs Fenice Hotel',
     'Dorset Square Hotel', 'Dorsett Shepherds Bush', 'DoubleTree By Hilton London Excel', 'DoubleTree By Hilton Milan',
     'DoubleTree by Hilton Amsterdam Centraal Station', 'DoubleTree by Hilton Hotel Amsterdam NDSM Wharf',
     'DoubleTree by Hilton Hotel London Marble Arch', 'DoubleTree by Hilton Hotel London Tower of London',
     'DoubleTree by Hilton London Chelsea', 'DoubleTree by Hilton London Docklands Riverside',
     'DoubleTree by Hilton London Ealing', 'DoubleTree by Hilton London Hyde Park',
     'DoubleTree by Hilton London Islington', 'DoubleTree by Hilton London Victoria',
     'DoubleTree by Hilton London West End', 'DoubleTree by Hilton London Westminster',
     'Doubletree By Hilton London Greenwich', 'Doubletree by Hilton London Kensington', 'Drawing Hotel',
     'Draycott Hotel', 'Dukes Hotel', 'Duquesa Suites Barcelona', 'Duquesa de Cardona', 'Duret', 'Durrants Hotel',
     'Dutch Design Hotel Artemis', 'Eccleston Square Hotel', 'Edouard 7 Paris Op ra', 'Egerton House',
     'Eiffel Trocad ro', 'Element Amsterdam', 'Elys es R gencia', 'Enterprise Hotel Design Boutique',
     'Etoile Saint Ferdinand', 'Eurohotel Diagonal Port', 'Eurostars Angli', 'Eurostars Bcn Design',
     'Eurostars Cristal Palace', 'Eurostars Embassy', 'Eurostars Grand Marina Hotel GL', 'Eurostars Monumental',
     'Eurostars Ramblas', 'Evenia Rossello', 'Excelsior Hotel Gallia Luxury Collection Hotel', 'Exe Laietana Palace',
     'Exe Vienna', 'Expo Hotel Barcelona', 'Fairmont Rey Juan Carlos I', 'Falkensteiner Hotel Wien Margareten',
     'Falkensteiner Hotel Wien Zentrum Schottenfeld', 'Fielding Hotel', 'Fifty Four Boutique Hotel',
     'First Hotel Paris Tour Eiffel', 'Fleming s Conference Hotel Wien', 'Fleming s Selection Hotel Wien City',
     'Flemings Mayfair', 'Fletcher Hotel Amsterdam', 'Forest Hill Paris la Villette',
     'Four Points Sheraton Milan Center', 'Four Seasons Hotel George V Paris', 'Four Seasons Hotel London at Park Lane',
     'Four Seasons Hotel Milano', 'FourSide Hotel Suites Vienna', 'FourSide Hotel Vienna City Center', 'Francois 1er',
     'Franklin Roosevelt', 'Gainsborough Hotel', 'Gallery Hotel', 'Garden Elys e', 'Gardette Park Hotel',
     'Gartenhotel Altmannsdorf Hotel 1', 'Georgian House Hotel', 'Glam Milano', 'Golden Tulip Amsterdam Riverside',
     'Golden Tulip Amsterdam West', 'Golden Tulip Bercy Gare de Lyon 209', 'Golden Tulip Opera de Noailles',
     'Golden Tulip Washington Opera', 'Good Hotel London', 'Goodenough Club',
     'Goralska R sidences H tel Paris Bastille', 'Graben Hotel', 'Gran Hotel Barcino', 'Gran Hotel La Florida',
     'Gran Hotel Torre Catalunya', 'Grand Ferdinand Vienna Your Hotel In The City Center',
     'Grand H tel Du Palais Royal', 'Grand Hotel Amr th Amsterdam', 'Grand Hotel Central', 'Grand Hotel Downtown',
     'Grand Hotel Saint Michel', 'Grand Hotel Wien', 'Grand Hotel et de Milan', 'Grand Pigalle Hotel',
     'Grand Royale London Hyde Park', 'Grand Visconti Palace', 'Grange Beauchamp Hotel', 'Grange Blooms Hotel',
     'Grange Buckingham Hotel', 'Grange City Hotel', 'Grange Clarendon Hotel', 'Grange Fitzrovia Hotel',
     'Grange Holborn Hotel', 'Grange Langham Court Hotel', 'Grange Rochester Hotel', 'Grange St Paul s Hotel',
     'Grange Strathmore Hotel', 'Grange Tower Bridge Hotel', 'Grange Wellington Hotel', 'Grange White Hall Hotel',
     'Great Northern Hotel A Tribute Portfolio Hotel London', 'Great St Helen Hotel',
     'Grosvenor House A JW Marriott Hotel', 'Grosvenor House Suites by Jumeirah Living', 'Grupotel Gran Via 678',
     'Guitart Grand Passage', 'H tel Ad le Jules', 'H tel Aiglon Esprit de France', 'H tel Amastan Paris',
     'H tel Arvor Saint Georges', 'H tel Balzac', 'H tel Barri re Le Fouquet s', 'H tel Baume', 'H tel Beauchamps',
     'H tel Bedford', 'H tel Bel Ami', 'H tel Belloy Saint Germain By Happyculture', 'H tel Bourgogne Montana by MH',
     'H tel Brighton Esprit de France', 'H tel California Champs Elys es', 'H tel Champs lys es Plaza',
     'H tel Chaplain Paris Rive Gauche', 'H tel Concorde Montparnasse', 'H tel Crayon Rouge by Elegancia',
     'H tel Cristal Champs Elys es', 'H tel D Aubusson', 'H tel Da Vinci Spa', 'H tel De Buci by MH',
     'H tel De Castiglione', 'H tel De Sers Champs Elys es Paris', 'H tel De Vend me', 'H tel Diva Opera',
     'H tel Du Jeu De Paume', 'H tel Duc De St Simon', 'H tel Duo', 'H tel Elysees Mermoz',
     'H tel Etoile Saint Honor by Happyculture', 'H tel Exquis by Elegancia', 'H tel F licien by Elegancia',
     'H tel Fabric', 'H tel France d Antin Op ra', 'H tel Gustave', 'H tel Hor',
     'H tel Horset Op ra Best Western Premier Collection', 'H tel Jos phine by Happyculture', 'H tel Juliana Paris',
     'H tel Keppler', 'H tel L Echiquier Op ra Paris MGallery by Sofitel', 'H tel La Comtesse by Elegancia',
     'H tel La Parizienne by Elegancia', 'H tel Lancaster Paris Champs Elys es', 'H tel Le Bellechasse Saint Germain',
     'H tel Le M', 'H tel Le Marianne', 'H tel Le Relais Saint Germain', 'H tel Le Royal Monceau Raffles Paris',
     'H tel Le Walt', 'H tel Les Dames du Panth on', 'H tel Madison by MH', 'H tel Mansart Esprit de France',
     'H tel Mathis Elys es', 'H tel Mayfair Paris', 'H tel Moli re', 'H tel Monna Lisa Champs Elys es',
     'H tel Montmartre Mon Amour', 'H tel Original Paris', 'H tel Paris Bastille Boutet MGallery by Sofitel',
     'H tel Pont Royal', 'H tel Powers', 'H tel R de Paris Boutique Hotel', 'H tel Raphael', 'H tel Recamier',
     'H tel Regent s Garden', 'H tel Regina', 'H tel Regina Op ra Grands Boulevards', 'H tel Saint Marc',
     'H tel Saint Paul Rive Gauche', 'H tel San R gis', 'H tel Square Louvois', 'H tel Th r se', 'H tel Thoumieux',
     'H tel Vernet', 'H tel Victor Hugo Paris Kl ber', 'H tel Waldorf Trocad ro', 'H tel Westminster',
     'H tel de Banville', 'H tel de Jos phine BONAPARTE', 'H tel de La Tamise Esprit de France', 'H tel de Lille',
     'H tel de Varenne', 'H tel de la Bourdonnais', 'H tel des Academies et des Arts', 'H tel des Champs Elys es',
     'H tel des Ducs D Anjou', 'H tel du Minist re', 'H10 Art Gallery 4 Sup', 'H10 Casa Mimosa 4 Sup', 'H10 Casanova',
     'H10 Cubik 4 Sup', 'H10 Itaca', 'H10 London Waterloo', 'H10 Marina Barcelona', 'H10 Metropolitan 4 Sup',
     'H10 Port Vell 4 Sup', 'H10 Universitat', 'H10 Urquinaona Plaza', 'HCC Regente', 'HCC St Moritz',
     'Hallmark Hotel London Chigwell Prince Regent', 'Ham Yard Hotel', 'Hampshire Hotel Amsterdam American',
     'Hampshire Hotel Rembrandt Square Amsterdam', 'Hampshire Hotel The Manor Amsterdam',
     'Hampton by Hilton Amsterdam Centre East', 'Haymarket Hotel', 'Hazlitt s', 'Henley House Hotel', 'Henry VIII',
     'Hidden Hotel by Elegancia', 'Hilton Amsterdam', 'Hilton Barcelona', 'Hilton Diagonal Mar Barcelona',
     'Hilton Garden Inn Milan North', 'Hilton Garden Inn Vienna South', 'Hilton London Angel Islington',
     'Hilton London Bankside', 'Hilton London Canary Wharf', 'Hilton London Euston', 'Hilton London Green Park',
     'Hilton London Hyde Park', 'Hilton London Kensington Hotel', 'Hilton London Metropole', 'Hilton London Olympia',
     'Hilton London Paddington', 'Hilton London Tower Bridge', 'Hilton London Wembley', 'Hilton Milan',
     'Hilton Paris Opera', 'Hilton Vienna', 'Hilton Vienna Danube Waterfront', 'Hilton Vienna Plaza',
     'Holiday Inn Amsterdam', 'Holiday Inn Amsterdam Arena Towers', 'Holiday Inn London Bloomsbury',
     'Holiday Inn London Brent Cross', 'Holiday Inn London Camden Lock', 'Holiday Inn London Kensington',
     'Holiday Inn London Kensington Forum', 'Holiday Inn London Mayfair', 'Holiday Inn London Oxford Circus',
     'Holiday Inn London Regent s Park', 'Holiday Inn London Stratford City', 'Holiday Inn London Wembley',
     'Holiday Inn London West', 'Holiday Inn London Whitechapel', 'Holiday Inn Milan Garibaldi Station',
     'Holiday Inn Paris Elys es', 'Holiday Inn Paris Gare Montparnasse', 'Holiday Inn Paris Gare de Lyon Bastille',
     'Holiday Inn Paris Gare de l Est', 'Holiday Inn Paris Montmartre', 'Holiday Inn Paris Montparnasse Pasteur',
     'Holiday Inn Paris Notre Dame', 'Holiday Inn Paris Op ra Grands Boulevards',
     'Holiday Inn Paris Saint Germain des Pr s', 'Holiday Inn Vienna City', 'Hollmann Beletage Design Boutique',
     'Hotel 1898', 'Hotel 4 Barcelona', 'Hotel 55', 'Hotel 82 London', 'Hotel Abbot', 'Hotel Advance', 'Hotel Alimara',
     'Hotel Am Konzerthaus Vienna MGallery by Sofitel', 'Hotel Am Parkring', 'Hotel Am Schubertring',
     'Hotel Am Stephansplatz', 'Hotel Amadeus', 'Hotel Ambassador', 'Hotel America Barcelona',
     'Hotel Amsterdam De Roode Leeuw', 'Hotel Arena', 'Hotel Ares Eiffel', 'Hotel Arkadenhof', 'Hotel Arts Barcelona',
     'Hotel Astor Saint Honor ', 'Hotel Astra Opera Astotel', 'Hotel Atlanta', 'Hotel Atmospheres', 'Hotel Auriga',
     'Hotel Bachaumont', 'Hotel Bagu s', 'Hotel Balmes', 'Hotel Balmoral', 'Hotel Barcelona Catedral',
     'Hotel Barcelona Center', 'Hotel Barcelona Universal', 'Hotel Beethoven Wien', 'Hotel Bellevue Wien',
     'Hotel Berna', 'Hotel Best Western PLUS Alfa Aeropuerto', 'Hotel Boltzmann', 'Hotel Boutique Duomo',
     'Hotel Bristol', 'Hotel Bristol A Luxury Collection Hotel', 'Hotel Cafe Royal', 'Hotel Cambon',
     'Hotel Capitol Milano', 'Hotel Capricorno', 'Hotel Carlton s Montmartre', 'Hotel Carrobbio', 'Hotel Casa Bonay',
     'Hotel Casa Camper', 'Hotel Casa Fuster G L Monumento', 'Hotel Cavendish', 'Hotel Cavour',
     'Hotel Champs Elys es Friedland by Happyculture', 'Hotel Chavanel', 'Hotel City Central',
     'Hotel Ciutadella Barcelona', 'Hotel Claridge Paris', 'Hotel Clerici', 'Hotel Corvinus', 'Hotel Crivi s',
     'Hotel D Este', 'Hotel DO Pla a Reial G L ', 'Hotel Da Vinci', 'Hotel Daniel Paris', 'Hotel Daniel Vienna',
     'Hotel Das Tigra', 'Hotel De Hallen', 'Hotel De Vigny', 'Hotel Dei Cavalieri', 'Hotel Derby',
     'Hotel Des Saints Peres Esprit de France', 'Hotel Design Secret de Paris', 'Hotel Die Port van Cleve',
     'Hotel Dieci', 'Hotel Domizil', 'Hotel Duminy Vendome', 'Hotel Dupond Smith', 'Hotel Eden', 'Hotel Eiffel Blomet',
     'Hotel Eitlj rg', 'Hotel Elys es Bassano', 'Hotel Erzherzog Rainer', 'Hotel Espa a Ramblas', 'Hotel Esther a',
     'Hotel Eug ne en Ville', 'Hotel Front Maritim', 'Hotel G tico', 'Hotel Galileo', 'Hotel Gallitzinberg',
     'Hotel Garbi Millenni', 'Hotel Georgette', 'Hotel Gran Derby Suites', 'Hotel Granados 83', 'Hotel Grums Barcelona',
     'Hotel Imlauer Wien', 'Hotel Imperial A Luxury Collection Hotel', 'Hotel Indigo Barcelona Plaza Catalunya',
     'Hotel Indigo London Kensington', 'Hotel Indigo London Paddington', 'Hotel Indigo London Tower Hill',
     'Hotel Indigo Paris Opera', 'Hotel J ger', 'Hotel JL No76', 'Hotel Johann Strauss', 'Hotel K nig von Ungarn',
     'Hotel Kaiserin Elisabeth', 'Hotel Kavalier', 'Hotel L Antoine', 'Hotel La Lanterne', 'Hotel La Place',
     'Hotel La Spezia Gruppo MiniHotel', 'Hotel La Villa Saint Germain Des Pr s', 'Hotel Lam e',
     'Hotel Landhaus Fuhrgassl Huber', 'Hotel Le 10 BIS', 'Hotel Le Chat Noir', 'Hotel Le Mareuil', 'Hotel Le Pera',
     'Hotel Le Placide Saint Germain Des Pr s', 'Hotel Le Saint Gregoire', 'Hotel Le Sainte Beuve', 'Hotel Le Six',
     'Hotel Le Squara', 'Hotel Le petit Paris', 'Hotel Les Bains Paris', 'Hotel Les Bulles De Paris',
     'Hotel Les Rives de Notre Dame', 'Hotel Les Th tres', 'Hotel Liberty', 'Hotel Lloyd', 'Hotel Lombardia',
     'Hotel Louis 2', 'Hotel Louvre Montana', 'Hotel Lumen Paris Louvre', 'Hotel Mademoiselle',
     'Hotel Magna Pars Small Luxury Hotels of the World', 'Hotel Mailberger Hof', 'Hotel Maison Ath n e',
     'Hotel Maison FL', 'Hotel Malte Astotel', 'Hotel Manin', 'Hotel Manzoni', 'Hotel Marconi', 'Hotel Margot House',
     'Hotel Marignan Champs Elys es', 'Hotel Mediolanum', 'Hotel Mentana',
     'Hotel Mercure La Sorbonne Saint Germain des Pr s', 'Hotel Mercure Milano Centro', 'Hotel Mercure Milano Solari',
     'Hotel Mercure Wien City', 'Hotel Mercure Wien Westbahnhof', 'Hotel Michelangelo', 'Hotel Midmost',
     'Hotel Milano Scala', 'Hotel Miramar Barcelona GL', 'Hotel Monceau Wagram', 'Hotel Monge', 'Hotel Monsieur',
     'Hotel Montaigne', 'Hotel Montalembert', 'Hotel Moonlight', 'Hotel Mozart', 'Hotel Murmuri Barcelona',
     'Hotel Neri', 'Hotel Nestroy Wien', 'Hotel OFF Paris Seine', 'Hotel Odeon Saint Germain', 'Hotel Okura Amsterdam',
     'Hotel Omm', 'Hotel Op ra Richepanse', 'Hotel Opera Cadet', 'Hotel Oscar', 'Hotel Palace GL',
     'Hotel Palais Strudlhof', 'Hotel Panache', 'Hotel Parc Saint Severin Esprit de France',
     'Hotel Parco di Sch nbrunn Vienna', 'Hotel Park Lane Paris', 'Hotel Park Villa',
     'Hotel Pension Baron am Schottentor', 'Hotel Pierre Milano', 'Hotel Plaza Athenee Paris', 'Hotel Plaza Elys es',
     'Hotel Portello Gruppo Minihotel', 'Hotel Principe Di Savoia', 'Hotel Prinz Eugen', 'Hotel Pulitzer',
     'Hotel Pulitzer Paris', 'Hotel Raffaello', 'Hotel Rathaus Wein Design', 'Hotel Regina', 'Hotel Rekord',
     'Hotel Roemer Amsterdam', 'Hotel Romana Residence', 'Hotel Ronda Lesseps', 'Hotel Royal', 'Hotel Royal Elys es',
     'Hotel SB Diagonal Zero Barcelona 4 Sup', 'Hotel SB Icaria Barcelona', 'Hotel Sacher Wien',
     'Hotel Saint Dominique', 'Hotel Saint Petersbourg Opera', 'Hotel Sanpi Milano', 'Hotel Sans Souci Wien',
     'Hotel Santa Marta Suites', 'Hotel Schani Wien', 'Hotel Schild', 'Hotel Scribe Paris Opera by Sofitel',
     'Hotel Serhs Rivoli Rambla', 'Hotel Seven One Seven', 'Hotel Sezz Paris', 'Hotel Silver',
     'Hotel Spa La Belle Juliette', 'Hotel Spa Villa Olimpica Suites', 'Hotel Spadari Al Duomo', 'Hotel Square',
     'Hotel Stefanie', 'Hotel Stendhal Place Vend me Paris MGallery by Sofitel', 'Hotel Sunflower',
     'Hotel The Peninsula Paris', 'Hotel The Serras', 'Hotel Tiziano Park Vita Parcour Gruppo MiniHotels', 'Hotel Tocq',
     'Hotel Topazz', 'Hotel Tour d Auvergne Opera', 'Hotel Trianon Rive Gauche', 'Hotel V Fizeaustraat',
     'Hotel V Nesplein', 'Hotel VIU Milan', 'Hotel Verneuil Saint Germain', 'Hotel ViennArt am Museumsquartier',
     'Hotel Vienna', 'Hotel Vignon', 'Hotel Vilamar ', 'Hotel Villa Emilia', 'Hotel Villa Lafayette Paris IX',
     'Hotel Villa Saxe Eiffel', 'Hotel Vittoria', 'Hotel Vondel Amsterdam', 'Hotel Vueling Bcn by HC', 'Hotel Wagner',
     'Hotel Wandl', 'Hotel Well and Come', 'Hotel West End', 'Hotel Whistler', 'Hotel Xanadu',
     'Hotel Xenia Autograph Collection', 'Hotel Zeitgeist Vienna Hauptbahnhof', 'Hotel d Orsay Esprit de France',
     'Hotel de France Wien', 'Hotel de Nell', 'Hotel de Seze', 'Hotel degli Arcimboldi',
     'Hotel des Tuileries Relais du Silence', 'Hotel du Collectionneur Arc de Triomphe',
     'Hotel du Louvre in the Unbound Collection by Hyatt', 'Hotel du Petit Moulin',
     'Hotel du Vin Cannizaro House Wimbledon', 'Hotel le Lapin Blanc', 'Hotel mbit Barcelona',
     'Hyatt Regency Amsterdam', 'Hyatt Regency London The Churchill', 'Hyatt Regency Paris Etoile',
     'IH Hotels Milano Ambasciatori', 'IH Hotels Milano Gioia', 'IH Hotels Milano Lorenteggio',
     'IH Hotels Milano Puccini', 'IH Hotels Milano Watt 13', 'INK Hotel Amsterdam MGallery by Sofitel',
     'Ibis Styles Milano Palmanova', 'Ibis Styles Paris Gare Saint Lazare', 'Idea Hotel Milano San Siro', 'Idol Hotel',
     'Ilunion Almirante', 'Ilunion Barcelona', 'Ilunion Bel Art', 'Imperial Riding School Renaissance Vienna Hotel',
     'Innkeeper s Lodge London Greenwich', 'Inntel Hotels Amsterdam Centre', 'InterContinental Amstel Amsterdam',
     'InterContinental London Park Lane', 'InterContinental Paris Avenue Marceau', 'InterContinental Paris Le Grand',
     'InterContinental Wien', 'IntercityHotel Wien', 'Intercontinental London The O2', 'JUFA Hotel Wien',
     'Jaz Amsterdam', 'Jumeirah Carlton Tower', 'Jumeirah Lowndes Hotel', 'K K H tel Cayr Saint Germain des Pr s',
     'K K Hotel George', 'K K Hotel Maria Theresia', 'K K Hotel Picasso', 'K K Palais Hotel', 'K West Hotel Spa',
     'Karma Sanctum Soho Hotel', 'Kensington House Hotel', 'Kingsway Hall Hotel', 'Klima Hotel Milano Fiere',
     'Knightsbridge Hotel', 'Kube Hotel Ice Bar', 'L Edmond H tel', 'L Empire Paris', 'L H tel',
     'L Hotel Pergol se Paris', 'LHP Hotel Napoleon', 'La Chambre du Marais', 'La Clef Tour Eiffel',
     'La Maison Champs Elys es', 'La Maison Favart', 'La Suite West Hyde Park', 'La Tremoille Paris',
     'La Villa Haussmann', 'La Villa Maillot', 'La Villa Royale', 'La Villa des Ternes',
     'LaGare Hotel Milano Centrale MGallery by Sofitel', 'Lancaster London', 'Landmark London',
     'Lansbury Heritage Hotel', 'Le 123 Elysees Astotel', 'Le 123 S bastopol Astotel', 'Le 7 Eiffel Hotel', 'Le A',
     'Le Belmont Champs Elys es', 'Le Burgundy Paris', 'Le Cinq Codet', 'Le Dokhan s a Tribute Portfolio Hotel',
     'Le G n ral H tel', 'Le Grand H tel de Normandie', 'Le Grey Hotel', 'Le Lavoisier', 'Le Littr ',
     'Le M ridien Barcelona', 'Le M ridien Etoile', 'Le Marceau Bastille', 'Le Marcel', 'Le Marquis Eiffel',
     'Le Mathurin Hotel Spa', 'Le Meridien Piccadilly', 'Le Meridien Vienna',
     'Le Metropolitan a Tribute Portfolio Hotel', 'Le Meurice', 'Le Narcisse Blanc Spa', 'Le Parisis Paris Tour Eiffel',
     'Le Pavillon de la Reine Spa', 'Le Pavillon des Lettres', 'Le Pigalle Hotel', 'Le Pradey', 'Le Relais M dicis',
     'Le Relais Madeleine', 'Le Relais Montmartre', 'Le Roch Hotel Spa', 'Le Saint Hotel Paris', 'Le Senat',
     'Le Tourville Eiffel', 'Le Tsuba Hotel', 'Legend Saint Germain by Elegancia', 'Leonardo Hotel Milan City Center',
     'Leonardo Hotel Vienna', 'Les Jardins De La Villa Spa', 'Les Jardins Du Marais', 'Les Matins de Paris Spa',
     'Les Plumes Hotel', 'Lindner Hotel Am Belvedere', 'Little Palace Hotel', 'London Bridge Hotel',
     'London City Suites', 'London Elizabeth Hotel', 'London Hilton on Park Lane', 'London Marriott Hotel County Hall',
     'London Marriott Hotel Grosvenor Square', 'London Marriott Hotel Kensington', 'London Marriott Hotel Marble Arch',
     'London Marriott Hotel Park Lane', 'London Marriott Hotel Regents Park', 'London Marriott Hotel West India Quay',
     'London Marriott Maida Vale', 'London Suites', 'Luxury Suites Amsterdam', 'Lyric H tel Paris',
     'M by Montcalm Shoreditch London Tech City', 'M venpick Hotel Amsterdam City Centre',
     'MARQUIS Faubourg St Honor Relais Ch teaux', 'ME London by Melia', 'ME Milan Il Duca', 'Madeleine Plaza',
     'Maison Albar H tel Paris Champs Elys es ex Mac Mahon ', 'Maison Albar Hotel Paris C line',
     'Maison Albar Hotel Paris Op ra Diamond', 'Maison Borella', 'Maison Souquet', 'Majestic Hotel Spa',
     'Majestic Hotel Spa Barcelona GL', 'Malmaison London', 'Mandarin Oriental Barcelona',
     'Mandarin Oriental Hyde Park London', 'Mandarin Oriental Milan', 'Mandarin Oriental Paris', 'Marlin Waterloo',
     'Maxim Op ra', 'Mayflower Hotel Apartments', 'Medinaceli', 'Megaro Hotel', 'Meli Milano', 'Melia Barcelona Sarri ',
     'Melia Barcelona Sky 4 Sup', 'Melia Paris Champs Elys es', 'Melia Paris Notre Dame', 'Melia Paris Tour Eiffel',
     'Melia Paris Vendome', 'Melia Vienna', 'Melia White House Hotel', 'Mercer Hotel Barcelona',
     'Mercer House B ria BCN', 'Mercure Amsterdam Sloterdijk Station', 'Mercure Barcelona Condor',
     'Mercure Grand Hotel Biedermeier Wien', 'Mercure Hotel Amsterdam Centre Canal District',
     'Mercure Hotel Amsterdam City South', 'Mercure Hotel Amsterdam West', 'Mercure Hotel Raphael Wien',
     'Mercure Josefshof Wien', 'Mercure London Bloomsbury Hotel', 'Mercure London Bridge', 'Mercure London Hyde Park',
     'Mercure London Kensington Hotel', 'Mercure London Paddington Hotel', 'Mercure Milano Regency',
     'Mercure Paris 15 Porte de Versailles', 'Mercure Paris 17 me Saint Lazare Monceau',
     'Mercure Paris 19 Philharmonie La Villette', 'Mercure Paris Alesia', 'Mercure Paris Arc de Triomphe Etoile',
     'Mercure Paris Bastille Marais', 'Mercure Paris Bastille Saint Antoine', 'Mercure Paris Bercy Biblioth que',
     'Mercure Paris Centre Tour Eiffel', 'Mercure Paris Champs Elys es', 'Mercure Paris Gare De Lyon TGV',
     'Mercure Paris Gare Montparnasse', 'Mercure Paris Gobelins Place d Italie', 'Mercure Paris Montmartre Sacr Coeur',
     'Mercure Paris Montparnasse Raspail', 'Mercure Paris Notre Dame Saint Germain des Pr s',
     'Mercure Paris Op ra Faubourg Montmartre', 'Mercure Paris Opera Garnier', 'Mercure Paris Opera Grands Boulevards',
     'Mercure Paris Opera Louvre', 'Mercure Paris Pigalle Sacre Coeur', 'Mercure Paris Place d Italie',
     'Mercure Paris Porte De Versailles Expo', 'Mercure Paris Porte d Orleans', 'Mercure Paris Terminus Nord',
     'Mercure Paris Tour Eiffel Pont Mirabeau', 'Mercure Secession Wien', 'Mercure Tour Eiffel Grenelle',
     'Mercure Vaugirard Paris Porte De Versailles', 'Mercure Vienna First', 'Mercure Wien Zentrum', 'MiHotel',
     'Milan Marriott Hotel', 'Milan Suite Hotel', 'Milestone Hotel Kensington', 'Mill sime H tel',
     'Millennium Copthorne Hotels at Chelsea Football Club', 'Millennium Gloucester Hotel London',
     'Millennium Hotel London Knightsbridge', 'Millennium Hotel London Mayfair', 'Millennium Hotel Paris Opera',
     'Mimi s Hotel Soho', 'Mokinba Hotels Baviera', 'Mokinba Hotels King', 'Mokinba Hotels Montebianco',
     'Molitor Paris MGallery by Sofitel', 'Mondrian London', 'Monhotel Lounge SPA',
     'Monsieur Cadet Hotel Spa Ex Meyerhold Spa ', 'Montagu Place Hotel', 'Montcalm Royal London House City of London',
     'Montfleuri', 'Monument Hotel', 'Morgan Mees', 'My Bloomsbury', 'My Chelsea', 'My Home In Paris',
     'NH Amsterdam Caransa', 'NH Amsterdam Centre', 'NH Amsterdam Museum Quarter', 'NH Amsterdam Noord',
     'NH Amsterdam Schiller', 'NH Amsterdam Zuid', 'NH Barcelona Stadium', 'NH Carlton Amsterdam',
     'NH City Centre Amsterdam', 'NH Collection Amsterdam Barbizon Palace', 'NH Collection Amsterdam Doelen',
     'NH Collection Amsterdam Grand Hotel Krasnapolsky', 'NH Collection Barcelona Constanza',
     'NH Collection Barcelona Gran Hotel Calder n', 'NH Collection Barcelona Podium', 'NH Collection Milano President',
     'NH Collection Wien Zentrum', 'NH Danube City', 'NH Hesperia Barcelona Presidente',
     'NH Hesperia Barcelona del Mar', 'NH London Kensington', 'NH Milano Grand Hotel Verdi', 'NH Milano Machiavelli',
     'NH Milano Palazzo Moscova', 'NH Milano Touring', 'NH Sants Barcelona', 'NH Wien Belvedere', 'NH Wien City',
     'NYX Milan', 'Napoleon Paris', 'Negresco Princess 4 Sup', 'Nell Hotel Suites', 'New Linden Hotel',
     'Newhotel Roblin', 'Nhow Milan', 'Nolinski Paris', 'Norfolk Towers Paddington', 'Nottingham Place Hotel',
     'Novotel Amsterdam City', 'Novotel Barcelona City', 'Novotel London Blackfriars', 'Novotel London Canary Wharf',
     'Novotel London City South', 'Novotel London Excel', 'Novotel London Greenwich', 'Novotel London Paddington',
     'Novotel London Tower Bridge', 'Novotel London Waterloo', 'Novotel London Wembley', 'Novotel London West',
     'Novotel Milano Linate Aeroporto', 'Novotel Milano Nord Ca Granda', 'Novotel Paris 14 Porte d Orl ans',
     'Novotel Paris 17', 'Novotel Paris Centre Bercy', 'Novotel Paris Centre Gare Montparnasse',
     'Novotel Paris Centre Tour Eiffel', 'Novotel Paris Gare De Lyon', 'Novotel Paris Les Halles',
     'Novotel Paris Vaugirard Montparnasse', 'Novotel Suites Paris Expo Porte de Versailles',
     'Novotel Suites Paris Montreuil Vincennes', 'Novotel Suites Paris Nord 18 me', 'Novotel Wien City', 'Nu Hotel',
     'Number Sixteen', 'Occidental Atenea Mar Adults Only', 'Oceania Paris Porte De Versailles', 'Ofelias Hotel 4 Sup',
     'Ohla Barcelona', 'Ohla Eixample', 'Okko Hotels Paris Porte De Versailles', 'Old Ship Inn Hackney',
     'Olivia Balmes Hotel', 'Olivia Plaza Hotel', 'One Aldwych', 'Onix Liceo', 'Op ra Marigny', 'Ozo Hotel',
     'Paddington Court Executive Rooms', 'Pakat Suites Hotel', 'Palais Coburg Residenz',
     'Palais Hansen Kempinski Vienna', 'Palazzo Parigi Hotel Grand Spa Milano', 'Palazzo Segreti',
     'Paris Marriott Champs Elysees Hotel', 'Paris Marriott Opera Ambassador Hotel', 'Paris Marriott Rive Gauche Hotel',
     'Park Avenue Baker Street', 'Park Grand London Hyde Park', 'Park Grand London Kensington',
     'Park Grand London Lancaster Gate', 'Park Grand Paddington Court', 'Park Hotel', 'Park Hyatt Milano',
     'Park Hyatt Paris Vendome', 'Park Hyatt Vienna', 'Park Inn by Radisson Uno City Vienna',
     'Park International Hotel', 'Park Lane Mews Hotel', 'Park Plaza County Hall London',
     'Park Plaza London Park Royal', 'Park Plaza London Riverbank', 'Park Plaza London Waterloo',
     'Park Plaza Sherlock Holmes London', 'Park Plaza Victoria Amsterdam', 'Park Plaza Victoria London',
     'Park Plaza Vondelpark Amsterdam', 'Park Plaza Westminster Bridge London', 'Pershing Hall',
     'Pertschy Palais Hotel', 'Pestana Arena Barcelona', 'Pestana Chelsea Bridge Hotel Spa', 'Petit Palace Barcelona',
     'Petit Palace Boqueria Garden', 'Petit Palace Museum', 'Petit Palais Hotel De Charme', 'Phileas Hotel',
     'Pillows Anna van den Vondel Amsterdam', 'Platine Hotel Spa', 'Plaza Tour Eiffel', 'Pol Grace Hotel',
     'Portobello House', 'Primero Primera', 'Prince de Galles a Luxury Collection hotel Paris', 'Pulitzer Amsterdam',
     'Pullman Barcelona Skipper', 'Pullman London St Pancras', 'Pullman Paris Centre Bercy',
     'Pullman Paris Montparnasse', 'Pullman Paris Tour Eiffel', 'Qualys Hotel Nasco', 'R Kipling by Happyculture',
     'Radisson Blu Champs Elys es Paris', 'Radisson Blu Edwardian Berkshire',
     'Radisson Blu Edwardian Bloomsbury Street', 'Radisson Blu Edwardian Grafton', 'Radisson Blu Edwardian Hampshire',
     'Radisson Blu Edwardian Kenilworth', 'Radisson Blu Edwardian Mercer Street',
     'Radisson Blu Edwardian New Providence Wharf', 'Radisson Blu Edwardian Sussex',
     'Radisson Blu Edwardian Vanderbilt', 'Radisson Blu Hotel Amsterdam', 'Radisson Blu Hotel Milan',
     'Radisson Blu Portman Hotel London', 'Radisson Blu Style Hotel Vienna', 'Rafayel Hotel Spa',
     'Rainers Hotel Vienna', 'Ramada Apollo Amsterdam Centre', 'Ramada Plaza Milano', 'Rathbone', 'Relais Christine',
     'Relais Du Louvre', 'Relais H tel du Vieux Paris', 'Relais Saint Jacques', 'Renaissance Amsterdam Hotel',
     'Renaissance Barcelona Hotel', 'Renaissance Paris Arc de Triomphe Hotel',
     'Renaissance Paris Le Parc Trocadero Hotel', 'Renaissance Paris Republique Hotel Spa',
     'Renaissance Paris Vendome Hotel', 'Residence Du Roy', 'Residence Henri IV', 'Ritz Paris',
     'Rocco Forte Brown s Hotel', 'Rochester Champs Elysees', 'Roger de Ll ria', 'Room Mate Aitana', 'Room Mate Anna',
     'Room Mate Carla', 'Room Mate Gerard', 'Room Mate Giulia', 'Roomz Vienna',
     'Rosa Grand Milano Starhotels Collezione', 'Rosewood London', 'Royal Amsterdam Hotel',
     'Royal Garden Champs Elysees', 'Royal Garden Hotel', 'Royal Hotel Champs Elys es', 'Royal Passeig de Gracia',
     'Royal Ramblas', 'Royal Saint Honore', 'Royal Saint Michel', 'Rubens At The Palace', 'Rydges Kensington Hotel',
     'STRAF a Member of Design Hotels ', 'Saint Georges Hotel', 'Saint James Albany Paris Hotel Spa',
     'Saint SHERMIN bed breakfast champagne', 'Sall s Hotel Pere IV', 'San Domenico House', 'Sanderson A Morgans Hotel',
     'Sansi Diputacio', 'Sansi Pedralbes', 'Savoy Hotel Amsterdam', 'Schlosshotel R mischer Kaiser', 'Select Hotel',
     'Senato Hotel Milano', 'Senator Barcelona Spa Hotel', 'Senator Hotel Vienna', 'Seraphine Kensington Gardens Hotel',
     'Sercotel Amister Art Hotel Barcelona', 'Seven Hotel', 'Shaftesbury Hyde Park International',
     'Shaftesbury Metropolis London Hyde Park', 'Shaftesbury Premier London Paddington',
     'Shaftesbury Suites London Marble Arch', 'Shangri La Hotel Paris', 'Shangri La Hotel at The Shard London',
     'Shepherd s Bush Boutique Hotel', 'Sheraton Diana Majestic', 'Sheraton Grand London Park Lane', 'Silken Concordia',
     'Silken Gran Hotel Havana', 'Silken Ramblas', 'Simm s Hotel', 'Simply Rooms Suites', 'Sina De La Ville',
     'Sina The Gray', 'Sir Adam Hotel', 'Sir Albert Hotel', 'Sixtytwo Hotel', 'Sloane Square Hotel',
     'Small Luxury Hotel Altstadt Vienna', 'Snob Hotel by Elegancia', 'Sofitel Legend The Grand Amsterdam',
     'Sofitel London St James', 'Sofitel Paris Arc De Triomphe', 'Sofitel Paris Baltimore Tour Eiffel',
     'Sofitel Paris Le Faubourg', 'Sofitel Vienna Stephansdom', 'South Place Hotel', 'Splendid Etoile',
     'Splendide Royal Paris', 'St Ermin s Hotel Autograph Collection', 'St George Hotel', 'St George s Hotel Wembley',
     'St James Court A Taj Hotel London', 'St James Hotel Club Mayfair', 'St Martins Lane A Morgans Original',
     'St Pancras Renaissance Hotel London', 'St Paul s Hotel', 'Starhotels Anderson', 'Starhotels Business Palace',
     'Starhotels Echo', 'Starhotels Ritz', 'Starhotels Tourist', 'Staunton Hotel B B',
     'Staybridge Suites London Stratford', 'Staybridge Suites London Vauxhall', 'Steigenberger Hotel Herrenhof',
     'Strand Palace Hotel', 'Strandhotel Alte Donau', 'Style Hotel', 'Suite Hotel 900 m zur Oper',
     'Suites H tel Helzear Champs Elys es', 'Suites H tel Helzear Montparnasse', 'Sunotel Central',
     'Sunotel Club Central', 'Swiss tel Amsterdam', 'Sydney House Chelsea', 'TH Street Duomo', 'TRYP Paris Op ra',
     'TWO Hotel Barcelona by Axel 4 Sup Adults Only', 'Taj 51 Buckingham Gate Suites and Residences',
     'Ten Manchester Street Hotel', 'Terrass H tel Montmartre by MH', 'The Abbey Court Notting Hill', 'The Academy',
     'The Ampersand Hotel', 'The Arch London', 'The Athenaeum', 'The Bailey s Hotel London', 'The Beaufort',
     'The Beaumont Hotel', 'The Belgrave Hotel', 'The Berkeley', 'The Bloomsbury Hotel', 'The Bryson Hotel',
     'The Capital', 'The Cavendish London', 'The Chamberlain', 'The Chelsea Harbour Hotel', 'The Chess Hotel',
     'The Chesterfield Mayfair', 'The Cleveland', 'The College Hotel', 'The Colonnade', 'The Connaught',
     'The Corner Hotel', 'The Cranley Hotel', 'The Cumberland A Guoman Hotel', 'The Curtain',
     'The Dorchester Dorchester Collection', 'The Drayton Court Hotel', 'The Dylan Amsterdam',
     'The Exhibitionist Hotel', 'The Franklin Hotel Starhotels Collezione', 'The Gates Diagonal Barcelona',
     'The Gore Hotel Starhotels Collezione', 'The Goring', 'The Grand at Trafalgar Square', 'The Grosvenor',
     'The Guesthouse Vienna', 'The Hari London', 'The Harmonie Vienna', 'The Henrietta Hotel', 'The Hoxton Amsterdam',
     'The Hoxton Holborn', 'The Hoxton Shoreditch', 'The Hub Hotel', 'The Justin James Hotel', 'The Kensington Hotel',
     'The Kings Head Hotel', 'The LaLit London', 'The Lanesborough', 'The Langham London', 'The Laslett',
     'The Leonard Hotel', 'The Levante Parliament A Design Hotel', 'The Level at Melia Barcelona Sky',
     'The Levin Hotel', 'The Lodge Hotel Putney', 'The London EDITION', 'The Mandeville Hotel',
     'The Marble Arch London', 'The Marylebone Hotel', 'The May Fair Hotel', 'The Mirror Barcelona',
     'The Montague On The Gardens', 'The Montcalm At Brewery London City', 'The Montcalm Marble Arch',
     'The Nadler Kensington', 'The Nadler Soho', 'The Nadler Victoria', 'The Ned', 'The One Barcelona GL',
     'The Park City Grand Plaza Kensington Hotel', 'The Park Grand London Paddington',
     'The Park Tower Knightsbridge a Luxury Collection Hotel', 'The Pelham Starhotels Collezione',
     'The Piccadilly London West End', 'The Pillar Hotel', 'The Portobello Hotel', 'The Premier Notting Hill',
     'The Principal London', 'The Queens Gate Hotel', 'The RE London Shoreditch', 'The Rembrandt',
     'The Ring Vienna s Casual Luxury Hotel', 'The Ritz Carlton Vienna', 'The Ritz London', 'The Rockwell',
     'The Rookery', 'The Royal Horseguards', 'The Royal Park Hotel', 'The Savoy', 'The Soho Hotel',
     'The Square Milano Duomo', 'The Stafford London', 'The Student Hotel Amsterdam City', 'The Sumner Hotel',
     'The Tophams Hotel', 'The Toren', 'The Tower A Guoman Hotel', 'The Trafalgar Hilton', 'The Victoria',
     'The Waldorf Hilton', 'The Wellesley Knightsbridge a Luxury Collection Hotel London', 'The Westbourne Hyde Park',
     'The Westbridge Hotel', 'The Westbury A Luxury Collection Hotel Mayfair London', 'The Westin Palace',
     'The Westin Paris Vend me', 'The Whitechapel', 'The Wittmore Adults Only', 'The Yard Milano', 'The Zetter Hotel',
     'The Zetter Townhouse Clerkenwell', 'The Zetter Townhouse Marylebone', 'TheWesley', 'Thistle Euston',
     'Thistle Holborn The Kingsley', 'Thistle Hyde Park', 'Thistle Kensington Gardens',
     'Thistle Trafalgar Square The Royal Trafalgar', 'Threadneedles Autograph Collection',
     'Timhotel Op ra Blanche Fontaine', 'Timhotel Op ra Grands Magasins', 'TownHouse 12', 'TownHouse 33',
     'TownHouse Duomo', 'TownHouse Galleria', 'Trinit Haussmann', 'Tryp Barcelona Apolo Hotel',
     'Tryp Barcelona Condal Mar Hotel', 'Twenty Nevern Square Hotel', 'U232 Hotel', 'UNA Hotel Century',
     'UNA Hotel Cusani', 'UNA Hotel Mediterraneo', 'UNA Hotel Scandinavia', 'UNA Maison Milano',
     'United Lodge Hotel and Apartments', 'Upper Diagonal', 'Uptown Palace', 'Urban Lodge Hotel', 'Vice Versa',
     'Victoire Germain', 'Victoires Opera', 'Victoria Palace Hotel', 'Vienna Marriott Hotel', 'Vienna Sporthotel',
     'Vilana Hotel', 'Villa Alessandra', 'Villa Beaumarchais', 'Villa Eugenie', 'Villa Lut ce Port Royal',
     'Villa Montparnasse', 'Villa Opera Drouot', 'Villa Panth on', 'Villa d Estr es', 'Vincci Bit', 'Vincci Gala',
     'Vincci Mae', 'Vincci Maritimo', 'W Amsterdam', 'W Barcelona', 'W London Leicester Square', 'W Paris Op ra',
     'W12 Rooms', 'Waldorf Astoria Amsterdam', 'Waldorf Madeleine', 'Warwick Paris Former Warwick Champs Elysees ',
     'Washington Mayfair Hotel', 'WestCord Art Hotel Amsterdam 4 stars', 'WestCord Fashion Hotel Amsterdam',
     'Westside Arc de Triomphe Hotel', 'Wilson Boutique Hotel', 'Windermere Hotel', 'Windsor Hotel Milano',
     'Windsor Opera', 'Worldhotel Cristoforo Colombo', 'XO Hotel', 'Zenit Barcelona', 'Zenit Borrell',
     'art otel Amsterdam', 'citizenM Amsterdam', 'citizenM London Bankside', 'citizenM London Shoreditch',
     'citizenM Tower of London', 'every hotel Piccadilly', 'pentahotel Vienna')
    options = list(range(len(lst)))

    HotelName= st.selectbox(
    'Select Hotel Name', lst)

    packageName = st.selectbox(
        'Select Package',
        ('Flair', 'Vader', 'TextBlob', 'Text2emotion'))
    if st.button('Search'):
        if HotelName:
            process(HotelName, packageName)
        else:
            st.warning("Please enter a Hotel name")

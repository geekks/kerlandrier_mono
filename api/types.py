"""
This module defines the data types used in the OpenAgenda system for representing locations and events.

Classes:
    Timing: Represents the timing information for an event.
    MultilingualEntry: A dictionary type for storing multilingual text entries.
    Location: Represents a location in the OpenAgenda system.
    OpenAgendaEvent: Represents an event in the OpenAgenda system.
    OpenAgendaEventsResponse: Represents a response containing a list of events and the total count.
"""

from typing import List, Dict, Optional, TypedDict, Any

class Timing:
    begin: str
    end: str

class MultilingualEntry(TypedDict, total=False):
    fr: str
    en: Optional[str]

class Location:
    """
    Represents a location in the OpenAgenda system.

    Attributes:
        uid (str): 	Identifiant unique OpenAgenda du lieu. Non éditable
        name (str): Nom du lieu. Max 100 caractères.
        address (str): Adresse. max 255 caractères.
        access (MultilingualEntry): Instructions d'accès en plusieurs langues.
        description (MultilingualEntry): Texte multilingue, 5000 caractères maximum. Présentation du lieu. 
        image (dict): Illustration du lieu
        imageCredits (str): Crédits liées à l'illustration du lieu
        slug (str): Identifiant textuel.Champ non éditable
        setUid (str): Identifiant du jeu de lieu associé.Champ non éditable
        city (str): Ville / Commune
        department (str): Département (pour les lieux en France)
        region (str): Région (pour les lieux en France)
        postalCode (str): Code postal.
        insee (str): Code INSEE
        countryCode (str): Code pays ISO 3166-1 Alpha 2. Exemple: CH
        district (str): Quartier.
        latitude (float): Coordonnée géographique décimale du lieu. Exemple: 48.4102778
        longitude (float): Coordonnée géographique décimale du lieu. Exemple: 7.4511111
        updatedAt (str): Date de dernière mise à jour. Champ non éditable
        createdAt (str): Date de création. Champ non éditable
        website (str): Lien vers le site internet principal du lieu.
        email (str): 	Adresse email de contact principale du lieu
        phone (str): Numéro de téléphone de contact principal du lieu
        links (List[str]): Liste de liens hypertextes. Exemple: ['https://www.louvre.fr', 'https://www.facebook.com/museedulouvre']
        timezone (str): Fuseau horaire du lieu. Exemple: Europe/Paris.
        extId (str): Référence sur un jeu de données externe à OpenAgenda
        state (int): Statut du lieu. 0 - le lieu est à vérifier / 1 - le lieu est vérifié
    """
    def __init__(self, uid: str, name: str, address: str, access: MultilingualEntry, description: MultilingualEntry,
                image: dict, imageCredits: str, slug: str, city: str, department: str, region: str,
                postalCode: str, insee: str, countryCode: str, district: str, latitude: float, longitude: float,
                updatedAt: str, createdAt: str, website: str, email: str, phone: str, links: List[str],
                timezone: str, extId: str, state: int):
        self.uid = uid
        self.name = name
        self.address = address
        self.access = access
        self.description = description
        self.image = image
        self.imageCredits = imageCredits
        self.slug = slug
        self.city = city
        self.department = department
        self.region = region
        self.postalCode = postalCode
        self.insee = insee
        self.countryCode = countryCode
        self.district = district
        self.latitude = latitude
        self.longitude = longitude
        self.updatedAt = updatedAt
        self.createdAt = createdAt
        self.website = website
        self.email = email
        self.phone = phone
        self.links = links
        self.timezone = timezone
        self.extId = extId
        self.state = state


class OpenAgendaEvent:
    """
    Represents an event in the OpenAgenda system.

    Attributes:
        uid (str): The unique identifier of the event.
        slug (str): The slug of the event.
        title (str): The title of the event.
        image (dict): Infos about the main image of the event.
        imageCredits (str): The credits for the image.
        onlineAccessLink (str): The link to access the event online (1=offline, 2=online, 3=hybrid)
        attendanceMode (int): The attendance mode of the event.
        registration (list[str]): Liste des moyens d'inscription : numéros de téléphones, email ou liens hypertextes
        accessibility (dict): Accessibility informations for each handicap.
        age (dict{min: int, max: int}): The age range of the event.
        status (int): The status of the event.  (Reporté, Annulé, Complet...)
        state (int): The state of the event on OA (Publié, Prêt à publier, À modérer, Refusé)
        location (Location): The location details of the event.
        firstTiming (Timing): The first timing of the event.
        nextTiming (Timing): The next timing of the event.
        lastTiming (Timing): The last timing of the event.
        longDescription (MultilingualEntry): The long description of the event.
        description (MultilingualEntry): The description of the event.
        keywords (List[str]): A list of keywords associated with the event.
        timings (List[Timing]): A list of timings for the event.
        locationUid (str): The unique identifier of the location.
        links (dict): A list of rich links associated with the event.
        timezone (str): The timezone of the event.
        createdAt (str): The creation date of the event.
        updatedAt (str): The last update date of the event.
    """
    def __init__(self, uid: str,
                slug: str,
                title: MultilingualEntry,
                onlineAccessLink: str,
                attendanceMode: int,
                status: int,
                keywords: List[str],
                location: Location,
                firstTiming: Timing,
                nextTiming: Timing,
                lastTiming: Timing,
                longDescription: MultilingualEntry,
                description: MultilingualEntry,
                image: str,
                imageCredits:str,
                registration: list[str],
                accessibility: dict,
                age: dict,
                locationUid: dict,
                timezone: str,
                timings: List[Timing]):
                
        self.uid = uid
        self.slug = slug
        self.title = title
        self.attendanceMode = attendanceMode
        self.onlineAccessLink = onlineAccessLink
        self.status = status
        self.keywords = keywords
        self.location = location
        self.firstTiming = firstTiming
        self.nextTiming = nextTiming
        self.lastTiming = lastTiming
        self.longDescription = longDescription
        self.description = description
        self.keywords = keywords
        self.timings = timings
        self.image = image
        self.imageCredits = imageCredits
        self.registration = registration
        self.accessibility = accessibility
        self.age = age
        self.locationUid = locationUid
        self.timezone = timezone




class OpenAgendaEventsResponse:
    def __init__(self, total: int, events: List[OpenAgendaEvent]):
        self.total = total
        self.events = events

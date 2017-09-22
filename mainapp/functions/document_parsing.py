from mainapp.models import SearchStreet, Body, Location
from django.conf import settings
import geoextract
import re


def create_geoextract_data(bodies=None):
    """
    :type bodies: list of mainapp.models.Body
    :return: list
    """

    street_names = []
    if bodies:
        streets = SearchStreet.objects.filter(bodies__in=bodies)
    else:
        streets = SearchStreet.objects.all()

    locations = []
    for street in streets:
        if street.displayed_name not in street_names:
            street_names.append(street.displayed_name)
            locations.append({
                'type': 'street',
                'name': street.displayed_name
            })

    for city in settings.GEOEXTRACT_KNOWN_CITIES:
        locations.append({
            'name': city,
            'type': 'city',
        })

    return locations


def get_geodata(location, fallback_city_name):
    search_str = ''
    if 'street' in location:
        search_str += location['street']
        if 'house_number' in location:
            search_str += ' ' + location['house_number']
        if 'postcode' in location:
            search_str += ', ' + location['postcode'] + ' ' + location['city']
        elif 'city' in location:
            search_str += ', ' + location['city']
        else:
            search_str += ', ' + fallback_city_name
    elif 'name' in location:
        search_str += location['name'] + ', ' + fallback_city_name

    search_str += ', ' + settings.GEO_SEARCH_COUNTRY

    geolocator = settings.OPENCAGEDATA_KEY
    location = geolocator.geocode(search_str, language="de", exactly_one=False)
    if len(location) == 0:
        return None

    return {
        'lat': location[0].latitude,
        'lng': location[0].longitude,
    }


def format_location_name(location):
    """
    :param location: str
    :return: str
    """
    name = ""

    if 'street' in location:
        name = location['street']
        if 'house_number' in location:
            name += ' ' + location['house_number']
    elif 'name' in location:
        name = location['name']

    return name


def extract_found_locations(text, bodies=None):
    """
    :type text: str
    :type bodies: list of Body
    :return: list
    """
    search_for = create_geoextract_data(bodies)

    #
    # STRING NORMALIZATION
    #

    # Strings must be normalized before searching and matching them. This includes
    # technical normalization (e.g. Unicode normalization), linguistic
    # normalization (e.g. stemming) and content normalization (e.g. synonym
    # handling).

    normalizer = geoextract.BasicNormalizer(subs=[(r'str\b', 'strasse')],
                                            stem='german')

    #
    # NAMES
    #

    # Many places can be referred to using just their name, for example specific
    # buildings (e.g. the Brandenburger Tor), streets (Hauptstraße) or other
    # points of interest. These can be extracted using the ``NameExtractor``.
    #
    # Note that extractor will automatically receive the (normalized) location
    # names from the pipeline we construct later, so there's no need to explicitly
    # pass them to the constructor.

    name_extractor = geoextract.NameExtractor()

    #
    # PATTERNS
    #

    # For locations that are notated using a semi-structured format (addresses)
    # the ``PatternExtractor`` is a good choice. It looks for matches of regular
    # expressions.
    #
    # The patterns should have named groups, their sub-matches will be
    # returned in the extracted locations.

    address_pattern = re.compile(r'''
        (?P<street>[^\W\d_](?:[^\W\d_]|\s)*[^\W\d_])
        \s+
        (?P<house_number>([1-9]\d*)[\w-]*)
        (
            \s+
            (
                (?P<postcode>\d{5})
                \s+
            )?
            (?P<city>([^\W\d_]|-)+)
        )?
    ''', flags=re.UNICODE | re.VERBOSE)

    pattern_extractor = geoextract.PatternExtractor([address_pattern])

    #
    # POSTPROCESSING
    #

    # Once locations are extracted you might want to postprocess them, for example
    # to remove certain attributes that are useful for validation but are not
    # intended for publication. Or you may want to remove a certain address that's
    # printed in the footer of all the documents you're processing.
    #
    # GeoExtract allows you to do this by using one or more postprocessors. In this
    # example we will remove all but a few keys from our location dicts.

    keys_to_keep = ['name', 'street', 'house_number', 'postcode', 'city']
    key_filter_postprocessor = geoextract.KeyFilterPostprocessor(keys_to_keep)

    #
    # PIPELINE CONSTRUCTION
    #

    # A pipeline connects all the different components.
    #
    # Here we're using custom extractors and a custom normalizer. We could also
    # provide our own code for splitting a document into chunks and for validation,
    # but for simplicity we'll use the default implementations in these cases.

    pipeline = geoextract.Pipeline(
        search_for,
        extractors=[pattern_extractor, name_extractor],
        normalizer=normalizer,
        postprocessors=[key_filter_postprocessor],
    )

    return pipeline.extract(text)


def detect_relevant_bodies(location):
    """
    :param location: mainapp.models.Location
    :return: list of mainapp.models.Body
    """
    body = Body.objects.get(id=4)  # @TODO
    return [body]


def extract_locations(text, fallback_city=None):
    """
    :type text: str
    :type fallback_city: str
    :return: list of mainapp.models.Body
    """
    if not fallback_city:
        fallback_city = settings.GEOEXTRACT_DEFAULT_CITY

    found_locations = extract_found_locations(text)

    locations = []
    for found_location in found_locations:
        location_name = format_location_name(found_location)
        try:
            location = Location.objects.get(name=location_name)
            locations.append(location)
        except Location.DoesNotExist:
            geodata = get_geodata(found_location, fallback_city)

            location = Location()
            location.name = location_name
            location.short_name = location_name
            location.is_official = False
            location.osm_id = None  # @TODO
            if geodata:
                location.geometry = {
                    "type": "Point",
                    "coordinates": [geodata['lng'], geodata['lat']]
                }
            else:
                location.geometry = None
            location.save()

            bodies = detect_relevant_bodies(location)
            for body in bodies:
                location.bodies.add(body)

            locations.append(location)

    return locations

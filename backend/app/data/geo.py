"""Catálogo de país / departamento / ciudad para el selector con buscador.

Colombia está cubierta con sus 32 departamentos y sus municipios principales.
Otros países incluyen sus ciudades más pobladas: la plataforma también acepta
ciudades escritas a mano, así que la lista es una ayuda, no un límite.
"""

from __future__ import annotations

COUNTRIES: dict[str, dict[str, list[str]]] = {
    "Colombia": {
        "Amazonas": ["Leticia", "Puerto Nariño"],
        "Antioquia": [
            "Medellín", "Bello", "Itagüí", "Envigado", "Apartadó", "Turbo", "Rionegro",
            "Sabaneta", "Copacabana", "La Estrella", "Caldas", "Girardota", "Barbosa",
            "Caucasia", "Necoclí", "Chigorodó", "Carepa", "El Bagre", "Segovia", "Yarumal",
            "Santa Fe de Antioquia", "Puerto Berrío", "Marinilla", "La Ceja", "Guarne",
            "El Carmen de Viboral", "Sonsón", "Andes", "Amagá", "Jericó", "Urrao", "Ituango",
            "Remedios", "Tarazá", "San Pedro de los Milagros", "Don Matías", "Támesis",
            "Santa Rosa de Osos", "Frontino", "Dabeiba", "Puerto Triunfo", "San Carlos",
        ],
        "Arauca": ["Arauca", "Arauquita", "Saravena", "Tame", "Fortul", "Puerto Rondón", "Cravo Norte"],
        "Atlántico": [
            "Barranquilla", "Soledad", "Malambo", "Sabanalarga", "Puerto Colombia", "Galapa",
            "Baranoa", "Sabanagrande", "Santo Tomás", "Palmar de Varela", "Polonuevo", "Luruaco",
            "Repelón", "Juan de Acosta", "Tubará", "Usiacurí", "Ponedera", "Campo de la Cruz",
            "Candelaria", "Manatí", "Santa Lucía", "Suan", "Piojó",
        ],
        "Bogotá D.C.": ["Bogotá"],
        "Bolívar": [
            "Cartagena", "Magangué", "Turbaco", "Arjona", "El Carmen de Bolívar", "Mompós",
            "San Juan Nepomuceno", "Santa Rosa del Sur", "Turbaná", "Villanueva", "María la Baja",
            "San Pablo", "Simití", "Achí", "Mahates", "Clemencia", "Santa Catalina", "Calamar",
            "San Jacinto", "Córdoba", "Morales", "Arenal", "Tiquisio",
        ],
        "Boyacá": [
            "Tunja", "Duitama", "Sogamoso", "Chiquinquirá", "Paipa", "Villa de Leyva",
            "Puerto Boyacá", "Moniquirá", "Garagoa", "Nobsa", "Tibasosa", "Samacá", "Ramiriquí",
            "Soatá", "Guateque", "Tuta", "Cómbita", "Aquitania", "Muzo", "Miraflores", "Saboyá",
            "Ventaquemada", "Santa Rosa de Viterbo", "Sotaquirá", "Turmequé", "Tópaga",
        ],
        "Caldas": [
            "Manizales", "Villamaría", "Chinchiná", "La Dorada", "Riosucio", "Anserma",
            "Manzanares", "Salamina", "Aguadas", "Neira", "Palestina", "Supía", "Marmato",
            "Pácora", "Viterbo", "Belalcázar", "Filadelfia", "Marquetalia", "Pensilvania",
            "Samaná", "Risaralda", "San José", "Norcasia", "Victoria", "La Merced", "Marulanda",
        ],
        "Caquetá": [
            "Florencia", "San Vicente del Caguán", "Puerto Rico", "El Doncello", "Curillo",
            "Belén de los Andaquíes", "Cartagena del Chairá", "La Montañita", "Morelia", "Milán",
            "Solano", "Solita", "Valparaíso", "Albania", "El Paujil", "San José del Fragua",
        ],
        "Casanare": [
            "Yopal", "Aguazul", "Villanueva", "Tauramena", "Paz de Ariporo", "Monterrey", "Maní",
            "Trinidad", "Orocué", "Hato Corozal", "Pore", "Nunchía", "San Luis de Palenque",
            "Támara", "Sabanalarga", "Chámeza", "Recetor", "La Salina", "Sácama",
        ],
        "Cauca": [
            "Popayán", "Santander de Quilichao", "Puerto Tejada", "El Bordo (Patía)", "Piendamó",
            "Corinto", "Miranda", "Caloto", "Guapi", "Timbío", "Cajibío", "Silvia", "El Tambo",
            "Morales", "Bolívar", "Mercaderes", "Villa Rica", "Padilla", "Toribío", "Inzá",
            "Belalcázar (Páez)", "Totoró", "Buenos Aires", "Suárez", "Argelia", "Balboa",
            "Caldono", "Jambaló", "Puracé", "Timbiquí", "López de Micay", "Sucre", "La Vega",
        ],
        "Cesar": [
            "Valledupar", "Aguachica", "Bosconia", "Agustín Codazzi", "La Jagua de Ibirico",
            "Curumaní", "Chimichagua", "El Copey", "San Alberto", "San Diego", "Pailitas",
            "Chiriguaná", "Becerril", "La Paz", "Manaure Balcón del Cesar", "Pelaya", "González",
            "Río de Oro", "Astrea", "El Paso", "Gamarra", "La Gloria", "Pueblo Bello",
            "Tamalameque", "San Martín",
        ],
        "Chocó": [
            "Quibdó", "Istmina", "Tadó", "Riosucio", "Condoto", "Bahía Solano", "Nuquí",
            "Acandí", "Unguía", "Bojayá", "Lloró", "Cértegui", "Nóvita", "El Carmen de Atrato",
            "Juradó", "Medio Atrato", "Bagadó", "Sipí", "Carmen del Darién",
        ],
        "Córdoba": [
            "Montería", "Lorica", "Cereté", "Sahagún", "Planeta Rica", "Montelíbano", "Tierralta",
            "Ciénaga de Oro", "San Antero", "Puerto Libertador", "Chinú", "San Pelayo", "Moñitos",
            "Los Córdobas", "Valencia", "Ayapel", "Buenavista", "Canalete", "San Bernardo del Viento",
            "Purísima", "Momil", "Tuchín", "Cotorra", "San Carlos", "Pueblo Nuevo", "La Apartada",
            "San José de Uré", "Chimá", "Puerto Escondido", "San Andrés de Sotavento",
        ],
        "Cundinamarca": [
            "Soacha", "Fusagasugá", "Facatativá", "Zipaquirá", "Chía", "Girardot", "Mosquera",
            "Madrid", "Funza", "Cajicá", "Sibaté", "Tocancipá", "Ubaté", "La Calera", "Cota",
            "Tenjo", "Sopó", "Villeta", "Cáqueza", "Choachí", "Anapoima", "La Mesa", "Silvania",
            "Guaduas", "Pacho", "Gachetá", "Tabio", "Nemocón", "Sesquilé", "Suesca", "Gachancipá",
            "Bojacá", "El Rosal", "Subachoque", "Zipacón", "Tocaima", "Ricaurte", "Agua de Dios",
            "Nilo", "Arbeláez", "Granada", "San Bernardo", "Pasca", "Une", "Fómeque", "Guasca",
            "Guatavita", "Chocontá", "Villapinzón", "Simijaca", "Puerto Salgar", "Caparrapí",
            "La Palma", "Yacopí", "Sasaima", "Anolaima", "Cachipay", "Viotá", "El Colegio",
            "Tena", "San Juan de Rioseco", "Medina", "Paratebueno", "Chipaque", "Cabrera",
            "Apulo", "Nocaima", "Supatá", "San Francisco", "Albán", "Machetá", "Lenguazaque",
        ],
        "Guainía": ["Inírida", "Barrancominas"],
        "Guaviare": ["San José del Guaviare", "El Retorno", "Calamar", "Miraflores"],
        "Huila": [
            "Neiva", "Pitalito", "Garzón", "La Plata", "Campoalegre", "Palermo", "Gigante",
            "Rivera", "Aipe", "Timaná", "Isnos", "San Agustín", "Acevedo", "Algeciras", "Suaza",
            "Tello", "Yaguará", "Villavieja", "Baraya", "Hobo", "Íquira", "Nátaga", "Paicol",
            "Tesalia", "Saladoblanco", "Oporapa", "Tarqui", "Altamira", "Guadalupe", "Colombia",
        ],
        "La Guajira": [
            "Riohacha", "Maicao", "Uribia", "Manaure", "San Juan del Cesar", "Villanueva",
            "Fonseca", "Barrancas", "Albania", "Dibulla", "Hatonuevo", "Distracción", "El Molino",
            "La Jagua del Pilar", "Urumita",
        ],
        "Magdalena": [
            "Santa Marta", "Ciénaga", "Fundación", "El Banco", "Plato", "Aracataca", "Zona Bananera",
            "Pivijay", "Santa Ana", "Guamal", "Sitionuevo", "Puebloviejo", "Algarrobo", "Ariguaní",
            "Chibolo", "Concordia", "El Piñón", "Pedraza", "Remolino", "Salamina", "San Sebastián",
            "Tenerife", "Zapayán", "Nueva Granada", "San Zenón", "Pijiño del Carmen",
        ],
        "Meta": [
            "Villavicencio", "Acacías", "Granada", "Puerto López", "Puerto Gaitán", "San Martín",
            "Cumaral", "Restrepo", "Guamal", "Castilla la Nueva", "El Dorado", "Puerto Lleras",
            "Puerto Rico", "Vistahermosa", "La Macarena", "Mesetas", "Lejanías", "El Castillo",
            "Fuente de Oro", "San Juan de Arama", "Barranca de Upía", "Cabuyaro", "San Carlos de Guaroa",
        ],
        "Nariño": [
            "Pasto", "Tumaco", "Ipiales", "Túquerres", "La Unión", "Samaniego", "Barbacoas",
            "Sandoná", "Cumbal", "Buesaco", "El Charco", "La Cruz", "Ricaurte", "Guaitarilla",
            "Consacá", "Yacuanquer", "Tangua", "Chachagüí", "El Tambo", "Linares", "Ospina",
            "Pupiales", "Iles", "Aldana", "Guachucal", "Córdoba", "Potosí", "Mallama", "Policarpa",
        ],
        "Norte de Santander": [
            "Cúcuta", "Ocaña", "Villa del Rosario", "Los Patios", "Pamplona", "Tibú", "El Zulia",
            "Sardinata", "Ábrego", "Chinácota", "Puerto Santander", "San Cayetano", "El Carmen",
            "Convención", "Teorama", "Bochalema", "Villa Caro", "Salazar", "Arboledas", "Cucutilla",
            "Toledo", "Labateca", "Chitagá", "Chibitá (Cácota)", "Silos", "Chinácota",
        ],
        "Putumayo": [
            "Mocoa", "Puerto Asís", "Orito", "Valle del Guamuez (La Hormiga)", "Villagarzón",
            "Sibundoy", "San Miguel", "Puerto Caicedo", "Puerto Guzmán", "Colón", "Santiago",
            "San Francisco", "Puerto Leguízamo",
        ],
        "Quindío": [
            "Armenia", "Calarcá", "La Tebaida", "Montenegro", "Quimbaya", "Circasia", "Filandia",
            "Salento", "Córdoba", "Pijao", "Buenavista", "Génova",
        ],
        "Risaralda": [
            "Pereira", "Dosquebradas", "Santa Rosa de Cabal", "La Virginia", "Marsella",
            "Belén de Umbría", "Quinchía", "Apía", "Santuario", "Guática", "Balboa", "La Celia",
            "Mistrató", "Pueblo Rico",
        ],
        "San Andrés y Providencia": ["San Andrés", "Providencia"],
        "Santander": [
            "Bucaramanga", "Floridablanca", "Girón", "Piedecuesta", "Barrancabermeja",
            "San Gil", "Socorro", "Barbosa", "Málaga", "Vélez", "Zapatoca", "Lebrija", "Rionegro",
            "Sabana de Torres", "Puerto Wilches", "Cimitarra", "Landázuri", "Charalá", "Curití",
            "Barichara", "Villanueva", "Los Santos", "Oiba", "Suaita", "Puente Nacional",
            "San Vicente de Chucurí", "El Playón", "Matanza", "California", "Tona", "Confines",
        ],
        "Sucre": [
            "Sincelejo", "Corozal", "Sampués", "San Marcos", "Since", "Tolú", "San Onofre",
            "Coveñas", "Los Palmitos", "Ovejas", "Morroa", "Galeras", "El Roble", "Betulia",
            "Buenavista", "Caimito", "Chalán", "Colosó", "Guaranda", "La Unión", "Majagual",
            "Palmito", "San Benito Abad", "San Juan de Betulia", "San Pedro", "Sucre", "Tolú Viejo",
        ],
        "Tolima": [
            "Ibagué", "Espinal", "Melgar", "Honda", "Líbano", "Chaparral", "Mariquita", "Guamo",
            "Purificación", "Flandes", "Fresno", "Lérida", "Armero-Guayabal", "Cajamarca",
            "Venadillo", "Ortega", "Rovira", "Saldaña", "Natagaima", "Coyaima", "Ambalema",
            "Icononzo", "Villahermosa", "Planadas", "Ataco", "Falan", "Alvarado", "Piedras",
        ],
        "Valle del Cauca": [
            "Cali", "Buenaventura", "Palmira", "Tuluá", "Cartago", "Buga", "Jamundí", "Yumbo",
            "Florida", "Candelaria", "Pradera", "Zarzal", "Roldanillo", "La Unión", "Sevilla",
            "Caicedonia", "Dagua", "El Cerrito", "Ginebra", "Guacarí", "Restrepo", "Bugalagrande",
            "Andalucía", "Trujillo", "Riofrío", "Yotoco", "La Cumbre", "Vijes", "Obando",
            "Toro", "Ansermanuevo", "El Águila", "El Cairo", "Argelia", "Versalles", "Alcalá",
            "Ulloa", "El Dovio", "Calima (El Darién)",
        ],
        "Vaupés": ["Mitú", "Carurú", "Taraira"],
        "Vichada": ["Puerto Carreño", "La Primavera", "Santa Rosalía", "Cumaribo"],
    },
    "México": {
        "Ciudad de México": ["Ciudad de México"],
        "Estado de México": ["Toluca", "Ecatepec", "Naucalpan", "Nezahualcóyotl", "Tlalnepantla", "Cuautitlán Izcalli"],
        "Jalisco": ["Guadalajara", "Zapopan", "Tlaquepaque", "Tonalá", "Puerto Vallarta", "Tlajomulco de Zúñiga"],
        "Nuevo León": ["Monterrey", "San Nicolás de los Garza", "Guadalupe", "Apodaca", "San Pedro Garza García"],
        "Puebla": ["Puebla", "Tehuacán", "Cholula"],
        "Guanajuato": ["León", "Irapuato", "Celaya", "Guanajuato", "San Miguel de Allende"],
        "Yucatán": ["Mérida", "Valladolid", "Progreso"],
        "Quintana Roo": ["Cancún", "Playa del Carmen", "Chetumal", "Tulum"],
        "Baja California": ["Tijuana", "Mexicali", "Ensenada"],
        "Veracruz": ["Veracruz", "Xalapa", "Coatzacoalcos"],
        "Querétaro": ["Querétaro", "San Juan del Río"],
        "Chihuahua": ["Chihuahua", "Ciudad Juárez"],
        "Sonora": ["Hermosillo", "Ciudad Obregón", "Nogales"],
        "Oaxaca": ["Oaxaca de Juárez", "Salina Cruz"],
        "Sinaloa": ["Culiacán", "Mazatlán", "Los Mochis"],
    },
    "Argentina": {
        "Ciudad Autónoma de Buenos Aires": ["Buenos Aires"],
        "Buenos Aires": ["La Plata", "Mar del Plata", "Bahía Blanca", "Quilmes", "Lomas de Zamora", "Tigre", "San Isidro"],
        "Córdoba": ["Córdoba", "Río Cuarto", "Villa Carlos Paz", "Villa María"],
        "Santa Fe": ["Rosario", "Santa Fe", "Rafaela"],
        "Mendoza": ["Mendoza", "San Rafael", "Godoy Cruz"],
        "Tucumán": ["San Miguel de Tucumán"],
        "Salta": ["Salta"],
        "Entre Ríos": ["Paraná", "Concordia", "Gualeguaychú"],
        "Neuquén": ["Neuquén", "San Martín de los Andes"],
        "Río Negro": ["Bariloche", "General Roca", "Viedma"],
        "Chubut": ["Comodoro Rivadavia", "Trelew", "Puerto Madryn"],
        "Misiones": ["Posadas", "Puerto Iguazú"],
    },
    "Chile": {
        "Región Metropolitana": ["Santiago", "Puente Alto", "Maipú", "La Florida", "Las Condes"],
        "Valparaíso": ["Valparaíso", "Viña del Mar", "Quilpué", "San Antonio"],
        "Biobío": ["Concepción", "Talcahuano", "Los Ángeles", "Chiguayante"],
        "Antofagasta": ["Antofagasta", "Calama"],
        "Araucanía": ["Temuco", "Villarrica", "Angol"],
        "Coquimbo": ["La Serena", "Coquimbo", "Ovalle"],
        "Maule": ["Talca", "Curicó", "Linares"],
        "Los Lagos": ["Puerto Montt", "Osorno", "Castro"],
        "O'Higgins": ["Rancagua", "San Fernando"],
        "Los Ríos": ["Valdivia", "La Unión"],
        "Tarapacá": ["Iquique", "Alto Hospicio"],
        "Magallanes": ["Punta Arenas"],
    },
    "Perú": {
        "Lima": ["Lima", "Callao", "San Juan de Lurigancho", "Miraflores", "Surco"],
        "Arequipa": ["Arequipa", "Camaná"],
        "La Libertad": ["Trujillo", "Chepén"],
        "Piura": ["Piura", "Sullana", "Talara"],
        "Lambayeque": ["Chiclayo", "Lambayeque"],
        "Cusco": ["Cusco", "Urubamba"],
        "Junín": ["Huancayo", "La Oroya"],
        "Loreto": ["Iquitos"],
        "Áncash": ["Chimbote", "Huaraz"],
        "Ica": ["Ica", "Chincha Alta", "Pisco"],
        "Puno": ["Puno", "Juliaca"],
        "Cajamarca": ["Cajamarca", "Jaén"],
    },
    "Ecuador": {
        "Pichincha": ["Quito", "Sangolquí", "Cayambe"],
        "Guayas": ["Guayaquil", "Durán", "Milagro", "Samborondón"],
        "Azuay": ["Cuenca", "Gualaceo"],
        "Manabí": ["Manta", "Portoviejo", "Chone", "Bahía de Caráquez"],
        "Tungurahua": ["Ambato", "Baños de Agua Santa"],
        "El Oro": ["Machala", "Pasaje"],
        "Loja": ["Loja", "Catamayo"],
        "Imbabura": ["Ibarra", "Otavalo"],
        "Esmeraldas": ["Esmeraldas", "Atacames"],
        "Santo Domingo": ["Santo Domingo"],
        "Chimborazo": ["Riobamba"],
        "Los Ríos": ["Babahoyo", "Quevedo"],
    },
    "Venezuela": {
        "Distrito Capital": ["Caracas"],
        "Zulia": ["Maracaibo", "Cabimas", "Ciudad Ojeda"],
        "Carabobo": ["Valencia", "Puerto Cabello"],
        "Aragua": ["Maracay", "La Victoria"],
        "Lara": ["Barquisimeto", "Cabudare"],
        "Bolívar": ["Ciudad Guayana", "Ciudad Bolívar"],
        "Táchira": ["San Cristóbal", "San Antonio del Táchira"],
        "Anzoátegui": ["Barcelona", "Puerto La Cruz", "El Tigre"],
        "Miranda": ["Los Teques", "Guarenas", "Charallave"],
        "Mérida": ["Mérida", "El Vigía"],
        "Nueva Esparta": ["Porlamar", "Pampatar"],
    },
    "España": {
        "Comunidad de Madrid": ["Madrid", "Móstoles", "Alcalá de Henares", "Getafe"],
        "Cataluña": ["Barcelona", "L'Hospitalet de Llobregat", "Badalona", "Tarragona", "Girona", "Lleida"],
        "Andalucía": ["Sevilla", "Málaga", "Córdoba", "Granada", "Almería", "Cádiz", "Jaén", "Huelva"],
        "Comunidad Valenciana": ["Valencia", "Alicante", "Elche", "Castellón de la Plana"],
        "País Vasco": ["Bilbao", "Vitoria-Gasteiz", "San Sebastián"],
        "Galicia": ["Vigo", "A Coruña", "Ourense", "Santiago de Compostela", "Lugo", "Pontevedra"],
        "Castilla y León": ["Valladolid", "Salamanca", "Burgos", "León"],
        "Canarias": ["Las Palmas de Gran Canaria", "Santa Cruz de Tenerife"],
        "Murcia": ["Murcia", "Cartagena"],
        "Aragón": ["Zaragoza", "Huesca", "Teruel"],
        "Islas Baleares": ["Palma de Mallorca", "Ibiza"],
        "Asturias": ["Oviedo", "Gijón"],
    },
    "Estados Unidos": {
        "Florida": ["Miami", "Orlando", "Tampa", "Jacksonville"],
        "Nueva York": ["Nueva York", "Buffalo"],
        "California": ["Los Ángeles", "San Diego", "San Francisco", "San José", "Sacramento"],
        "Texas": ["Houston", "Dallas", "Austin", "San Antonio"],
        "Illinois": ["Chicago"],
        "Nueva Jersey": ["Newark", "Jersey City"],
        "Georgia": ["Atlanta"],
        "Massachusetts": ["Boston"],
    },
}

DEFAULT_COUNTRY = "Colombia"


def list_countries() -> list[str]:
    return sorted(COUNTRIES.keys())


def list_regions(country: str) -> list[str]:
    return sorted(COUNTRIES.get(country, {}).keys())


def list_cities(country: str, region: str | None = None) -> list[str]:
    regions = COUNTRIES.get(country, {})
    if region:
        return sorted(regions.get(region, []))
    return sorted({city for cities in regions.values() for city in cities})


def _flatten() -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []
    for country, regions in COUNTRIES.items():
        for region, cities in regions.items():
            for city in cities:
                rows.append((country, region, city))
    return rows


ALL_CITIES: list[tuple[str, str, str]] = _flatten()


def find_city(city: str, country: str | None = None) -> tuple[str, str, str] | None:
    """Busca una coincidencia exacta (sin distinguir mayúsculas ni tildes)."""
    from ..utils import slugify

    target = slugify(city)
    for row in ALL_CITIES:
        if slugify(row[2]) == target and (not country or row[0] == country):
            return row
    return None

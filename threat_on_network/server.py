import math

import mesa

from .model import ThreatOnNetworkModel, INFECCION, PRODUCCION, numero_infectados
from .agents import AgenteActivoTI, AgenteProceso

# Configuración de represetación


def network_portrayal(G):
    """Configuración de la represetanción de la red
    Es el argumento que le pasamos a `mesa.visualization.NetworkModule` para configurar la represetanción visual

    Returns:
        dict : Configuración de la represetanción de la red
    """

    def color_proceso(agent):
        """Define el color del agente en la represetanción

        Args:
            agent (_type_): El objeto agente

        Returns:
            string : el color del angete
        """
        estado = agent.estado
        return {PRODUCCION.PARADA: "#FF0000", PRODUCCION.CORRIENDO: "#008000"}.get(agent.estado, "#808080")    

    def color_activoTI(agent):
        """Define el color del agente en la represetanción

        Args:
            agent (_type_): El objeto agente

        Returns:
            string : el color del angete
        """
        estado = agent.estado
        tipo = agent.tipo
        if (tipo=='computo'):       return {INFECCION.IMPACTADO: "#330000", INFECCION.INFECTADO: "#FF0000", INFECCION.SUSCEPTIBLE: "#FFFF00"}.get(estado, "#808080")
        if (tipo=='LAN'):           return {INFECCION.INFECTADO: "#FF0000", INFECCION.SUSCEPTIBLE: "#EE8800"}.get(estado, "#808080")
        if (tipo=='informacion'):   return {INFECCION.IMPACTADO: "#330000", INFECCION.INFECTADO: "#FF0000", INFECCION.SUSCEPTIBLE: "#DDAA00"}.get(estado, "#808080")
        if (tipo=='enrutamiento'):  return {INFECCION.INFECTADO: "#FF0000", INFECCION.SUSCEPTIBLE: "#DDBB00"}.get(estado, "#808080")
        if (tipo=='aplicacion'):    return {INFECCION.INFECTADO: "#FF0000", INFECCION.SUSCEPTIBLE: "#888800"}.get(estado, "#808080")

    def edge_color(agent1, agent2):
        """Color del vértice

        Args:
            agent1 (_type_): Uno de los nodos(agente)
            agent2 (_type_): El otro nodo(agente)

        Returns:
            string : el color del vertice entre los agentes
        """
        if type(agent1) is AgenteProceso or type(agent2) is AgenteProceso:
            return "#808000"
        elif INFECCION.INFECTADO in (agent1.estado, agent2.estado):
            return "#800000"
        else:
            return "#000000"

    def edge_width(agent1, agent2):
        """El grosor del vertice 

        Args:
            agent1 (_type_): Uno de los nodos(agente)
            agent2 (_type_): El otro nodo(agente)

        Returns:
            int : grosor del vértice
        """
        if INFECCION.RESISTENTE in (agent1.estado, agent2.estado):
            return 3
        return 2

    def get_agents(source, target):
        """Para mapear los agentes en G.edges"""
        return G.nodes[source]["agent"][0], G.nodes[target]["agent"][0]

    def node_size(agent):
        return 6

    portrayal = dict()

    activos = [{
            "size": node_size(agents[0]),
            "color": color_activoTI(agents[0]),
            "tooltip": f"id: {agents[0].unique_id}<br>{agents[0].tipo}:{agents[0].etiqueta}<br>C:{agents[0].confidencialidad}<br>I:{agents[0].integridad}<br>D:{agents[0].disponibilidad}<br>state: {agents[0].estado.name}",
        }
        for (_, agents) in G.nodes.data("agent") if issubclass(type(agents[0]),AgenteActivoTI)]

    procesos = [{
            "size": node_size(agents[0]),
            "color": color_proceso(agents[0]),
            "tooltip": f"id: {agents[0].unique_id}<br>{agents[0].etiqueta}<br>aporte:+${agents[0].get_aporte()}M<br>state: {agents[0].estado.name}",
        }
        for (_, agents) in G.nodes.data("agent") if type(agents[0]) is AgenteProceso]        
    
    portrayal["nodes"] = activos + procesos

    portrayal["edges"] = [
        {
            "source": source,
            "target": target,
            "color": edge_color(*get_agents(source, target)),
            "width": edge_width(*get_agents(source, target)),
        }
        for (source, target) in G.edges
    ]

    return portrayal


# Para visualizar el modelo en una gráfica de red
# https://mesa.readthedocs.io/en/main/mesa.visualization.modules.html#module-mesa.visualization.modules.NetworkVisualization
moduloRed = mesa.visualization.NetworkModule( network_portrayal, 700, 500)

# Para visualizar los datos en una gráfica
moduloGraficaInfeccion = mesa.visualization.ChartModule(
    [
        {"Label": "Infectados", "Color": "#FF0000"},
        {"Label": "Vulnerables", "Color": "#008000"},
        {"Label": "Parchados", "Color": "#000080"},
        {"Label": "Impactados", "Color": "#888888"},
    ]
)

# Para visualizar los datos en una gráfica
moduloGraficaGanancia = mesa.visualization.ChartModule(
    [
        {"Label": "Ganancia", "Color": "#000000"},        
        {"Label": "Ganancia esperada", "Color": "#888888"},     
    ]
)

# Para mostrar un texto
def get_resistant_susceptible_ratio(model):
    ratio = model.resistant_susceptible_ratio()
    ratio_text = "&infin;" if ratio is math.inf else f"{ratio:.2f}"
    infected_text = str(numero_infectados(model))

    return "Resistant/Susceptible Ratio: {}<br>Infected Remaining: {}".format(
        ratio_text, infected_text
    )


# Parámetros para `ModularServer`
# https://mesa.readthedocs.io/en/latest/mesa.visualization.html#mesa.visualization.ModularVisualization.ModularServer
model_params = {          
    "probabilidad_propagacion": mesa.visualization.Slider(
        "Probabilidad de propagacion",
        0.4,
        0.0,
        1.0,
        0.1,
        description="Probabilidad de que el vecino susceptible sea infectado",
    ),
    "frecuencia_chequeo": mesa.visualization.Slider(
        "frecuencia de chequeo",
        0.4,
        0.0,
        1.0,
        0.1,
        description="Frecuencia con la que los nodos comprueban si están infectados por un virus",
    ),
    "probabilidad_recuperacion": mesa.visualization.Slider(
        "Probabilidad de recuperacion",
        0.0,
        0.0,
        1.0,
        0.1,
        description="Probabilidad de que el virus sea eliminado",
    ),
    "probabilidad_ganar_resistencia": mesa.visualization.Slider(
        "Probabilidad de ganar resistencia",
        0.5,
        0.0,
        1.0,
        0.1,
        description="Probabilidad de que un agente recuperado se convierta en"
         "resistentes a este virus en el futuro",
    ),
    "impacto_confidencialidad": mesa.visualization.Slider(
        "Immpacto en confidenciliada",
        0.5,
        0.0,
        1.0,
        0.1,
        description="Impacto en la confidencialidad del activo",
    ),
    "impacto_integridad": mesa.visualization.Slider(
        "Impacto en integridad",
        0.0,
        0.0,
        1.0,
        0.1,
        description="Impacto en la integridad del activo",
    ),
    "impacto_disponibilidad": mesa.visualization.Slider(
        "Impacto en disponibilidad",
        1.0,
        0.0,
        1.0,
        0.1,
        description="Impacto en la disponibilidad del activo",
    ),      
}
p = None
# https://mesa.readthedocs.io/en/latest/mesa.visualization.html#mesa.visualization.ModularVisualization.ModularServer
server = mesa.visualization.ModularServer(
    ThreatOnNetworkModel,                   # Modelo
    [                                       # Lista de modulos de visualización a mostrar
        moduloRed,         
        moduloGraficaGanancia,
        moduloGraficaInfeccion,        
        get_resistant_susceptible_ratio, 
    ],
    "Modelo de amenaza en red corporativa", # Titulo
    model_params,                           # Parámetros del modelo
)
# Puerto de virualización HTML
server.port = 8521

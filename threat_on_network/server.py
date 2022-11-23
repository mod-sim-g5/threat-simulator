import math

import mesa

from .model import ThreatOnNetworkModel, ESTADO, number_infected

# Configuración de represetación


def network_portrayal(G):
    """Configuración de la represetanción de la red
    Es el argumento que le pasamos a `mesa.visualization.NetworkModule` para configurar la represetanción visual

    Returns:
        dict : Configuración de la represetanción de la red
    """

    def node_color(agent):
        """Define el color del agente en la represetanción

        Args:
            agent (_type_): El objeto agente

        Returns:
            string : el color del angete
        """
        print(agent.estado)
        return {ESTADO.INFECTADO: "#FF0000", ESTADO.SUSCEPTIBLE: "#008000"}.get(agent.estado, "#808080")

    def edge_color(agent1, agent2):
        """Color del vértice

        Args:
            agent1 (_type_): Uno de los nodos(agente)
            agent2 (_type_): El otro nodo(agente)

        Returns:
            string : el color del vertice entre los agentes
        """
        if ESTADO.RESISTENTE in (agent1.estado, agent2.estado):
            return "#000000"
        return "#e8e8e8"

    def edge_width(agent1, agent2):
        """El grosor del vertice 

        Args:
            agent1 (_type_): Uno de los nodos(agente)
            agent2 (_type_): El otro nodo(agente)

        Returns:
            int : grosor del vértice
        """
        if ESTADO.RESISTENTE in (agent1.estado, agent2.estado):
            return 3
        return 2

    def get_agents(source, target):
        """Para mapear los agentes en G.edges"""
        return G.nodes[source]["agent"][0], G.nodes[target]["agent"][0]

    def node_size(agent):
        return 6

    portrayal = dict()
    portrayal["nodes"] = [
        {
            "size": node_size(agents[0]),
            "color": node_color(agents[0]),
            "tooltip": f"id: {agents[0].unique_id}<br>{agents[0].tipo}<br>state: {agents[0].estado.name}",
        }
        for (_, agents) in G.nodes.data("agent")
    ]

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
networkModule = mesa.visualization.NetworkModule(
    network_portrayal, 500, 500)

# Para visualizar los datos en una gráfica
chartModule = mesa.visualization.ChartModule(
    [
        {"Label": "Infected", "Color": "#FF0000"},
        {"Label": "Susceptible", "Color": "#008000"},
        {"Label": "Resistant", "Color": "#808080"},
    ]
)

# Para mostrar un texto
def get_resistant_susceptible_ratio(model):
    ratio = model.resistant_susceptible_ratio()
    ratio_text = "&infin;" if ratio is math.inf else f"{ratio:.2f}"
    infected_text = str(number_infected(model))

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
        description="Probability that susceptible neighbor will be infected",
    ),
    "frecuencia_chequeo": mesa.visualization.Slider(
        "frecuencia de chequeo",
        0.4,
        0.0,
        1.0,
        0.1,
        description="Frequency the nodes check whether they are infected by " "a virus",
    ),
    "probabilidad_recuperacion": mesa.visualization.Slider(
        "Probabilidad de recuperacion",
        0.3,
        0.0,
        1.0,
        0.1,
        description="Probability that the virus will be removed",
    ),
    "probabilidad_ganar_resistencia": mesa.visualization.Slider(
        "Probabilidad de ganar resistencia",
        0.5,
        0.0,
        1.0,
        0.1,
        description="Probability that a recovered agent will become "
        "resistant to this virus in the future",
    ),
}

# https://mesa.readthedocs.io/en/latest/mesa.visualization.html#mesa.visualization.ModularVisualization.ModularServer
server = mesa.visualization.ModularServer(
    ThreatOnNetworkModel,                   # Modelo
    [                                       # Lista de modulos de visualización a mostrar
        networkModule, 
        get_resistant_susceptible_ratio, 
        chartModule
    ],
    "Modelo de amenaza en red corporativa", # Titulo
    model_params,                           # Parámetros del modelo
)
# Puerto de virualización HTML
server.port = 8521

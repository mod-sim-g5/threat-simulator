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
        return {ESTADO.INFECTED: "#FF0000", ESTADO.SUSCEPTIBLE: "#008000"}.get(agent.state, "#808080")

    def edge_color(agent1, agent2):
        """Color del vértice

        Args:
            agent1 (_type_): Uno de los nodos(agente)
            agent2 (_type_): El otro nodo(agente)

        Returns:
            string : el color del vertice entre los agentes
        """
        if ESTADO.RESISTANT in (agent1.state, agent2.state):
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
        if ESTADO.RESISTANT in (agent1.state, agent2.state):
            return 3
        return 2

    def get_agents(source, target):
        """Para mapear los agentes en G.edges"""
        return G.nodes[source]["agent"][0], G.nodes[target]["agent"][0]

    portrayal = dict()
    portrayal["nodes"] = [
        {
            "size": 6,
            "color": node_color(agents[0]),
            "tooltip": f"id: {agents[0].unique_id}<br>state: {agents[0].state.name}",
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
    "virus_spread_chance": mesa.visualization.Slider(
        "Virus Spread Chance",
        0.4,
        0.0,
        1.0,
        0.1,
        description="Probability that susceptible neighbor will be infected",
    ),
    "virus_check_frequency": mesa.visualization.Slider(
        "Virus Check Frequency",
        0.4,
        0.0,
        1.0,
        0.1,
        description="Frequency the nodes check whether they are infected by " "a virus",
    ),
    "recovery_chance": mesa.visualization.Slider(
        "Recovery Chance",
        0.3,
        0.0,
        1.0,
        0.1,
        description="Probability that the virus will be removed",
    ),
    "gain_resistance_chance": mesa.visualization.Slider(
        "Gain Resistance Chance",
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

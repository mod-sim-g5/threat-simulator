import math

import networkx as nx
import pandas as pd 

import mesa

from .agents import AgenteNodo, ESTADO

def number_state(model, estado):
    return sum(1 for a in model.grid.get_all_cell_contents() if a.estado is estado)

def number_infected(model):
    return number_state(model, ESTADO.INFECTADO)


def number_susceptible(model):
    return number_state(model, ESTADO.SUSCEPTIBLE)


def number_resistant(model):
    return number_state(model, ESTADO.RESISTENTE)

def build_graph():
    edges = pd.read_csv('edges.csv')
    print(edges)
    #https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html
    G = nx.from_pandas_edgelist(edges)     
    nodes = pd.read_csv('nodes.csv')
    data = nodes.set_index('nodo').to_dict('index').items()
    G.add_nodes_from(data)
    print(G.nodes(data=True))
    return G

# Modelo
class ThreatOnNetworkModel(mesa.Model):
    """A virus model with some number of agents"""

    def __init__(
        self,        
        probabilidad_propagacion=0.4,
        frecuencia_chequeo=0.4,
        probabilidad_recuperacion=0.3,
        probabilidad_ganar_resistencia=0.5,
    ):
        """_summary_

        Args:
            probabilidad_propagacion        (float, optional): _description_. Defaults to 0.4.
            frecuencia_chequeo              (float, optional): _description_. Defaults to 0.4.
            probabilidad_recuperacion       (float, optional): _description_. Defaults to 0.3.
            probabilidad_ganar_resistencia  (float, optional): _description_. Defaults to 0.5.
        """
        self.G = build_graph()            
        self.num_nodes = self.G.number_of_nodes() 

        self.grid = mesa.space.NetworkGrid(self.G)
        self.schedule = mesa.time.RandomActivation(self)
        
        self.initial_outbreak_size = 1
        self.probabilidad_propagacion = probabilidad_propagacion
        self.frecuencia_chequeo = frecuencia_chequeo
        self.probabilidad_recuperacion = probabilidad_recuperacion
        self.probabilidad_ganar_resistencia = probabilidad_ganar_resistencia

        # Para la gráfica
        self.datacollector = mesa.DataCollector(
            {
                "Infected": number_infected,
                "Susceptible": number_susceptible,
                "Resistant": number_resistant,
            }
        )


        # Crear agentes
        for i, node in enumerate(self.G.nodes()):
            print(str(node)+":"+ self.G.nodes(data=True)[i]['tipo'])
            a = AgenteNodo(
                i,
                self,
                self.G.nodes(data=True)[i]['tipo'],
                ESTADO.INFECTADO if self.G.nodes(data=True)[i]['infectado']==1 else ESTADO.SUSCEPTIBLE,
                self.probabilidad_propagacion,
                self.frecuencia_chequeo,
                self.probabilidad_recuperacion,
                self.probabilidad_ganar_resistencia,
            )
            self.schedule.add(a)
            # Agegar el agente al nodo
            self.grid.place_agent(a, node)

        self.running = True
        self.datacollector.collect(self)

    def resistant_susceptible_ratio(self):
        try:
            return number_state(self, ESTADO.RESISTENTE) / number_state(
                self, ESTADO.SUSCEPTIBLE
            )
        except ZeroDivisionError:
            return math.inf

    def step(self):
        self.schedule.step()
        # collect data
        self.datacollector.collect(self)

    def run_model(self, n):
        for i in range(n):
            self.step()

import math

import networkx as nx
import pandas as pd

import mesa

from .agents import *


def number_state(model, estado):
    return sum(1 for a in model.grid.get_all_cell_contents() if type(a) is AgenteActivoTI and a.estado is estado)


def tasa_ganancia(model):
    return sum(a.get_aporte() for a in model.grid.get_all_cell_contents() if type(a) is AgenteProceso and a.estado is PRODUCCION.CORRIENDO)


def number_infected(model):
    return number_state(model, INFECCION.INFECTADO)


def number_susceptible(model):
    return number_state(model, INFECCION.SUSCEPTIBLE)


def number_resistant(model):
    return number_state(model, INFECCION.RESISTENTE)


def cargar_nodos(G, file):
    nodes = pd.read_csv(file, sep='\t+')
    data = nodes.set_index('nodo').to_dict('index').items()
    G.add_nodes_from(data)
    return G


def build_graph():
    G = nx.Graph()
    edges = pd.read_csv('input/vertices.csv', sep='\t+')
    print(edges)
    for i in edges.index:
        G.add_edge(int(edges['source'][i]), int(edges['target'][i]))

    cargar_nodos(G, 'input/LAN.csv')
    cargar_nodos(G, 'input/hosts.csv')
    cargar_nodos(G, 'input/enrutamiento.csv')
    cargar_nodos(G, 'input/procesos.csv')
    cargar_nodos(G, 'input/informacion.csv')

    print("Grafo:")
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
        impacto_confidencialidad=0.5,
        impacto_integridad=0.5,
        impacto_disponibilidad=0.5,
    ):
        """_summary_

        Args:
            probabilidad_propagacion        (float, optional): _description_. Defaults to 0.4.
            frecuencia_chequeo              (float, optional): _description_. Defaults to 0.4.
            probabilidad_recuperacion       (float, optional): _description_. Defaults to 0.3.
            probabilidad_ganar_resistencia  (float, optional): _description_. Defaults to 0.5.
        """

        # Grafo
        self.G = build_graph()
        self.num_nodes = self.G.number_of_nodes()

        # Esto es de MEsa
        self.grid = mesa.space.NetworkGrid(self.G)
        self.schedule = mesa.time.RandomActivation(self)

        # 5.3. Impacto del ataque
        self.impacto_confidencialidad = impacto_confidencialidad
        self.impacto_integridad = impacto_integridad
        self.impacto_disponibilidad = impacto_disponibilidad
        self.tipo_activo_objetivo = "informacion"

        # Probalidades
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
                "Ganancia": tasa_ganancia
            }
        )

        # Crear agentes
        print("Nodos:")
        for i, node in enumerate(self.G.nodes()):       
            print(node)     
            print(self.G.nodes(data=True)[node])     
            tipo = self.G.nodes(data=True)[node]['tipo']
            etiqueta = self.G.nodes(data=True)[node]['etiqueta']
            print(str(node)+": '"+str(etiqueta)+"' " + tipo)
            if tipo == 'copmuto':
                a = AgenteComputo(
                    node,
                    self,
                    etiqueta,
                    tipo,
                    self.probabilidad_propagacion,
                    self.frecuencia_chequeo,
                    self.probabilidad_recuperacion,
                    self.probabilidad_ganar_resistencia,
                    INFECCION.INFECTADO if self.G.nodes(
                        data=True)[node]['infectado'] == 1 else INFECCION.SUSCEPTIBLE,
                    self.G.nodes(data=True)[node]['protocolo_infectable']
                )
            elif tipo == 'proceso':
                a = AgenteProceso(
                    node,
                    self,
                    etiqueta,
                    PRODUCCION.CORRIENDO,
                    self.G.nodes(data=True)[node]['aporte']
                )
            else:
                a = AgenteActivoTI(
                    node,
                    self,
                    etiqueta,
                    self.G.nodes(data=True)[node]['tipo'],
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
            return number_state(self, INFECCION.RESISTENTE) / number_state(
                self, INFECCION.SUSCEPTIBLE
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

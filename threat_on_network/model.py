import math

import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import threading
import multiprocessing as mp
import mesa

from .agents import *

import pprint

pp = pprint.PrettyPrinter(indent=4,width=2)
from IPython.lib.pretty import pprint

def number_state(model, estado):
    """cacula el numero de nodos con estado"""
    return sum(1 for a in model.grid.get_all_cell_contents() if type(a) is AgenteActivoTI and a.estado is estado)


def tasa_ganancia(model):
    """suma la tasa actual de produccion"""
    return sum(a.get_aporte() for a in model.grid.get_all_cell_contents() if type(a) is AgenteProceso and a.estado is PRODUCCION.CORRIENDO)

def tasa_ganancia_esperada(model):
    """suma la tasa actual de produccion"""
    return sum(a.aporte for a in model.grid.get_all_cell_contents() if type(a) is AgenteProceso and a.estado is PRODUCCION.CORRIENDO)

def numero_infectados(model):
    return number_state(model, INFECCION.INFECTADO)


def numero_vulnerables(model):
    return number_state(model, INFECCION.SUSCEPTIBLE)


def numero_resistentes(model):
    return number_state(model, INFECCION.RESISTENTE)

def numero_impactados(model):
    return number_state(model, INFECCION.IMPACTADO)

def cargar_nodos(G, file):
    nodes = pd.read_csv(file, dtype = str, sep='\t+', engine='python')
    data = nodes.set_index('nodo').to_dict('index').items()
    print("Datos de "+file)
    pp.pprint(nodes)
    G.add_nodes_from(data)
    return G


def crear_grafo():
    """Construir grafo
    ¡IMPORTANTE! que primero se agreguen los nodos y luego si se agreguen las vertices
    se deben agregar en orden ascendente
    """
    # Instanciar un nuevo grafo simple
    G = nx.Graph()

    #for i in range(11):
        #G.add_node(i)

    #vertices
    edges = pd.read_csv('input/vertices.csv', dtype = str, sep='\t+', engine='python') 
    edges = edges.sort_values(by=['source', 'target'])
    print(edges)
    for i in edges.index:
        G.add_edge(str(edges['source'][i]), str(edges['target'][i]))

    #nodos
    archivos_nodos = [
        'input/informacion.csv',
        'input/procesos.csv',
        'input/LAN.csv',
        'input/hosts.csv',
        'input/enrutamiento.csv',                
    ]

    for f in archivos_nodos:
        cargar_nodos(G, f) 

    """
    NetworkX:
    Hasta aquí serviría normal para liberrias como matplotlib
    Para que Mesa funcione el indice y el label de cada nodo debe coincidir
    """    
    
    #pp.pprint(G.nodes(data=True))
    #pp.pprint(G.edges(data=True))
    
    relabel_map = dict([ (n,int(i)) for i,n in enumerate(G.nodes())])
    print("Re-etiquetado: ",end="")
    print(relabel_map)
    
    G = nx.relabel_nodes(G, relabel_map)        
    
    print("Grafo:")    
    pprint(G.nodes(data=True))
    pprint(G.edges(data=True))     
    """
    El codigo hace el grafo bien, con los nodos y vertices correctamente hasta acá
    """
    return G

def plotting_thread(G,):
    nx.draw(G,with_labels = True)
    plt.show()

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
        self.G = crear_grafo()
        p = mp.Process(target=plotting_thread, args=(self.G,))
        p.start()

        self.num_nodes = self.G.number_of_nodes()

        # Esto es de Mesa
        self.grid = mesa.space.NetworkGrid(self.G) #!
        self.schedule = mesa.time.RandomActivation(self) # activa cada agente en cada circlo en orden aleatorio

        # 5.3. Impacto del ataque
        self.impacto_confidencialidad = impacto_confidencialidad
        self.impacto_integridad = impacto_integridad
        self.impacto_disponibilidad = impacto_disponibilidad
        self.tipo_activo_objetivo = "computo"
        self.protocolo_infeccion = 80

        # Probalidades
        self.probabilidad_propagacion = probabilidad_propagacion
        self.frecuencia_chequeo = frecuencia_chequeo
        self.probabilidad_recuperacion = probabilidad_recuperacion
        self.probabilidad_ganar_resistencia = probabilidad_ganar_resistencia

        # Para la gráfica
        self.datacollector = mesa.DataCollector(
            {
                "Infectados": numero_infectados,
                "Vulnerables": numero_vulnerables,
                "Parchados": numero_resistentes,
                "Impactados": numero_impactados,
                "Ganancia": tasa_ganancia,
                "Ganancia esperada": tasa_ganancia_esperada
            }
        )

        # Crear agentes
        print("Creación de agentes: Nodos:")
        for i, node in enumerate(self.G.nodes()):   # por cada uno de los nodos en el grafo
            """
            Para que Mesa funcione el indice y el label de cada nodo debe coincidir
            int : INT
            node : int
            """          
            print("["+str(node)+"]", end='=?')   
            print(i, end=',')               
            print(self.G.nodes(data=True)[node])     
            tipo = self.G.nodes(data=True)[node]['tipo']
            etiqueta = self.G.nodes(data=True)[node]['etiqueta']
            
            """Mesa crea un agente para agregarlo como atributo al nodo de NetworkX"""
            #print(str(node)+": '"+str(etiqueta)+"' " + tipo)
            if tipo == 'computo':
                agente = AgenteComputo(
                    i,  
                    self,
                    etiqueta,
                    self.probabilidad_propagacion,
                    self.frecuencia_chequeo,
                    self.probabilidad_recuperacion,
                    self.probabilidad_ganar_resistencia,
                    INFECCION.INFECTADO if int(self.G.nodes(data=True)[node]['infectado']) == 1 else INFECCION.SUSCEPTIBLE,
                    self.protocolo_infeccion,
                    float(self.G.nodes(data=True)[node]['antivirus']),
                    float(self.G.nodes(data=True)[node]['costo_antivirus'])
                )
                
            elif tipo == 'proceso':
                agente = AgenteProceso(
                    i,
                    self,
                    etiqueta,
                    PRODUCCION.CORRIENDO,
                    self.G.nodes(data=True)[node]['aporte']
                )                              
            else:
                agente = AgenteActivoTI(
                    i,
                    self,
                    etiqueta,
                    self.G.nodes(data=True)[node]['tipo'],
                    self.probabilidad_propagacion,
                    self.frecuencia_chequeo,
                    self.probabilidad_recuperacion,
                    self.probabilidad_ganar_resistencia,
                    INFECCION.INFECTADO if int(self.G.nodes(data=True)[node]['infectado']) == 1 else INFECCION.SUSCEPTIBLE,
                )
            self.schedule.add(agente)
            print("agente",agente)
            # Agegar el objeto agente como atributo al nodo nodo
            self.grid.place_agent(agente, node) 

        print("Agents:")
        pp.pprint([a.etiqueta for a in self.grid.get_all_cell_contents()])
        self.running = True
        self.datacollector.collect(self)



        #final consutrccion de modelo

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




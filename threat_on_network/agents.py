import mesa
from enum import Enum

class INFECCION(Enum):
    SUSCEPTIBLE = 0
    INFECTADO = 1
    RESISTENTE = 2

class PRODUCCION(Enum):
    PARADA = 0
    CORRIENDO = 1

class AgenteActivoTI(mesa.Agent):
    def __init__(
        self,
        id,
        model,
        etiqueta=id,
        tipo='computo',        
        probabilidad_propagacion=0.4,
        frecuencia_chequeo=0.4,
        probabilidad_recuperacion=0.2,
        probabilidad_ganar_resistencia=0.1,
        estado_inicial=INFECCION.SUSCEPTIBLE,        
        protocolo_infectable=0,
    ):
        super().__init__(id, model)
        self.etiqueta = etiqueta
        self.tipo = tipo

        # Infección
        self.estado = estado_inicial
        self.protocolo_infectable = protocolo_infectable

        # Seguridad y rendimiento
        self.confidencialidad = 1
        self.integridad = 1
        self.disponibilidad = 1


        self.probabilidad_propagacion = probabilidad_propagacion
        self.frecuencia_chequeo = frecuencia_chequeo
        self.probabilidad_recuperacion = probabilidad_recuperacion
        self.probabilidad_ganar_resistencia = probabilidad_ganar_resistencia

    def try_to_infect_neighbors(self):
        nodos_vecinos = self.model.grid.get_neighbors(self.pos, include_center=False)
        vecinos_suceptibles = [
            agent
            for agent in self.model.grid.get_cell_list_contents(nodos_vecinos)
            if agent.estado is INFECCION.SUSCEPTIBLE
        ]
        for a in vecinos_suceptibles:
            if self.random.random() < self.probabilidad_propagacion:
                a.estado = INFECCION.INFECTADO

    def try_gain_resistance(self):
        if self.random.random() < self.probabilidad_ganar_resistencia:
            self.estado = INFECCION.RESISTENTE

    def try_remove_infection(self):
        # Try to remove
        if self.random.random() < self.probabilidad_recuperacion:
            # Success
            self.estado = INFECCION.SUSCEPTIBLE
            self.try_gain_resistance()
        else:
            # Failed
            self.estado = INFECCION.INFECTADO

    def try_check_situation(self):
        if self.random.random() < self.frecuencia_chequeo:
            # Checking...
            if self.estado is INFECCION.INFECTADO:
                self.try_remove_infection()

    def step(self):
        if self.estado is INFECCION.INFECTADO:
            self.try_to_infect_neighbors()
            self.confidencialidad = 1-self.model.impacto_confidencialidad
            self.integridad = 1-self.model.impacto_integridad
            self.disponibilidad = 1-self.model.impacto_disponibilidad

        self.try_check_situation()

class AgenteComputo(AgenteActivoTI):
    def __init__(
        self,
        id,
        model,
        etiqueta=id,          
        probabilidad_propagacion=0.4,
        frecuencia_chequeo=0.4,
        probabilidad_recuperacion=0.2,
        probabilidad_ganar_resistencia=0.1,
        estado_inicial=INFECCION.SUSCEPTIBLE,        
        protocolo_infectable=0,        
    
    ):
        super().__init__(
            id,
            model,
            etiqueta,
            'computo',
            probabilidad_propagacion,
            frecuencia_chequeo,
            probabilidad_recuperacion,
            probabilidad_ganar_resistencia,
            estado_inicial,
            protocolo_infectable 
        )     

class AgenteInformacion(mesa.Agent):
    def __init__(
        self,
        id,
        model,
        etiqueta,
        tipo,        
        probabilidad_propagacion,
        frecuencia_chequeo,
        probabilidad_recuperacion,
        probabilidad_ganar_resistencia,
        estado_inicial=INFECCION.SUSCEPTIBLE,        
        protocolo_infectable=0,
    ):
        super().__init__(id, model)
        self.etiqueta = etiqueta
        self.tipo = tipo

        # Infección
        self.estado = estado_inicial
        self.protocolo_infectable = protocolo_infectable

        # Seguridad y rendimiento
        self.confidencialidad = 1
        self.integridad = 1
        self.disponibilidad = 1


        self.probabilidad_propagacion = probabilidad_propagacion
        self.frecuencia_chequeo = frecuencia_chequeo
        self.probabilidad_recuperacion = probabilidad_recuperacion
        self.probabilidad_ganar_resistencia = probabilidad_ganar_resistencia  
  


class AgenteProceso(mesa.Agent):
    def __init__(
        self,
        id,
        model,
        etiqueta,
        estado_inicial,
        aporte=0,
    ):
        super().__init__(id, model)
        self.etiqueta = etiqueta
        self.estado = estado_inicial
        self.aporte = float(aporte)
        self.produccion = 1

    def get_aporte(self):
        return self.get_produccion() * self.aporte 

    def get_produccion(self):
        nodos_vecinos = self.model.grid.get_neighbors(self.pos, include_center=False)
        activos_dependencia = [ 
            agent.disponibilidad for agent in self.model.grid.get_cell_list_contents(nodos_vecinos) if type(agent) is AgenteActivoTI  
        ]         
        if len(activos_dependencia)==0: return 0
        else: return sum(activos_dependencia) / len(activos_dependencia)



# Usuarios
# Información y datos
# Aplicación
# Computo
# LAN
# Enrutamiento


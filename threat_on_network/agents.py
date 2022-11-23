import mesa
from enum import Enum

class ESTADO(Enum):
    SUSCEPTIBLE = 0
    INFECTADO = 1
    RESISTENTE = 2

class AgenteNodo(mesa.Agent):
    def __init__(
        self,
        id,
        model,
        tipo,
        estado_inicial,
        probabilidad_propagacion,
        frecuencia_chequeo,
        probabilidad_recuperacion,
        probabilidad_ganar_resistencia,
    ):
        super().__init__(id, model)
        self.tipo = tipo
        self.estado = estado_inicial

        self.probabilidad_propagacion = probabilidad_propagacion
        self.frecuencia_chequeo = frecuencia_chequeo
        self.probabilidad_recuperacion = probabilidad_recuperacion
        self.probabilidad_ganar_resistencia = probabilidad_ganar_resistencia

    def try_to_infect_neighbors(self):
        neighbors_nodes = self.model.grid.get_neighbors(self.pos, include_center=False)
        susceptible_neighbors = [
            agent
            for agent in self.model.grid.get_cell_list_contents(neighbors_nodes)
            if agent.state is ESTADO.SUSCEPTIBLE
        ]
        for a in susceptible_neighbors:
            if self.random.random() < self.probabilidad_propagacion:
                a.state = ESTADO.INFECTADO

    def try_gain_resistance(self):
        if self.random.random() < self.probabilidad_ganar_resistencia:
            self.estado = ESTADO.RESISTENTE

    def try_remove_infection(self):
        # Try to remove
        if self.random.random() < self.probabilidad_recuperacion:
            # Success
            self.estado = ESTADO.SUSCEPTIBLE
            self.try_gain_resistance()
        else:
            # Failed
            self.estado = ESTADO.INFECTADO

    def try_check_situation(self):
        if self.random.random() < self.frecuencia_chequeo:
            # Checking...
            if self.estado is ESTADO.INFECTADO:
                self.try_remove_infection()

    def step(self):
        if self.estado is ESTADO.INFECTADO:
            self.try_to_infect_neighbors()
        self.try_check_situation()
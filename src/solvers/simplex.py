import numpy as np

class Simplex:
    def __init__(self, c, A, b, desigualdades=None):
        self.c_original = np.array(c, dtype=float)
        self.A_original = np.array(A, dtype=float)
        self.b_original = np.array(b, dtype=float)
        self.desigualdades = desigualdades if desigualdades else ['<=']*len(b)
        self.m, self.n = self.A_original.shape
        self.holguras = []
        self.artificiales = []
        self.basicas = []
        self.CB = []  # Almacenar CB separadamente
        self.fase = 1
        self.etiquetas = []
        self.tabla = None  # Tabla solo contendrá A|b
        self.obj = 0.0  # Valor objetivo separado
        self.iterations_str = ""
        
        self.forma_estandar()
        self.Only2Fase = len(self.artificiales) == 0        
        self.get_base()
        
        
    def forma_estandar(self):
        # Añadir variables de holgura/exceso
        self.holguras = []
        for i, des in enumerate(self.desigualdades):
            if des == '<=':
                self.A_original = np.hstack([self.A_original, np.zeros((self.m, 1))])
                self.A_original[i, -1] = 1
                self.holguras.append(self.A_original.shape[1]-1)
            elif des == '>=':
                self.A_original = np.hstack([self.A_original, np.zeros((self.m, 1))])
                self.A_original[i, :] *= -1
                self.A_original[i, -1] = 1
                self.holguras.append(self.A_original.shape[1]-1)
                
                # Añadir variable artificial para >=
                if self.b_original[i] > 0:
                    self.artificiales.append(self.A_original.shape[1])
                    self.A_original = np.hstack([self.A_original, np.zeros((self.m, 1))])
                    self.A_original[i, -1] = 1
                else:
                    self.b_original[i] *= -1            
            elif des == '=':
                # Añadir variable artificial para =
                self.artificiales.append(self.A_original.shape[1])
                self.A_original = np.hstack([self.A_original, np.zeros((self.m, 1))])
                self.A_original[i, -1] = 1
        
        self.n = self.A_original.shape[1]
        self.c = np.zeros(self.n)
        self.c[:len(self.c_original)] = self.c_original
        
    def imprimir_tabla(self):
        # Construir la tabla como cadena
        tabla_str = ""
        encabezados = ["CB", "VB"] + self.etiquetas
        anchos = [8, 8] + [10] * len(self.etiquetas) + [10]
        
        # Línea superior
        tabla_str += "\n" + "-" * sum(anchos) + "\n"
        
        # Encabezados
        tabla_str += "|".join(h.center(w) for h, w in zip(encabezados, anchos)) + "\n"
        tabla_str += "-" * sum(anchos) + "\n"
        
        # Filas de restricciones
        for i in range(self.m):
            fila = [
                f"{self.CB[self.basicas[i]]:.2f}".center(8),
                self.etiquetas[self.basicas[i]].center(8)
            ] + [f"{self.tabla[i, j]:.2f}".center(10) for j in range(self.tabla.shape[1] - 1)] + [f"{self.tabla[i, -1]:.2f}".center(10)]  #[f"{self.tabla[i, -1]:.2f}".center(10)]
            tabla_str += "|".join(fila) + "\n"
        
        # Línea divisoria
        tabla_str += "-" * sum(anchos) + "\n"
        
        # Fila Z
        z_fila = [
            "Z".center(8),
            "".center(8)
        ] + [f"{cr:.2f}".center(10) for cr in self.calcular_costos_reducidos()]
        tabla_str += "|".join(z_fila) + "\n"
        tabla_str += "-" * sum(anchos) + "\n"
        
        return tabla_str  # Devolver cadena en lugar de imprimir   

    
    def inicializar_tabla(self, fase, tabla):
        # Tabla para Fase 1: [A | b]
        self.tabla = tabla
        self.etiquetas = [f'x{i+1}' for i in range(len(self.c_original))]
        self.etiquetas += [f'h{i+1}' for i in range(len(self.holguras))]
        self.etiquetas += [f'a{i+1}' for i in range(len(self.artificiales))]
        self.etiquetas.append("LD")  # Columna LD
        
        # Inicializar CB para artificiales = 1
        if fase == 2:
            self.CB = np.array([ self.c_original[int(etq[1:]) - 1] if etq.startswith('x') else 0.0 for etq in self.etiquetas[:-1]])
        else:
            self.CB = np.array([1.0 if etq.startswith('a') else 0.0 for etq in self.etiquetas[:-1]])
            #self.basicas = self.artificiales.copy()
            
        # Función objetivo Fase 1: min sum(artificiales)
        # self.obj = sum(self.tabla[i, -1] for i in range(self.m))
        
    def calcular_costos_reducidos(self):
        costos_reducidos = []
        for j in range(self.tabla.shape[1] - 1):  # Excluir columna LD
            if self.fase == 1:
                c_j = 1.0 if self.etiquetas[j].startswith('a') else 0.0
            else:
                c_j = self.c_original[j] if j < len(self.c_original) else 0.0
                
            suma = sum(self.CB[self.basicas[i]] * self.tabla[i, j] for i in range(self.m))
            costos_reducidos.append(c_j - suma)
        
        # Calcular valor objetivo actual
        self.obj = sum(self.CB[self.basicas[i]] * self.tabla[i, -1] for i in range(self.m))
        return costos_reducidos + [self.obj]
            
    def seleccionar_entrada(self):
        # Regla de Bland: seleccionar la primera columna con rj < 0
        costos = self.calcular_costos_reducidos()
        for j in range(len(costos) - 1):
            if costos[j] < -1e-6 and j not in self.artificiales:
                return j

        return -1
        
    def seleccionar_salida(self, q):
        ratios = []
        for i in range(self.m):
            if self.tabla[i, q] > 1e-6:
                ratio = self.tabla[i, -1] / self.tabla[i, q]
                ratios.append((i, ratio))
        if not ratios:
            return -1
        # Regla de Bland: menor índice si hay empate
        min_ratio = min(ratios, key=lambda x: (x[1], x[0]))
        return min_ratio[0]
        
    def pivot(self, p, q):
        # Normalizar fila pivote
        pivot_val = self.tabla[p, q]
        self.tabla[p, :] /= pivot_val
        
        # Eliminar otras filas
        for i in range(self.m):
            if i != p and self.tabla[i, q] != 0:
                factor = self.tabla[i, q]
                self.tabla[i, :] -= factor * self.tabla[p, :]
        
        # Actualizar CB y variables básicas        
        if self.fase == 1 and self.basicas[p] in self.artificiales:
            self.tabla = np.delete(self.tabla, self.basicas[p], axis=1)
            self.CB = np.delete(self.CB, self.basicas[p])

            for i, basica in enumerate(self.basicas):
                if basica > self.basicas[p]:
                    self.basicas[i] -= 1
                    
            for i, art in enumerate(self.artificiales):
                if art > self.basicas[p]:
                    self.artificiales[i] -= 1
            
            self.etiquetas.remove(f"{self.etiquetas[self.basicas[p]]}")
            self.artificiales.remove(self.basicas[p])
            self.basicas[p] = q
            
            
            self.n -= 1
        else:
            #self.CB[self.basicas[p]] = self.c_original[q]
            self.basicas[p] = q
                
    def fase1(self):
        self.iterations_str += "\n--- FASE 1: BUSCANDO SOLUCIÓN FACTIBLE INICIAL ---"
        
        # Iterar hasta alcanzar optimalidad
        while True:
            self.iterations_str += self.imprimir_tabla()
            
            q = self.seleccionar_entrada()
            if q == -1:  # Si no hay más variables para entrar
                break

            p = self.seleccionar_salida(q)
            if p == -1:  # Si no se puede seleccionar fila pivote
                raise ValueError("Problema no acotado en Fase 1")
                        
            self.iterations_str += f"\nPivote: Fila {self.etiquetas[self.basicas[p]]}, Columna {self.etiquetas[q]}"
            self.pivot(p, q)       
            

        # Verificar si se encontró solución factible
        if not np.isclose(self.obj, 0, atol=1e-6):
            raise ValueError("No existe solución factible")

        # Manejar variables artificiales básicas
        nuevas_filas = []
        nuevas_basicas = []
        for i, j in enumerate(self.basicas):
            print_t = False
            if j in self.artificiales:
                # Intentar pivotear para reemplazar artificiales
                print_t = True
                pivote_encontrado = False
                for col in range(len(self.etiquetas)):
                    if not np.isclose(self.tabla[i, col], 0) and col not in self.artificiales:
                        self.pivot(i, col)
                        nuevas_filas.append(self.tabla[i])
                        nuevas_basicas.append(col)
                        pivote_encontrado = True
                        break
                if not pivote_encontrado:
                    self.iterations_str +=f"\nEliminando restricción redundante {i + 1}"
                    continue
            else:
                nuevas_filas.append(self.tabla[i])
                nuevas_basicas.append(j)
            
            if print_t:
                self.iterations_str += "\nEliminando variables artificacioles de la base"
                self.iterations_str += self.imprimir_tabla()

        # Verificar si hay filas válidas
        if not nuevas_filas:
            raise ValueError("Problema no factible: todas las restricciones son redundantes")

        self.iterations_str += "\n--- FIN DE FASE 1 ---"

    def fase2(self):
        self.iterations_str += "\n--- FASE 2: OPTIMIZANDO SOLUCIÓN ---"
        self.fase = 2
        
        #print(self.imprimir_tabla())
        
        while True:
            self.iterations_str += self.imprimir_tabla()
            
            q = self.seleccionar_entrada()
            if q == -1: break
            
            p = self.seleccionar_salida(q)
            if p == -1:
                raise ValueError("Problema no acotado en Fase 2")
                
            self.iterations_str += f"\nPivote: Fila {self.etiquetas[self.basicas[p]]}, Columna {self.etiquetas[q]}"
            self.pivot(p, q)
            
            
    def get_base(self):
        """Determina si existe una base factible inicial sin variables artificiales"""
        # Buscar columnas que formen una matriz identidad
        ident_cols = []
        for i in range(self.A_original.shape[1]):
            col = self.A_original[:, i]
            if sum(col == 0) == self.m - 1 and sum(col == 1) == 1:
                ident_cols.append(i)
        
        if len(ident_cols) >= self.m:
            self.basicas = ident_cols
    
    
    def resolver(self):    
        if self.Only2Fase:
            self.iterations_str += "\n--- INICIANDO DIRECTAMENTE EN FASE 2 ---"
            self.inicializar_tabla(2, np.hstack([self.A_original, self.b_original.reshape(-1, 1)]))
        else:
            self.inicializar_tabla(1, np.hstack([self.A_original, self.b_original.reshape(-1, 1)]))
            self.fase1()
            self.inicializar_tabla(2, self.tabla)

        self.fase2()
        
        # Obtener solución
        solucion = np.zeros(len(self.c_original))
        for i in range(self.m):
            if self.basicas[i] < len(self.c_original):
                solucion[self.basicas[i]] = self.tabla[i, -1]  # Usar LD correcto      
            
        return solucion, round(self.obj,2), self.iterations_str

# Ejemplo del documento
if __name__ == "__main__":
    c = [4, 1, 1]
    A = [
        [2, 1, 2],
        [3, 3, 1]
    ]
    b = [4, 3]
    
    solver = Simplex(c, A, b, ['=', '='])
    sol, obj = solver.resolver()
    

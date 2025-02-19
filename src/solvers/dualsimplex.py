import numpy as np

class DualSimplex:
    def __init__(self, c, A, b, desigualdades=None):
        self.c_original = np.array(c, dtype=float)
        self.A_original = np.array(A, dtype=float)
        self.b_original = np.array(b, dtype=float)
        self.desigualdades = desigualdades if desigualdades else ['<=']*len(b)
        self.m, self.n = self.A_original.shape
        self.holguras = []
        self.basicas = []
        self.CB = []  # Almacenar CB separadamente
        self.etiquetas = []
        self.tabla = None  # Tabla solo contendrá A|b
        self.obj = 0.0  # Valor objetivo separado
        self.iterations_str = ""
        
        self.forma_estandar()
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
                self.b_original[i] *= -1
                self.A_original[i, -1] = 1
                self.holguras.append(self.A_original.shape[1]-1)         
            elif des == '=':
                self.A_original = np.hstack([self.A_original, np.zeros((self.m, 1))])
                self.A_original[i, -1] = -1
                self.b_original[i] *= -1
                self.holguras.append(self.A_original.shape[1]-1) 
        
        self.n = self.A_original.shape[1]

        
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

    
    def inicializar_tabla(self, tabla):
        # Tabla para Fase 1: [A | b]
        self.tabla = tabla
        self.etiquetas = [f'x{i+1}' for i in range(len(self.c_original))]
        self.etiquetas += [f'h{i+1}' for i in range(len(self.holguras))]
        self.etiquetas.append("LD")  # Columna LD
        
        # Inicializar CB 
        self.CB = np.array([ self.c_original[int(etq[1:]) - 1] if etq.startswith('x') else 0.0 for etq in self.etiquetas[:-1]])
        
        # Función objetivo Fase 1: min sum(artificiales)
        # self.obj = sum(self.tabla[i, -1] for i in range(self.m))
        
    def calcular_costos_reducidos(self):
        costos_reducidos = []
        for j in range(self.tabla.shape[1] - 1):  # Excluir columna LD
            c_j = self.c_original[j] if j < len(self.c_original) else 0.0 
            suma = sum(self.CB[self.basicas[i]] * self.tabla[i, j] for i in range(self.m))
            costos_reducidos.append(c_j - suma)
        
        # Calcular valor objetivo actual
        self.obj = sum(self.CB[self.basicas[i]] * self.tabla[i, -1] for i in range(self.m))
        return costos_reducidos + [self.obj]
            
    def seleccionar_salida(self):
        # Regla de Bland: seleccionar la primera columna con rj < 0
        for i in range(self.m):
            if self.tabla[i, -1] < -1e-6:
                return i

        return -1
        
    def seleccionar_entrada(self, p):
        ratios = []
        r = self.calcular_costos_reducidos()
        for j in range(len(r) - 1):
            if self.tabla[p, j] < 0:
                ratio = -r[j] / self.tabla[p, j]
                ratios.append((j, ratio))
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
        self.basicas[p] = q
                
    def DualSimplex(self):
        #print(self.imprimir_tabla())
        
        while True:
            self.iterations_str += self.imprimir_tabla()
            
            p = self.seleccionar_salida()
            if p == -1:
                break
            
            q = self.seleccionar_entrada(p)
            if q == -1: 
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
    
    def dual_factible(self):
        for rj in self.calcular_costos_reducidos():
            if rj  <  1e-6:
                return False
        
        for i in range(self.m):
            if self.tabla[i, -1] <  1e-6:
                return True
            
        return False
                
    
    def resolver(self):    
        self.iterations_str += "\n--- INICIANDO DUALSIMPLEX ---"
        self.inicializar_tabla(np.hstack([self.A_original, self.b_original.reshape(-1, 1)]))
        
        if not self.dual_factible:
            self.iterations_str += "\nEl POL no es Dual Factible"
            return { np.empty, -1, self.iterations_str}
        
        self.DualSimplex()
        
        # Obtener solución
        solucion = np.zeros(len(self.c_original))
        for i in range(self.m):
            if self.basicas[i] < len(self.c_original):
                solucion[self.basicas[i]] = self.tabla[i, -1]  # Usar LD correcto      
            
        return solucion, round(self.obj,2), self.iterations_str
    
if __name__ == "__main__":
    c = [3, 2, 1]
    A = [
        [1, 1, -1],
        [-2, -1, 2]
    ]
    b = [5, 4]
    
    solver = DualSimplex(c, A, b, ['>=', '>='])
    sol, obj, iter = solver.resolver()
    print(iter)
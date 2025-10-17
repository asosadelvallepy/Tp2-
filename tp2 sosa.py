import numpy as np
from PIL import Image

#inputs del programa

ruta_imagen= input("Ingrese la ruta de la imagen:")
metodo= input("Seleccione el metodo:").lower().strip()

if metodo=="vitral":

    n= input("Ingrese la cantidad de puntos:")

    if n=="":
        n=1000 #por default es 1000
    else:
        n=int(n)
        if n<0:
            print("La cantidad de puntos debe ser mayor a 0")

    metrica=input("Ingrese la metrica de distancia (euclidean/manhattan):").lower()
    if metrica!= "euclidean" and metrica!= "manhattan":
        print("La metrica seleccionada no esta dentro de las opciones por default es euclidean")
        metrica="euclidean" #por default es euclidean
    

    ruta_guardar_imagen= input("Seleccione la ruta para guardar imagen procesada:")

elif metodo=="mosaico":
    
    variance_threshold=input( "Ingrese el umbral de varianza (default=150):")
    
    if variance_threshold=="":
        variance_threshold=150 #por default es 150
    else:
        variance_threshold=int(variance_threshold)
        if variance_threshold<0:
            print("El umbral de varianza debe ser mayor a 0")

    min_size=input("Ingrese el tamaño mínimo de bloque (default=20):")
    
    if min_size=="":
        min_size=20 #por default es 20
    else:
        min_size=int(min_size)
        if min_size<0:
            print("EL tamaño minimo de bloque debe ser un numero positivo")

    max_passes= input("Ingrese el número máximo de subdivisiones (default=10):")
    if max_passes=="":
        max_passes=10 #por default es 10 
    else:
        max_passes=int(max_passes)
        if max_passes<0:
            print("El numero maximo de subdivisiones debe ser un numero positivo")


    bordes_bloques= input("¿Dibujar bordes en los bloques? (si/no):")
    ruta_guardar_imagen= input("Seleccione la ruta para guardar la imagen procesada:")

else:
    print("El metodo seleccionado no esta entre las opciones")

#------------------------------------------------------------------------------------------


# Metodo para transformar imagen en algo que podamos usar

def open_image(path:str)->np.ndarray:

    """Abre una imagen desde path, la convierte a RGB y retorna (alto,ancho,3)"""
    img= Image.open(path).convert("RGB") #abre y convierte a RGB
    return np.array(img) #se convierte a arreglo



def puntos(imagen:np.ndarray,n:int)->np.ndarray:
    """
    Devuelve (n, 2) con coordenadas (y, x) de n puntos aleatorios dentro de la imagen.
    imagen=(alto,ancho,3)
    n=cantidad de puntos
    """

    
    random=np.random.default_rng() #genera numeros aleatorios
    
        
    alto,ancho,_= imagen.shape  #dimensiones de la imagen 

    ys= random.integers(0,alto,n) 
    xs=random.integers(0,ancho,n)  #se generan coordenadas aleatorias (n coordenadas) respetando los li,ites que tiene la imagen que son el alto y el ancho
    matriz= np.stack([ys,xs],1) # se apila en columnas [(y0,x0),(y1,x1),etc]
    return matriz

#------------------------------------------------------------------------------------------

# Metodo del vitral
    
def calc_dist(gy:np.ndarray,gx:np.ndarray,sy:int,sx:int,metrica:str)->np.ndarray:

    """
       Calcula la distancia desde todos los pixeles (gy,gx) hasta un punto (sy,sx). 
    Retorna un valor (alto, ancho) con las distancias.
    gy,gx=coordenadas Y y X para cada pixel
    sy,sx=punto especifico
    metrica= si es manhattan o euclidean
    """
    
    if metrica=="manhattan":
        return np.abs(gy-sy)+np.abs(gx-sx) #calculo con el metodo manhattan
    elif metrica=="euclidean":
        return (gy-sy)**2 + (gx-sx)**2 #calculo con el metodo euclidean

def cercanas(alto:int,ancho:int,sitios:np.ndarray,metrica:str)->np.ndarray:
    """
    Para cada píxel de una imagen (alto x ancho), asigna el índice del sitio más cercano según la metrica.
    Retorna 'punto_cerc' con forma (alto, ancho) 
    """
   
    gy=np.arange(alto)[:, None]
    gx=np.arange(ancho)[None, :]

    menor_dist=None  
    punto_cerc= None

    for i, (sy,sx) in enumerate(sitios): #se recorre cada sitio (sy,sx) y se actualiza a medida que se encuentra un punto mas cercano
        dist=calc_dist(gy,gx,sy,sx,metrica) 
        if menor_dist is None: #si no hay un valor para la menor distancia entra al if
            menor_dist= dist #almacena la menor distancia encontrada
            punto_cerc= np.full_like(dist,i)
        else: #si ya hay un valior para la menor distancia chequea si este nuevo valor es aun menor que la menor distancia, y si es asi, actualiza el valor de menor_dist
            matriz_chequeo= dist<menor_dist
            menor_dist[matriz_chequeo]= dist[matriz_chequeo]
            punto_cerc[matriz_chequeo]=i

    return punto_cerc  # retorna (alto,ancho) con el indice del punto mas cercano

def colorear_por_promedio(img: np.ndarray, labels: np.ndarray, n: int) -> np.ndarray:
    """
    Dado 'labels' (alto x ancho) con el índice de sitio por píxel, calcula el color promedio (R,G,B)
    de cada celda (sitio) y pinta toda la celda con ese color promedio.
    - img: imagen original como arreglo (alto, ancho, 3)
    - labels: índice de sitio por píxel (alto, ancho)
    - n: cantidad n de sitios
    Retorna imagen (alto, ancho, 3) con el efecto "vitral".
    """
    flat_labels = labels.ravel()                   # (h*w,)
    pixels = img.reshape(-1, 3).astype(np.float64) # (h*w, 3)

    sums_r = np.bincount(flat_labels, weights=pixels[:, 0], minlength=n)
    sums_g = np.bincount(flat_labels, weights=pixels[:, 1], minlength=n)
    sums_b = np.bincount(flat_labels, weights=pixels[:, 2], minlength=n)
    counts = np.bincount(flat_labels, minlength=n).astype(np.float64) # cuenta de pixeles por sitio
    counts[counts == 0] = 1.0  # evita que se caiga el programa por division por cero si alguna celda quedó vacía

    means = np.stack([sums_r/counts, sums_g/counts, sums_b/counts], axis=1)  # promedio por sitio -->(n, 3)
    out = means[labels]  # (h, w, 3)
    return np.clip(out, 0, 255).astype(np.uint8)

def aplicar_vitral(img: np.ndarray, n: int, metrica: str) -> np.ndarray:
    """
    maneja el vitral: puntos → asignación → coloreo.
    """
    alto, ancho, _ = img.shape
    sites = puntos(img, n)
    labels = cercanas(alto, ancho, sites, metrica)
    return colorear_por_promedio(img, labels, n)

#------------------------------------------------------------------------------------------

# Metodo del mosaico

def calcular_estadisticas_bloque(bloque: np.ndarray):
    """
    Calcula dos cosas importantes de un bloque (una parte de la imagen):
    1. Cuánto varían sus colores (varianza promedio RGB)
    2. Cuál es su color promedio (promedio de R, G y B)
    """
    # Convertimos el bloque a float para evitar errores al promediar
    bloque_float = bloque.astype(np.float32)

    # Calculamos el color promedio de todos los píxeles en R, G y B
    color_promedio = bloque_float.mean(axis=(0, 1))  # → [prom_R, prom_G, prom_B]

    # Calculamos la varianza (qué tanto cambian los colores dentro del bloque)
    var_por_canal = bloque_float.var(axis=(0, 1))     # → [var_R, var_G, var_B]

    # Tomamos el promedio de las varianzas de los 3 canales
    varianza_promedio = float(var_por_canal.mean())

    # Devolvemos ambos valores
    return varianza_promedio, color_promedio



def dibujar_borde_negro(imagen: np.ndarray, top: int, bottom: int, left: int, right: int):
    """
    Dibuja un rectángulo negro alrededor del bloque indicado.
    No usa ImageDraw, se hace directamente sobre el array de píxeles.
    """
    # Dibujamos una línea negra arriba e abajo del bloque
    imagen[top:top+1, left:right] = 0
    imagen[bottom-1:bottom, left:right] = 0

    # Dibujamos una línea negra a la izquierda y a la derecha del bloque
    imagen[top:bottom, left:left+1] = 0
    imagen[top:bottom, right-1:right] = 0



def mosaico_adaptativo_simple(imagen: np.ndarray,
                              umbral_varianza: float = 150.0,
                              tamano_minimo: int = 20,
                              max_niveles: int = 10,
                              con_bordes: bool = True) -> np.ndarray:
    """
    Aplica el efecto de "Mosaico adaptativo" o "subdivisión adaptativa".

    La idea es:
    1. Empezar con toda la imagen como un bloque grande.
    2. Si ese bloque tiene mucha diferencia de colores (varianza alta),
       lo partimos en 4 cuadrantes.
    3. Repetimos el proceso para cada bloque nuevo.
    4. Cuando los bloques son chicos o tienen colores parecidos,
       los pintamos con su color promedio.

    Parámetros:
      - umbral_varianza: controla cuánta diferencia de color hace falta para subdividir.
                         (más chico = más detalle, más grande = menos subdivisiones)
      - tamano_minimo: evita bloques demasiado pequeños.
      - max_niveles: limita cuántas veces se puede subdividir.
      - con_bordes: True para dibujar bordes negros entre los bloques.
    """

    # Guardamos el alto y ancho de la imagen original
    alto, ancho = imagen.shape[:2]

    # Creamos una imagen vacía del mismo tamaño donde pondremos el resultado
    salida = np.zeros_like(imagen)

    # Guardamos los bloques finales para dibujar los bordes después
    bloques_finales = []

    # Creamos una lista (pila) con un solo bloque inicial: toda la imagen
    # Cada bloque está representado como: (fila_inicial, fila_final, col_inicial, col_final, nivel)
    pila = [(0, alto, 0, ancho, 0)]

    # Mientras haya bloques en la pila...
    while pila:
        # Sacamos el último bloque
        top, bottom, left, right, nivel = pila.pop()

        # Obtenemos solo esa parte de la imagen
        bloque = imagen[top:bottom, left:right]

        # Guardamos su altura y ancho
        alto_bloque, ancho_bloque = bloque.shape[:2]

        # Calculamos varianza y color promedio del bloque
        varianza, color_promedio = calcular_estadisticas_bloque(bloque)

        # Decidimos si vale la pena subdividir el bloque o dejarlo así
        if (varianza > umbral_varianza and   # hay mucha diferencia de color
            alto_bloque > tamano_minimo and  # el bloque no es demasiado chico
            ancho_bloque > tamano_minimo and
            nivel < max_niveles): # y todavía no llegamos al límite de subdivisión

            # Calculamos el punto medio del bloque
            mitad_y = (top + bottom) // 2
            mitad_x = (left + right) // 2

            # Agregamos los 4 sub-bloques a la pila
            # Arriba izquierda
            pila.append((top, mitad_y, left, mitad_x, nivel + 1))
            # Arriba derecha
            pila.append((top, mitad_y, mitad_x, right, nivel + 1))
            # Abajo izquierda
            pila.append((mitad_y, bottom, left, mitad_x, nivel + 1))
            # Abajo derecha
            pila.append((mitad_y, bottom, mitad_x, right, nivel + 1))

        else:
            # Si el bloque no necesita subdividirse, lo pintamos con su color promedio
            salida[top:bottom, left:right] = np.clip(color_promedio, 0, 255).astype(np.uint8)
            bloques_finales.append((top, bottom, left, right))  # Lo guardamos para los bordes

    # Dibujamos los bordes si el usuario dijo que si 
    if con_bordes:
        for top, bottom, left, right in bloques_finales:
            dibujar_borde_negro(salida, top, bottom, left, right)

    # Retornamos la imagen procesada
    return salida

#funcion principal:
def main():
    
    imagen= open_image(ruta_imagen) # abre la imagen y la convierte a RGB

    if metodo=="vitral": # si el metodo es vitral se ejecuta el if 
        resultado = aplicar_vitral(imagen, n, metrica)  

   
        Image.fromarray(resultado).save(ruta_guardar_imagen) #guarda la imagen
        print("Vitral guardado en:", ruta_guardar_imagen)

        Image.open(ruta_guardar_imagen).show() # te abre la foto automaticamente
    elif metodo=="mosaico":
        # normalizo tipos
        vth = float(variance_threshold)
        mins = int(min_size)
        passes = int(max_passes)

        # interpretar si/no de bordes
        dibujar = str(bordes_bloques).strip().lower()
        dibujar = (dibujar in ("si", "sí", "s", "y", "yes", "true", "1"))

        resultado = mosaico_adaptativo_simple(
            imagen,
            variance_threshold=vth,
            min_size=mins,
            max_passes=passes,
            dibujar_bordes=dibujar
        )

        Image.fromarray(resultado).save(ruta_guardar_imagen)
        print("Mosaico guardado en:", ruta_guardar_imagen)
        Image.open(ruta_guardar_imagen).show()


if __name__=="__main__":
    main()

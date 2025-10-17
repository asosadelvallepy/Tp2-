import numpy as np
from PIL import Image




#inputs del programa

ruta_imagen= input("Ingrese la ruta de la imagen:")
metodo= input("Seleccione el metodo:").lower()

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





#funcion principal:
def main():
    
    imagen= open_image(ruta_imagen) # abre la imagen y la convierte a RGB

    if metodo=="vitral": # si el metodo es vitral se ejecuta el if 
        resultado = aplicar_vitral(imagen, n, metrica)  

   
        Image.fromarray(resultado).save(ruta_guardar_imagen) #guarda la imagen
        print("Vitral guardado en:", ruta_guardar_imagen)

        Image.open(ruta_guardar_imagen).show() # te abre la foto automaticamente

if __name__=="__main__":
    main()



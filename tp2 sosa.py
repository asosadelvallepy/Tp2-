import numpy as np
from PIL import Image




#inputs del programa

ruta_imagen= input("Ingrese la ruta de la imagen:")
metodo= input("Seleccione el metodo:").lower()

if metodo=="vitral":

    n= input("Ingrese la cantidad de puntos:")

    if n=="":
        n=1000
    else:
        n=int(n)
        if n<0:
            print("La cantidad de puntos debe ser mayor a 0")

    metrica=input("Ingrese la metrica de distancia (euclidean/manhattan):").lower()
    if metrica!= "euclidean" and metrica!= "manhattan":
        print("La metrica seleccionada no esta dentro de las opciones por default es euclidean")
        metrica="euclidean"
    

    ruta_guardar_imagen= input("Seleccione la ruta para guardar imagen procesada:")

elif metodo=="mosaico":
    
    variance_threshold=input( "Ingrese el umbral de varianza (default=150):")
    
    if variance_threshold=="":
        variance_threshold=150
    else:
        variance_threshold=int(variance_threshold)
        if variance_threshold<0:
            print("El umbral de varianza debe ser mayor a 0")

    min_size=input("Ingrese el tamaño mínimo de bloque (default=20):")
    
    if min_size=="":
        min_size=20
    else:
        min_size=int(min_size)
        if int(min_size<0):
            print("EL tamaño minimo de bloque debe ser un numero positivo")

    max_passes= input("Ingrese el número máximo de subdivisiones (default=10):")
    if max_passes=="":
        max_passes=10
    else:
        max_passes=int(max_passes)
        if max_passes<0:
            print("El numero maximo de subdivisiones debe ser un numero positivo")


    bordes_bloques= input("¿Dibujar bordes en los bloques? (si/no):")
    ruta_guardar_imagen= input("Seleccione la ruta para guardar la imagen procesada:")

else:
    print("El metodo seleccionado no esta entre las opciones")


def open_image(path:str):
    img= Image.open(path).convert("RGB")
    return np.array(img)



def puntos(imagen,n,seed):
    """
    Devuelve (n, 2) con coordenadas (y, x) de n puntos aleatorios dentro de la imagen.
    """

    
    random=np.random.default_rng(seed)
    
        
    alto,ancho,_= imagen.shape 

    ys= random.integers(0,alto,n)
    xs=random.integers(0,ancho,n)
    matriz= np.stack([ys,xs],1)
    return matriz

    
def calc_dist(gy,gx,sy,sx,metrica):

    """
    Distancia desde todos los píxeles (gy,gx) a un punto (sy,sx). Retorna (alto, ancho).
    """
    
    if metrica=="manhattan":
        return np.abs(gy-sy)+np.abs(gx-sx)
    elif metrica=="euclidean":
        return (gy-sy)**2 + (gx-sx)**2

def cercanas(alto,ancho,sitios,metrica):
    """
    Para cada píxel, asigna el índice del sitio más cercano. Retorna labels (h, w)
    """
    gy=np.arange(alto)[:, None]
    gx=np.arange(ancho)[None, :]

    menor_dist=None 
    punto_cerc= None

    for i, (sy,sx) in enumerate(sitios):
        dist=calc_dist(gy,gx,sy,sx,metrica)
        if menor_dist is None:
            menor_dist= dist
            punto_cerc= np.full_like(dist,i)
        else:
            matriz_chequeo= dist<menor_dist
            menor_dist[matriz_chequeo]= dist[matriz_chequeo]
            punto_cerc[matriz_chequeo]=i

    return punto_cerc  # retorna (alto,ancho) que es el indice del punto mas cercano

def colorear_por_promedio(img: np.ndarray, labels: np.ndarray, n: int) -> np.ndarray:
    """
    Calcula el color promedio de cada celda y pinta toda la celda con ese color.
    """
    flat_labels = labels.ravel()                   # (h*w,)
    pixels = img.reshape(-1, 3).astype(np.float64) # (h*w, 3)

    sums_r = np.bincount(flat_labels, weights=pixels[:, 0], minlength=n)
    sums_g = np.bincount(flat_labels, weights=pixels[:, 1], minlength=n)
    sums_b = np.bincount(flat_labels, weights=pixels[:, 2], minlength=n)
    counts = np.bincount(flat_labels, minlength=n).astype(np.float64)
    counts[counts == 0] = 1.0  # evita división por cero si alguna celda quedó vacía

    means = np.stack([sums_r/counts, sums_g/counts, sums_b/counts], axis=1)  # (n, 3)
    out = means[labels]  # (h, w, 3)
    return np.clip(out, 0, 255).astype(np.uint8)

def aplicar_vitral(img: np.ndarray, n: int, metrica: str, seed: int | None = None) -> np.ndarray:
    """
    maneja el vitral: puntos → asignación → coloreo.
    """
    alto, ancho, _ = img.shape
    sites = puntos(img, n, seed=seed)
    labels = cercanas(alto, ancho, sites, metrica)
    return colorear_por_promedio(img, labels, n)






def main():
    
    imagen= open_image(ruta_imagen)

    if metodo=="vitral":
        resultado = aplicar_vitral(imagen, n, metrica)  

   
        Image.fromarray(resultado).save(ruta_guardar_imagen)
        print("Vitral guardado en:", ruta_guardar_imagen)

        Image.fromarray(resultado).save(ruta_guardar_imagen)
        print("Vitral guardado en:", ruta_guardar_imagen)
        Image.open(ruta_guardar_imagen).show()

if __name__=="__main__":
    main()


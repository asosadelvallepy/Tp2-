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
        print("La metrica seleccionada no esta dentro de las opciones")
    elif metrica=="":
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


    if seed is not None:
        random=np.random.default_rng(seed)
    else:
        random= np.random.default_rng()

        alto,ancho,rgb= imagen

        ys= random.integers(0,alto,n)
        xs=random.integers(ancho,0,n)
        matriz= np.stack([ys,xs],1)
        return matriz

    gy=np.arrange(alto)[:, None]
    gx=np.arrange(ancho)[None, :]
    
def calc_dist(gy,gx,ys,xs,metrica):
    
    if metrica=="manhattan":
        return np.abs(gy-ys)+np.abs(gx-xs)
    elif metrica=="euclidean":
        return (gy-ys)**2 + (gx-xs)**2

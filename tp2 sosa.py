import numpy




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

if metodo=="mosaico":
    
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



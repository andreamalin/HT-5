#Se mandan a llamar las liberias a utilizar
from simpy import * 
from random import *
from statistics import *

CPU_lim_instr = 0 #Cantidad de instrucciones que procesa el CPU
actual_mem = 0 #Espacio variable para la memoria del proceso actual
actual_instr = 0 #Espacio variable para la cantidad de instrucciones
inicial_mem = 0 #Espacio variable para la memoria a utilizar
RANDOM_SEED = 10 

statistics_data = [] #Datos a realizar resumen de datos
inicial_data = [] #Tiempos iniciales
final_data = [] #Tiempos finales



#Primera funcion, genera los procesos
def principal(env, req_process):
    for i in range(req_process): #Se realiza n veces
        i += 1
        yield env.process(new(env, "Proceso %d"%i))
        
        
#Segunda funcion, recibe el proceso
def new(env, name_process):
    global actual_mem
    global inicial_mem
    global actual_instr
    global RANDOM_SEED
    
    seed(RANDOM_SEED)
    
    actual_mem = randint(1, 10) #Cantidad de memoria a utilizar
    inicial_mem = actual_mem

    
    while actual_mem > RAM.level: #Mientras no quepa, genera mas tiempo de espera
        time = expovariate(1.0/10.0) #Tiempo de espera
        yield env.timeout(time)
        
    if actual_mem <= RAM.level:
        time = expovariate(1.0/10.0) #Tiempo de espera
        
        yield env.timeout(time)
        inicial_data.append(env.now) #Se guardan los tiempos de llegada
        
        print ("---> %s llega a la RAM en tiempo %.2f" % (name_process, env.now))
        RAM.get(actual_mem) #Se obtiene la memoria
        actual_instr = randint(1, 10) #Cantidad de instrucciones a realizar
        env.process(ready(env, name_process)) #Se comienza el estado de ready
            
            
#Tercera funcion, el CPU atiende      
def ready(env, name_process):
    global actual_instr
    
    with CPU.request() as req: #Se revisa si el CPU esta desocupado
        yield req #El CPU atiende
        print ("==> El CPU acepta el %s con %s instrucciones" % (name_process, actual_instr))
        
        env.process(running(env, name_process))
    
        
        
#Cuarta funcion, el CPU corre instrucciones
def running(env, name_process):
    global actual_instr
    global CPU_lim_instr 
    
    for i in range(0, CPU_lim_instr):    
        actual_instr -= 1 #Se resta un proceso
    
    yield env.timeout(1) #Rapidez CPU = CPU_lim_instr procesadas en 1 tiempo
    
    if actual_instr < CPU_lim_instr: #Si hay menos de n instrucciones
        print ("<== EL CPU se libera del %s en tiempo %.2f" %(name_process, env.now))
        actual_instr = 0 #Se define que el proceso ya no tiene instrucciones
        env.process(terminated(env, name_process)) #Se termina el proceso
    else:
        yield env.process(waiting(env, name_process)) #Se manda a I/O


#Se usa al salir del CPU
def terminated(env, name_process):
    global inicial_mem
    global final_data
    global req_process
    
    RAM.put(inicial_mem) #Se devuelve la memoria pedida
    yield env.timeout(0) #Se tarda 0 seg en salir del sistema
    
    final_data.append(env.now)
    print("<--- El %s ha salido del sistema en el tiempo %.2f" %(name_process, env.now))

#Se usa al salir del CPU
def waiting(env, name_process):
    global RANDOM_SEED
    
    seed(RANDOM_SEED)
    input_output = randint(1, 2)
    
    while input_output == 1: #Si es 1 pasa a hacer cola
        print("!! El %s esta en cola" % (name_process))
        yield env.timeout(1) #Pasa 1 segundo para vez que este en cola
        input_output = randint(1, 2)
    
    print("!! El %s sale de procesos I/O" % (name_process))
    env.process(ready(env, name_process)) #Se regresa al estado ready en el CPU
    
#PARA DATOS
def statistics():
    global req_process
    global final_data
    
    for i in range(req_process): #Por cada proceso
        inicial_time = inicial_data[i] #Se recibe su tiempo de llegada
        final_time = final_data[i] #Se recibe su tiempo de salido
        res = final_time - inicial_time #Se obtiene el tiempo real del proceso
        statistics_data.append(final_time) #Se agrega a la base de estadisticas
        
        print("Proceso %d\n | Tiempo inicial %.2f | Tiempo final %.2f | Tiempo total del proceso %.2f" %(i+1, inicial_time, final_time, res))


#SE COMIENZA LA SIMULACION
print("_________________________________________\n        BIENVENIDO A LA SIMULACION\n_________________________________________\n")
req_process = int(input('Ingrese la cantidad de procesos a realizar: '))
CPU_lim_instr = int(input('Ingrese la cantidad de instrucciones que procesa el CPU en 1 unidad de tiempo: '))
env = Environment() #Se define el environment
CPU = Resource(env, capacity=1) #Se define el CPU
RAM = Container(env, init=100, capacity=100) #Capacidad de la memoria de la RAM
env.process(principal(env, req_process)) #Se manda a generar procesos
env.run()  #Comienza la simulacion

#SE MUESTRAN LAS ESTADISTICAS
print("__________________________________________________________________________________\n                                 DATOS OBTENIDOS\n__________________________________________________________________________________\n")
statistics()
print("_____________________________________RESUMEN______________________________________\n")
print("Cantidad de procesos %d"  %req_process)
print("CPU con velocidad 1 para %d instrucciones"  %CPU_lim_instr)
print("Tiempo promedio por proceso %.2f"  %mean(statistics_data))
print("Desviacion estandar por proceso %.2f"  %stdev(statistics_data))
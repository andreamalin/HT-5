#Se mandan a llamar las liberias a utilziar
from simpy import * 
from random import *
from statistics import *

CPU_lim_instr = 0 #Cantidad de instrucciones que procesa el CPU
CPU_speed = 0 #CPU_lim_instr procesadas en n tiempo
actual_mem = 0 #Espacio variable para el proceso actual
actual_instr = 0 #Espacio variable para la cantidad de instrucciones
inicial_mem = 0 #Espacio variable para la memoria a utilizar

inicial_time = 0.0
finish_time = 0.0
total_time = 0.0 #Espacio para obtener el tiempo total
desvest_data = []



#Primera función, genera los procesos
def principal(env, req_process):
    for i in range(req_process): #Se realiza n veces
        i += 1
        yield env.process(new(env, "Proceso %d"%i))
        
        
#Segunda función, recibe el proceso
def new(env, name_process):
    global actual_instr
    global actual_mem
    global inicial_mem
    global inicial_time
    
    time = expovariate(1.0/10.0) #Tiempo de llegada
    inicial_time+=time
    yield env.timeout(time)
    
    print ("---> %s llega a la RAM en tiempo %.2f" % (name_process, env.now))
    
    with RAM.request() as req:  #revisamos la memoria
        yield req # Obtiene memoria
        
        actual_mem = randint(1, 10) #Cantidad de memoria a utilizar
        inicial_mem = actual_mem
     
        if actual_instr <= cap_RAM.level: #Se revisa que la memoria pedida quepa en la memoria actual
            cap_RAM.get(inicial_mem) #Se obtiene la memoria
            env.process(ready(env, name_process)) #Se comienza el estado de ready        
            
#Tercera función, el CPU atiende      
def ready(env, name_process):
    global actual_instr
    
    with CPU.request() as req: #Se revisa si el CPU está desocupado
        yield req #El CPU atiende
        actual_instr = randint(1, 10) #Cantidad de instrucciones a realizar
        print ("==> El CPU acepta el %s con %s instrucciones" % (name_process, actual_instr))
        
        env.process(running(env, name_process))
    
        
        
#Cuarta función, el CPU corre instrucciones
def running(env, name_process):
    global actual_instr
    
    for i in range(0, CPU_lim_instr):    
        actual_instr -= 1 #Se resta un proceso
    
    yield env.timeout(CPU_speed)
    
    
    if actual_instr < CPU_lim_instr: #Si hay menos de n instrucciones
        print ("<== EL CPU se libera del %s en tiempo %.2f" %(name_process, env.now))
        actual_instr = 0 #Se define que el proceso ya no tiene instrucciones
        env.process(terminated(env, name_process)) #Se termina el proceso
    else:
        yield env.process(waiting(env, name_process)) #Se manda a I/O

#Se usa al salir del CPU
def terminated(env, name_process):
    global inicial_mem
    global inicial_time
    global total_time
    global finish_time
    
    #SALIR DEL SISTEMA
    cap_RAM.put(inicial_mem) #Se coloca la memoria pedida
    total_time += env.now
    finish_time += env.now
    
    actual_time = finish_time - inicial_time
    print(actual_time)
    desvest_data.append(actual_time)
    yield env.timeout(1) #Se tarda 1 seg en salir del sistema
    print("<--- El %s ha salido del sistema en el tiempo %.2f" %(name_process, env.now))

 
 
#Se usa al salir del CPU
def waiting(env, name_process):
    input_output = randint(1, 2)
    
    while input_output == 1: #Si es 1 pasa a hacer cola
        print("!! El %s esta en cola" % (name_process))
        yield env.timeout(1) #Pasa 1 segundo para vez que esté en cola
        input_output = randint(1, 2)
    
    print("!! El %s sale de procesos I/O" % (name_process))
    env.process(ready(env, name_process)) #Se regresa al estado ready en el CPU
    



#SE COMIENZA LA SIMULACION
print("_________________________________________\n        BIENVENIDO A LA SIMULACION\n_________________________________________\n")
req_process = int(input('Ingrese la cantidad de procesos a realizar: '))
CPU_speed = int(input('Ingrese la velocidad de instrucciones del CPU: '))
CPU_lim_instr = int(input('Ingrese la cantidad de instrucciones que procesa el CPU en ese tiempo dado: '))

env = Environment() #Se define el environment
CPU = Resource(env, capacity=1) #Se define el CPU
RAM = Resource(env, capacity=1) #Se define la RAM
cap_RAM = Container(env, init=100, capacity=100) #Capacidad de la memoria de la RAM
env.process(principal(env, req_process)) #Se manda a generar procesos
env.run()  #Comienza la simulacion

#SE MUESTRAN LAS ESTADISTICAS
print("_________________________________________\n        DATOS OBTENIDOS\n_________________________________________\n")
print("Cantidad de procesos %d"  %req_process)
print("CPU con velocidad %d para %d instrucciones"  %(CPU_speed, CPU_lim_instr))
print("Tiempo promedio %.2f" %(total_time/req_process))
print("Desviacion estandar %.2f"  %pstdev(desvest_data))
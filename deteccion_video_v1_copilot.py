##El vector se calcula en el frame posterior mostrado
import cv2
import numpy as np
import time
import math
import imutils

class Objeto(object):
  """
  Esta clase es para definir un objeto reconocido.
  """
  
  def __init__(self, id):
    self.id = id
    self.init_x = 0
    self.init_y = 0

    self.finish_x = 0
    self.finish_y = 0

    self.distancia = 0
    self.velocidad = 0
    self.init_time = 0
    self.finish_time = 0
    self.acumulador_velocidad = 0
    self.acumulador_modulo = 0
    self.cont = 1
    self.cont_velocidad = 0
  
  def __str__(self):
    return self.id

  def modificar_posicion(self, x, y, tiempo):
    if self.cont % 2 == 0:
      #print("Es Par")
      self.init_x = self.finish_x
      self.init_y = self.finish_y
      self.init_time = self.finish_time
      self.finish_time = tiempo
      self.finish_x = x
      self.finish_y = y


    elif self.cont % 2 != 0:
      #print("Es ImPar")
      self.init_y = self.finish_y
      self.init_x = self.finish_x
      self.init_time = self.finish_time
      self.finish_time = tiempo
      self.finish_x = x
      self.finish_y = y
    #print("Cont:",self.cont)
    self.cont += 1
    self.cont_velocidad += 1
    self.acumula_velocidad ()
    self.acumula_modulo ()
      
      

  def calcular_modulo(self): #Modulo no es vector, el vector es la distancia del punto inicial al fianal
    self.distancia =cv2.sqrt(cv2.pow(self.init_x-self.finish_x,2)+cv2.pow(self.init_y-self.finish_y,2))[0,0]
    return round(self.distancia,3)

  def acumula_modulo(self):
    self.acumulador_modulo += self.distancia
    return self.acumulador_modulo

  def calcular_tiempo(self):
    tiempo = self.finish_time + self.init_time
    return tiempo  

  def calcular_velocidad(self): #rapidez
    self.velocidad = self.distancia/self.calcular_tiempo()
    self.cont_velocidad += 1
    #print("CONTADOR VELOCIDAD: ", self.cont_velocidad)
    #self.acumulador_velocidad += self.velocidad
    return round(self.velocidad,3)

  def get_velocidad(self):
    return round(self.velocidad,3)
  
  def acumula_velocidad(self):
    self.acumulador_velocidad += self.velocidad
    return self.acumulador_velocidad











class ControladorObjetos(object):
  """
  Esta clase controla los objetos reconocidos por la camara.
  """
  def __init__(self):
    self.lista = []


  def existe_obj(self, id):
    #print("LISTA",self.lista)
    for l in self.lista:
      if l.id == id:
        return True
    return False

  def crear_objeto(self, id, init_x, init_y, tiempo):
    if self.existe_obj(id):
      return 0
    
    obj = Objeto(id)
    obj.finish_x = init_x
    obj.finish_y = init_y
    obj.finish_time = tiempo
    self.lista.append(obj)
    #obj.acumula_velocidad()
    #obj.acumula_modulo()
    return 1
  
  def get_posicion_init_x(self, id):
    if self.existe_obj(id):
      obj = self.encontrar_objeto(id)
      return (obj.init_x, obj.init_y, obj.cont, obj.id)
    return 0
  
  def get_posicion_finish_x(self, id):
    if self.existe_obj(id):
      obj = self.encontrar_objeto(id)
      return (obj.finish_x, obj.finish_y, obj.cont, obj.id)
    return 0

  
  def modificar_posicion_ctr(self, id, x, y, tiempo):
    if self.existe_obj(id):
      obj = self.encontrar_objeto(id)
      obj.modificar_posicion(x, y, tiempo)
      #self.lista.append(obj)
      return 1
    return 0

  
  def get_velocidad_objeto(self, id):
    if self.existe_obj(id):
      obj = self.encontrar_objeto(id)
      obj.calcular_modulo()

      return round(obj.calcular_velocidad(),3)
      
    return 0
  


  def get_distancia_puntos(self, id):
    if self.existe_obj(id):
      obj = self.encontrar_objeto(id)
      return round(obj.calcular_modulo(),3)
    
    return 0


  ####PROBAR
  def get_tiempo_objeto(self, id):
    if self.existe_obj(id):
      obj = self.encontrar_objeto(id)
      return round(obj.calcular_tiempo(),3)
    
    return 0

  def get_distancia_total(self, id):
    if self.existe_obj(id):
      obj = self.encontrar_objeto(id)
      #print("acumulador_modulo", obj.acumulador_modulo)
      return round(obj.acumulador_modulo,3)
    
    return 0

  def get_velocidad_promedio(self, id):
    if self.existe_obj(id):
      obj = self.encontrar_objeto(id)

      return round(obj.acumulador_velocidad/obj.cont_velocidad,3)
    
    return 0



  def encontrar_objeto(self, id):
    for l in self.lista:
      if l.id == id:
        return l
  
  def guardar_datos(self, id, file):
    if self.existe_obj(id):
      obj = self.encontrar_objeto(id)
      #file.write("#Pelota         #X      #Y "+"\n")
      file.write("#{}    {}     {}    {}    {}    {}    {}    {} ".format(id, obj.init_x, obj.init_y, obj.finish_x, obj.finish_y, obj.calcular_modulo(), obj.get_velocidad(), obj.calcular_tiempo())+"\n")
      #file.close()
      return 1   
    return 0





class Reconocimiento(object):
     
  def __init__(self, media):
    self.image = cv2.VideoCapture(media) #Leo video
    """(major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')
 
    if int(major_ver)  < 3 :
        fps = self.image.get(cv2.CV_CAP_PROP_FPS)
        print("Frames per second using video.get(cv2.cv.CV_CAP_PROP_FPS): {0}".format(fps))
    else :
        fps = self.image.get(cv2.CAP_PROP_FPS)
        print("Frames per second using video.get(cv2.CAP_PROP_FPS) : {0}".format(fps))"""

    self.controller = ControladorObjetos()


  def dibujar(self): #por si hay que detectar más colores
    """
        Esta funcion dibuja los contornos y el HSV.
    """
    
    font = cv2.FONT_HERSHEY_SIMPLEX #Fuente a utilizar   
    #Rango de colores en HSV MIN Y MAX
    green_bajo = np.array([24,50,50],np.uint8) 
    green_alto= np.array([75,255,255],np.uint8)

    #Sustracción de fondo
    fgbg = cv2.createBackgroundSubtractorMOG2()
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
    ball_cont = 0
    
    frames = {}
    valores = {}
    
    x_list = []
    y_list = []
    f = 0
    t_frame = 0.033
    t_acumulado = 0
    file = open("datos2.txt", "w")
    file.write("#ID          #X_init    #Y_init  #X_finish  #Y_finish    #Desplazamiento   #Rapidez    #Tiempo "+"\n")
    #prev_frame_time = 0
    #new_frame_time = 0
    while True:
      #t_frame += 0.033 #Cambiar, ya que calculo tiempo acumulado
      #t_acumulado += 0.033 #tiempo video
      ret, frame = self.image.read()
      
      n_frame = 'Frame:' + str(f+1)
      i=0

      


      if ret==True: 
        blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        frame_hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        mask_green = cv2.inRange(frame_hsv, green_bajo, green_alto)
        mask_green = cv2.erode(mask_green, None, iterations=2)
        mask_green = cv2.dilate(mask_green, None, iterations=2)
        #contornos,_=cv2.findContours(mask_green, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        contornos = cv2.findContours(mask_green.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        i=0
        contador=0

        area_pts=np.array([[10, 600], [frame.shape[1]-10, 600], [frame.shape[1]-10, 100], [10, 100]])

        # Con una imagen auxiliar, determino el area sobre el cual actuar el detector de movimiento

        imAux= np.zeros(shape=(frame.shape[:2]), dtype=np.uint8)
        imAux = cv2.drawContours(imAux, [area_pts], -1, (255), -1)
        image_area = cv2.bitwise_and(frame, frame, mask=imAux)

        #Aplicar sustracción de fondo
        fgmask = fgbg.apply(image_area)
        fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel)
        fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_CLOSE, kernel)
        fgmask = cv2.dilate(fgmask, None, iterations=5)
        #cnts = cv2.findContours(fgmask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]

        #cv2.drawContours(frame, [area_pts], -1, (255, 0, 255), 2)
        #cv2.line(frame, (1200,600),(1200,100), (0, 255, 255), 1)

        #diccionario
        """new_frame_time = time.time() 
        fps = 1/(new_frame_time-prev_frame_time) 
        prev_frame_time = new_frame_time
 
        fps = int(fps)
        fps = str(fps) 
        cv2.putText(frame, fps,(7, 70), font, 3,(100, 255, 0), 3, cv2.LINE_AA)"""
        for c in contornos:
          area=cv2.contourArea(c)
          #perimetro = cv2.arcLength(c, True)
          #Las pelotas tienen sobre 20k el area, hay un rango de error de 1cm de diametro, es decir, 0,5 por radio
          '''Agregar filtro kalman al codigo'''


          if area > 20000:#Pixeles
            #M2=cv2.moments(area)
            #print (" AREA M00:",M2["m00"] )
            #tim1= time.time()
            nuevoContorno = cv2.convexHull(c)
            area_convexa=cv2.contourArea(nuevoContorno)
            perimetro=round(cv2.arcLength(nuevoContorno, True),3)
            #cv2.drawContours(self.image, [nuevoContorno], 0, (0,0,0), 2) #Contorno circular
            rx,ry,w,h = cv2.boundingRect(nuevoContorno)
            #if 1199 < (rx+w) > 1201:# < 901:>
             # ball_cont += 1
             # cv2.line(frame,(1200,600),(1200,100), (0, 255, 0), 3)
            #x1,y1,w1,h1 = cv2.boundingRect(c)
            #cv2.rectangle(frame,(x1,y1),(x1+w1,y1+h1),(0,255,255),1)
            M=cv2.moments(nuevoContorno)
            if (M["m00"]==0): M["m00"]=1 #Para evitar que la división sea infinita
            x=int(M["m10"]/M["m00"]) #para calcular centroide
            y=int(M["m01"]/M["m00"])
            #print (" CONVEX M00:",M["m00"] )
            x_cm = round(x*0.043,3) #Convierto a centimetros
            y_cm = round(y*0.043,3) #Convierto a centimetros
            cv2.circle(frame,(x,y), 3, (255,0,0),-1) #Para marcar el centro
            mensaje= 'Pelota:' + str(i+1) #+" Frame: "+str(f)
            
            id = 'Pelota:' + str(i+1)
            #print ('numero de contornos', len(contornos))
            #Identificador texto, coordenadas centro
            cv2.putText(frame, 'X:{},Y:{}'.format(x,y),(x-50,y+30), font, 0.55,(255,0,0),1 ,cv2.LINE_AA)
            #Identificación de texto para las pelotas
            cv2.putText(frame, mensaje ,(x-20,y-100), font, 0.55,(255,0,0),1 ,cv2.LINE_AA) #


            cv2.rectangle(frame,(rx,ry),(rx+w,ry+h),(0,255,0),3) #Rectangulo
            #self.controller.modificar_posicion_inicial(id, x, y)
            #Crear objeto si no existe la id
            
           
            self.controller.crear_objeto(id, x_cm, y_cm, t_frame)
            #print("largo menos 1:",len(self.controller.lista)-1-i)
            #print("I",i)
            #print("ID1",id)
            #id="Pelota:" + str(len(self.controller.lista)-1-i)

            self.controller.modificar_posicion_ctr(id, x_cm, y_cm, t_frame)
            print("ID: {}".format(id))
            print("Init X,Y:{}".format(self.controller.get_posicion_init_x(id)))
            print("Finish X,Y:{}".format(self.controller.get_posicion_finish_x(id)))
            

            print("Distancia:",self.controller.get_distancia_puntos(id),"cm") 
            print("Distancia total:",self.controller.get_distancia_total(id),"cm")


            print("Velocidad:",self.controller.get_velocidad_objeto(id),"cm/s")
            #print("Velocidad promedio:", self.controller.get_velocidad_promedio_de_todos_los_objetos(id),"cm/s")
            print("Velocidad Promedio:",self.controller.get_velocidad_promedio(id),"cm/s")
            
            
            print("Tiempo:",self.controller.get_tiempo_objeto(id),"s")
            print("################################################################")
            
            #Guarda los datos en el archivo de texto plano
            self.controller.guardar_datos(id, file)

            #Mostrar velocidad por pelota
            cv2.putText(frame, 'Velocidad: {}'.format(self.controller.get_velocidad_objeto(id)),(x-60,y+90), font, 0.55,(255,0,0),1 ,cv2.LINE_AA)
            cv2.putText(frame, 'Perimetro: {}'.format(perimetro),(x-60,y+140), font, 0.55,(255,0,0),1 ,cv2.LINE_AA)
            cv2.putText(frame, 'Area: {}'.format(area_convexa),(x-60,y+180), font, 0.55,(255,0,0),1 ,cv2.LINE_AA)
   
            #print("Velocidad:",self.controller.get_velocidad_objeto(id, t_frame),"cm/s")
            i = i+1
            valores[mensaje] = [x,y] #Valores a retonar
            frames[n_frame] = valores
        #cv2.imshow('maskGreen', mask_green)
        #cv2.rectangle(frame, (frame.shape[1]-70,215),(frame.shape[1]-5,270),(0,255,0),2)
        #cv2.putText(frame, str(ball_cont),(frame.shape[1]-60,240), font, 1.2,(0,255,0),2 ,cv2.LINE_AA)
        cv2.imshow("image", frame)
        #cv2.imshow("fgmask", fgmask)
        #print(self.controller.lista)
        f += 1
      if cv2.waitKey(30) & 0xFF == ord('s'):
        break
    self.image.release()
    file.close()
    #print(valores)
    
    return frames
    
  ##def recuperar_datos(self, resultados):
  #  file = open("test.out", "w")
  #  file.write("#Pelota         #X      #Y "+"\n")
   # for resultado in resultados:
    #    print(resultado)
     #   file.write("#{}    {}     {} ".format(resultado, resultados[resultado][0], resultados[resultado][1])+"\n")
    #file.close() 

  def execute(self):
    resultados = self.dibujar()
    #print(resultados)
    #self.recuperar_datos(resultados) 
    cv2.waitKey(0)
    cv2.destroyAllWindows()
        

def main():
  #media = '/media/pi/C6A433E7A433D89F/tenis.mp4'
  #media = '/media/pi/C6A433E7A433D89F/Videos lab hidraulica/720p30.3fps/1pelotainicio.mp4'
  #media = 0 #Pi Camera
  media = '/media/pi/C6A433E7A433D89F/Videos lab hidraulica/720p30.3fps/7/3pelotaslinea.mp4'
  #media = '/media/pi/C6A433E7A433D89F/Videos lab hidraulica/720p30.3fps/6/3pelotasverticaldelay.mp4'
  uc = Reconocimiento(media)
  uc.execute()

if __name__ == "__main__":
    main()


## Sacar promedios de Velocidad y distancia
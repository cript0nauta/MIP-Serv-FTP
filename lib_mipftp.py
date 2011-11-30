#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Libreria con la clase general y algunas funciones del servidor FTP de MIP-Serv
#by sh4r3m4n
#Esta aplicacion se encuentra bajo licensia Creative Commons, visible en
#http://creativecommons.org/licenses/by/2.5/ar/

#Importa las librerías del sistema necesarias
import os,random,socket,threading,re

#Define la clase del servidor
class servidor:
  """La clase del servidor"""
  def __init__(self,conf,class_cliente):
    """Para iniciarme pasarme como parámetro un array de configuración"""
    self.conf=conf
    self.site=conf['site'] #Diccionario con los comandos SITE. Fijarse ejemplo en server.py
    self.detener=False #Cuando es True detiene los hilos
    
    #Crea el socket principal
    try:
      self.h_socket=socket.socket()
      self.h_socket.bind((self.conf['ip'],self.conf['puerto']))
      self.h_socket.listen(self.conf['max_cons'])
      self.escuchar(self.conf['ip'],self.conf['puerto'])
    except socket.error:
      self.error_bindeando()
      exit()
      
    if((self.conf['run_user'] != False) and os.getuid()==0):
      #Si se define usuario a correr el programa y se está corriendo como root
      import pwd #Importa la librería para obtener UID y GID del usuario
      usuario=pwd.getpwnam(self.conf['run_user'])
      os.setgid(usuario[3]) #Cambia el identificador de grupo indicado en la configuración, y se evita tener que correr como root
      os.setuid(usuario[2]) #Cambia el identificador de usuario al del usuario indicado en la configuración, y se evita tener que correr como root
    
    #Se pone a escuchar
    clientes=[]
    try:
      while(True):
	sock_cliente=self.h_socket.accept()
	#print 'Nueva conexión de',sock_cliente[1]
	self.nueva_con(sock_cliente[1])
	if(False):
	  ###Eliminado a partir de la versión 1.1 BETA
	  pass
	else:
	  clientes.append(class_cliente(sock_cliente,self))
	#Inicia el hilo del último elemento de clientes
	clientes[-1].start()
    except KeyboardInterrupt:
      self.interrupcion()
      
      #Cierra el socket principal
      self.detener=True
      
      #Espera a que finalizen todos los clientes
      for cliente in clientes:
	#print 'Hilo detenido'
	cliente.join()
	cliente.sock.close()
      
      #print 'Terminaron todos los hilos'
      self.h_socket.close()
      exit()
  
  #Declaración de eventos
  def escuchar(self,ip,puerto):
    """Evento que se produce cuando el servidor principal se pone en escucha"""
    pass
  def nueva_con(self,datos):
    """Evento que se produce cuando se acepta una nueva conexion de un cliente"""
    pass
  def error_bindeando(self):
    """Evento que se produce al producirse un error intentando escuchar conexiones"""
    pass
  def interrupcion(self):
    """Evento que se produce cuando hay una interrupción"""
    pass

#Define el hilo controlador del cliente
class cliente(threading.Thread):
  """Clase hilo que es un manejador individual del sock de cada cliente"""
  def __init__(self,sock,h_servidor):
    """La función de inicio del manejador de cliente,
       para iniciarme pasarme como parámetro lo que nos devuelve el método accept del socket principal"""
       
    #Se inicia el thread
    threading.Thread.__init__(self)
    self.sock=sock[0]
    self.datos=sock[1]
    self.servidor=h_servidor
    self.logueado=False
    self.user=''
    self.path=''
    self.conf_path=''
    self.acceso_escritura=False
    self.tipo_data_con=0
    self.datos_data_con=('',0)
    self.renombrar=''
    self.seek=0
    #self.start()
  def run(self):
    """Para llamarme use la función start de mi clase"""
    #Envia el banner
    self.sock.send('220 '+self.servidor.conf['errores'][220]+'\n')
    while(True):
      try:	
	#Recibe los datos
	recibido=''
	repetir=True
	
	#Hace que si el socket no recibe datos en los próximos dos segundos cause una excepción
	self.sock.settimeout(1)
	
	while(repetir):
	  if(self.servidor.detener==False):
	    #Si no se quiere salir
	    #print 'Recibiendo...'
	    try:
	      recibido=recibido+self.sock.recv(self.servidor.conf['max_size'])
	    except socket.timeout:
	      #Si pasó un segundo sin recibir nada se produce una excepción, la ignoro y comienzo el bucle otra vez
	      #print 'TimeOut'
	      pass
	    if(recibido.find('\n') != -1):
	      #Si se encuentra el caracter de nueva línea en lo que se recibe del socket remoto
	      repetir=False
	  else:
	    self.logout(self.user,self.datos)
	    self.sock.close()
	    break
	
	#Separa los comandos en un array y borra recibido, para mas memoria
	comandos=re.split('\r?\n',recibido)
	del(recibido)
	#print comandos
	
	#Procesar los comandos
	for comando_y_pars in comandos:
	  #Verifica que no este en blanco
	  if(comando_y_pars!=''):
	    #Separar comando y parametros
	    find=comando_y_pars.find(' ')
	    if(find != -1):
	      comando=comando_y_pars[:find]
	      parametros=comando_y_pars[find+1:]
	    else:
	      comando=comando_y_pars
	      parametros=''
	    #Pasa el comando a mayusculas, para que sea Case-Sensitive como indica el RFC
	    comando=comando.upper()
	      
	
	    #Ejecuta el evento
	    self.comando_ejecutado(comando,parametros)
	    
	    #Hacer cada cosa segun el comando
	    if(comando=='USER'):
	      self.logueado=False
	      self.user=parametros
	      mostrar_error(self,331)
	    elif(comando=='PASS'):
	      self.logueado=False
	      """if(self.servidor.conf['login']==(self.user,parametros)):
		self.intento_login(self.user,parametros,True)
		self.logueado=True
		mostrar_error(self,230)
	      else:
		self.intento_login(self.user,parametros,False)
		self.logueado=False
		mostrar_error(self,tienepermisos(self,comando))"""
	      usuarios=self.servidor.conf['usuarios']
	      if(usuarios.has_key(self.user)):
		#Si existe el usuario
		if(usuarios[self.user][0]==parametros or usuarios[self.user][0]==False):
		  #Si la pass es correcta o no se necesita
		  self.intento_login(self.user,parametros,True)
		  self.logueado=True
		  self.path=usuarios[self.user][1]
		  self.conf_path=usuarios[self.user][1]
		  self.acceso_escritura=usuarios[self.user][2]
		  mostrar_error(self,230)
		else:
		  self.logueado=False
		  self.intento_login(self.user,parametros,False)
		  mostrar_error(self,tienepermisos(self,comando))
		  #print 'pass'
	      else:
		self.intento_login(self.user,parametros,False)
		self.logueado=False
		mostrar_error(self,tienepermisos(self,comando))
		#print 'usuario'
	    elif(comando=='NOOP'):
	      if(tienepermisos(self,comando)==True):
		mostrar_error(self,200)
	      else:
		mostrar_error(self,tienepermisos(self,comando))
		
	    elif(comando=='PASV'):
	      if(tienepermisos(self,comando)==True):
		#Crea un puerto aleatorio del rango especificado en la configuracion
		id_puerto=random.randint(0,len(self.servidor.conf['rango_pasv'])-1)
		puerto=self.servidor.conf['rango_pasv'][id_puerto]
		
		#Setea la conexion de datos y llama a su evento
		self.tipo_data_con=1
		self.datos_data_con=(self.servidor.conf['ip'],puerto) #conf[ip] en vez de conf[ip_pasv]
		try:
		  self.h_data_con=socket.socket()
		  self.h_data_con.bind((self.datos_data_con[0],self.datos_data_con[1]))
		  self.h_data_con.listen(1)
		  self.setear_data_con(1,self.servidor.conf['ip_pasv'],puerto)
		  correctamente=True
		except socket.error, error:
		  correctamente=False
		  print error
		  try:
		    h_data.close()
		    h_data_client.close()
		  except:
		    pass
		  self.error_socket(error,self.datos)
		  mostrar_error(self,425)
		
		#Lo envia
		enviar=ip_normal_a_ftp(self.servidor.conf['ip_pasv'])+','+puerto_normal_a_ftp(puerto)
		self.sock.send('227 '+self.servidor.conf['errores'][227]+' ('+enviar+')\n')
	      else:
		mostrar_error(self,tienepermisos(self,comando))
	    elif(comando=='PORT'):
	      if(tienepermisos(self,comando)==True):
		ip=ip_ftp_a_normal(parametros)
		puerto=puerto_ftp_a_normal(parametros)
		if(ip==False or puerto==False):
		  mostrar_error(self,501)
		else:
		  if(self.servidor.conf['permitir_bounce']==True or self.datos[0]==ip):
		    #Si se permite el Bounce Attack o la ip indicada es la del cliente
		    self.tipo_data_con=2
		    self.datos_data_con=(ip,puerto)
		    mostrar_error(self,200)
		    self.setear_data_con(2,ip,puerto)
		  else:
		    mostrar_error(self,425)
	      else:
		mostrar_error(self,tienepermisos(self,comando))
	    elif(comando=='CWD'
	    or comando=='CDUP'
	    or comando=='NLST'
	    or comando=='LIST'
	    or comando=='STAT'
	    or comando=='RETR'
	    or comando=='STOR'
	    or comando=='DELE'
	    or comando=='RNFR'
	    or comando=='RNTO'
	    or comando=='MKD'
	    or comando=='RMD'
	    or comando=='STOU'
	    or comando=='APPE'):
	      #Comandos que usen el sistema de directorios
	      #Listar carpetas: os.listdir(dir)
	      #Tipo: os.path.is(dir|file)
	      #UID&GID: os.stat(archivo).st_(u|g)id
	      #Tamaño: os.stat(archivo).st_size
	      
	      if(tienepermisos(self,comando)==True):
		#Delcaracion de variables
		path=self.path
		if(path[-1] != '/'):
		  #Si no termina en /, se le agrega una
		  path=path+'/'
		conf_path=self.conf_path
		if(conf_path[-1] != '/'):
		  conf_path=conf_path+'/'
		rel_path=path[len(conf_path):]
		#print 'Rel_path: ',rel_path
		if(comando!='CDUP'):
		  destino=parametros
		  if(destino==''):
		    if(comando=='CWD'):
		      destino='/'
		    else:
		      destino='.'
		else:
		  #Si el comando es CDUP
		  destino='..'
		
		#Path absoluto o relativo
		if(destino[0] != '/'):
		  #Path relativo
		  destino=rel_path+destino
		  
		#Filtrar .. , . y //
		split=destino.split('/')
		dirs=[]
		for actual in split:
		  #Ignora si esta vacio o es .
		  if(actual!='' and actual!='.'):
		    if(actual=='..'):
		      #Quita el ultimo directorio(si existe alguno) para elevar
		      if(len(dirs)>0):
			dirs.pop()
		    else:
		      #Agrega el directorio al array
		      dirs.append(actual)
		if(len(dirs)==0):
		  actual=''
		else:
		  actual=''
		  for i in range(0,len(dirs)-1):
		    actual=actual+dirs[i]+'/'
		  actual=actual+dirs[-1]
		  
		#Ve si el parametro solicitado es un archivo o directorio
		if(comando=='CWD'
		or comando=='CDUP'
		or comando=='RMD'):
		  #Solo se permiten directorios
		  existe=False
		  if(os.path.isdir(conf_path+actual)):
		    existe=True
		elif(comando=='NLST'
		or comando=='LIST'
		or comando=='STAT'
		or comando=='RNFR'
		or comando=='RNTO'):
		  #Se permiten ficheros y directorios
		  existe=False
		  if(os.path.isdir(conf_path+actual) or os.path.isfile(conf_path+actual)):
		    existe=True
		elif(comando=='RETR'
		or comando=='DELE'
		or comando=='APPE'):
		  #Solo se permiten ficheros
		  existe=False
		  if(os.path.isfile(conf_path+actual)):
		    existe=True
		elif(comando=='STOR'
		or comando=='RNTO'
		or comando=='MKD'
		or comando=='STOU'):
		  #Se esta creando un fichero o directorio nuevo
		  existe=True
		
		#Ejecuta las acciones si el archivo o directorio existe
		if(existe):
		  if(comando=='CWD' or comando=='CDUP'):
		    try:
		      self.path=conf_path+actual
		      self.cambiar_carpeta(self.path[len(self.conf_path):])
		      mostrar_error(self,250)
		    except:
		      self.error_carpeta(conf_path+actual,1)
		  elif(comando=='NLST' or comando=='LIST' or comando=='STAT'):
		    #Lista el directorio, se le agregan . y ..
		    listar=conf_path+actual
		    continuar=False
		    try:
		      if(os.path.isdir(listar)):
			listado=os.listdir(listar)
		      else:
			listado=[listar]
			listar=''
		      continuar=True
		    except:
		      self.error_carpeta(conf_path+actual,4)
		      mostrar_error(self,550)
		    if(continuar):
		      if(listar != ''):
			listado=['.','..']+listado
		      contenido=''
		      for arc in listado:
			#Agrefa info si es list
			if(comando=='LIST' or comando=='STAT'):
			  #Le añade permisos de directorio si lo es
			  if(os.path.isdir(listar+'/'+arc)):
			    permisos='drwxrwxrwx'
			  else:
			    permisos='-rwxrwxrwx'
			  #La cantidad de enlaces por ahora siempre sera 1
			  enlaces='1'
			  #Obtiene  el GID, UID y tamaño
			  #print listar,arc
			  correcto=True
			  try:
			    stat=os.stat(listar+'/'+arc)
			  except:
			    correcto=False #No se lista el elemento
			  if(correcto):
			    uid=str(stat.st_uid)
			    gid=str(stat.st_gid)
			    size=str(stat.st_size)
			    #Calcula una fecha fija, todavia no se ven fechas reales
			    fecha='Jan 01 00:00'
			    #Concatena todo
			    contenido=contenido+permisos+' '+enlaces+' '+uid+' '+gid+' '+size+' '+fecha+' '+arc+'\n'
			  else:
			    contenido=''
			elif(comando=='NLST'):
			  contenido=contenido+arc+'\n'
		      if(comando=='LIST' or comando=='NLST'):
			#Envia el listado por la conexion de datos
			enviar_data_con(self,contenido)
		      elif(comando=='STAT'):
			#Envia los datos por la conexion principal
			if(parametros==''):
			  try:
			    self.sock.send('211 '+self.servidor.conf['server_name']+'\n') #El mensaje del codigo de error 211 es el tipo de servidor
			  except:
			    self.sock.close()
			else:
			  self.sock.send('213-STAT\n')
			  self.sock.send(contenido)
			  self.sock.send('213 End\n')
		  elif(comando=='RETR'
		  or   comando=='STOR'
		  or   comando=='APPE'):
		    if(parametros==''):
		      mostrar_error(self,501)
		    else:
		      continuar=True
		      try:
			if(comando=='RETR'):
			  arc=open(conf_path+actual,'r')
			  arc.seek(self.seek)
			  contenido=arc.read()
			else:
			  if(comando=='STOR'):
			    arc=open(conf_path+actual,'w')
			  elif(comando=='APPE'):
			    arc=open(conf_path+actual,'a')
			  #Recibe y para luego escribir en el archivo
			  recibido=enviar_data_con(self,recibir=True)
			  if(recibido==None):
			    recibido=''
			  arc.write(recibido)
			arc.close()
		      except IOError:
			continuar=False
			if(comando=='RETR'):
			  self.error_archivo(conf_path+actual,1)
			else:
			  self.error_archivo(conf_path+actual,2)
			mostrar_error(self,550)
		      if(continuar):
			if(comando=='RETR'):
			  enviar_data_con(self,contenido)
		      if(comando=='RETR'):
			del(contenido)
		  elif(comando=='DELE'):
		    if(parametros==''):
		      mostrar_error(self,501)
		    else:
		      try:
			os.remove(conf_path+actual)
			mostrar_error(self,250)
		      except:
			self.error_archivo(conf_path+actual,4)
			mostrar_error(self,550)
		  elif(comando=='RNFR'):
		    if(parametros==''):
		      mostrar_error(self,501)
		    else:
		      self.renombrar=conf_path+actual
		      mostrar_error(self,350)
		  elif(comando=='RNTO'):
		    if(parametros==''):
		      mostrar_error(self,501)
		    else:
		      try:
			os.rename(self.renombrar,conf_path+actual)
			mostrar_error(self,250)
		      except OSError, error:
			self.error_archivo(self.renombrar,5,conf_path+actual)
			mostrar_error(self,550)
			print error
		  elif(comando=='MKD'):
		    if(parametros==''):
		      mostrar_error(self,501)
		    else:
		      try:
			os.mkdir(conf_path+actual)
			self.sock.send('257 "'+parametros+'" '+self.servidor.conf['errores'][257]+'\n')
		      except:
			self.error_carpeta(conf_path+actual,2)
			mostrar_error(self,550)
		  elif(comando=='RMD'):
		    if(parametros==''):
		      mostrar_error(self,501)
		    else:
		      try:
			os.rmdir(conf_path+actual)
			mostrar_error(self,250)
		      except:
			self.sock.error_carpeta(conf_path+actual,3)
			mostrar_error(self,550)
		  elif(comando=='STOU'):
		    nombre=self.path+'/'+self.servidor.conf['STOU_prefix']+str(random.randint(0,self.servidor.conf['max_size']))
		    if(os.path.isdir(nombre) or os.path.isfile(nombre)):
		      #Si existe
		      mostrar_error(self,550)
		    else:
		      try:
			arc=open(nombre,'w')
			#Recibe y para luego escribir en el archivo
			recibido=enviar_data_con(self,recibir=True)
			if(recibido==None):
			  recibido=''
			arc.write(recibido)
			arc.close()
		      except IOError:
			self.error_archivo(nombre,2)
			mostrar_error(self,550)
		      
		else:
		  if(parametros!=''):
		    mostrar_error(self,550)
		  else:
		    mostrar_error(self,501)
	      else:
		mostrar_error(self,tienepermisos(self,comando))
	    elif(comando=='PWD'):
	      if(tienepermisos(self,comando)==True):
		#Calcula el path relativo para no mostrar el absoluto
		path=self.conf_path
		rel_path=self.path[len(path):]
		#if(path[-1]!='/'):
		#if(self.path[-1]!='/'):
		if(len(rel_path)>0):
		  if(rel_path[0]!='/'):
		    rel_path='/'+rel_path
		else:
		  rel_path='/'
		
		self.sock.send('257 "'+rel_path+'" '+self.servidor.conf['errores'][257]+'\n')
	      else:
		mostrar_error(self,tienepermisos(self,comando))
	    elif(comando=='ABOR'):
	      #No me interesa implementarlo
	      mostrar_error(self,502)
	    elif(comando=='REST'):
	      if(not re.match('^[0-9]+$',parametros)):
		mostrar_error(self,501)
	      else:
		self.seek=int(parametros)
		mostrar_error(self,200)
	    elif(comando=='SYST'):
	      if(tienepermisos(self,comando)==True):
		self.sock.send('215 UNIX Type: L8\n')
	      else:
		mostrar_error(self,tienepermisos(self,comando))
	    elif(comando=='HELP'):
	      try:
		self.sock.send('214-'+self.servidor.conf['errores'][214]+'\n')
		for site in self.servidor.site.items():
		  self.sock.send(' '+site[0]+'\n')
		self.sock.send('214 '+self.servidor.conf['server_name']+'\n')
	      except:
		self.sock.close()
	    elif(comando=='TYPE'):
	      #No hara falta ya que es de mas bajo nivel
	      mostrar_error(self,200)
	    elif(comando=='SITE'):
	      comando_site=parametros
	      parametros_site=''
	      find=comando_site.find(' ')
	      if(find != -1): #Si se encuentra un espacio
		comando_site=comando_site[:find].upper()
		parametros_site=parametros[find+1:]
	      else:
		comando_site=parametros.upper()
	      if(not self.servidor.site.has_key(comando_site)): #Si no existe el comando SITE
		mostrar_error(self,500)
	      else:
		self.servidor.site[comando_site](self,comando_site,parametros_site)
	    elif(comando=='QUIT'):
	      user=''
	      if(self.logueado):
		user=self.user
	      self.logout(user,self.datos)
	      mostrar_error(self,221)
	      self.sock.close()
	    else:
	      self.sock.send('500 '+self.servidor.conf['errores'][500]+'\n')
      except socket.error, error:
	self.sock.close()
	self.error_socket(error,self.datos)
	#print 'Conexion de',self.__datos,'cerrada por el cliente'
	break
    
  
  #Declaración de eventos
  def pedir_archivo(self,nombre):
    """Evento que se produce al solicitar un cliente la lectura de un archivo"""
    pass
  def subir_archivo(self,nombre):
    """Evento que se produce al solicitar un cliente la subida de un archivo"""
    pass
  def error_archivo(self,nombre,tipo_acceso,destino=''):
    """Evento que se produce al producirse un error al intentar abrir el archivo
    tipo_acceso indica el tipo de acceso que se le da al archivo siendo:
      1: lectura
      2: escritura
      3: escritura en append
      4: borrar
      5: renombrar
      6: obtener tamaño
      y destino solo se usa cuando se quiere renombrar(puede ser un directorio)"""
    pass
  def cambiar_carpeta(self,carpeta):
    """Evento que se produce al cambiar la carpeta actual"""
    pass
  def error_carpeta(self,carpeta,tipo_acceso):
    """Evento que se produce al producirse un error al abrir la carpeta
    tipo_acceso:
      1: cambiar
      2: crear
      3: borrar
      4: listar"""
    pass
  def error_socket(self,errores,datos):
    """Evento que se produce al producirse un error al abrir el socket
    errores=lo que devuelve el except"""
    pass
  def intento_login(self,user,contra,exitoso):
    """Evento que se produce al un usuario intentar loguearse
    exitoso indica si se logueo o no"""
    pass
  def comando_ejecutado(self,comando,params):
    """Este evento se produce cuando se un usuario ejecuta un comando"""
    pass
  def setear_data_con(self,metodo,ip,puerto):
    """Este evento se produce cuando el usuario quiere cambiar el tipo de conexión de datos
    metodo=1 para PASV y 2 para PORT"""
    pass
  def logout(self,user,datos):
    """Este evento se produce cuando se ejecuta el comando QUIT. Si user está vacío
    significa que no se logueó"""
    pass

#Declaración de funciones
def ip_normal_a_ftp(normal):
  """Convierte una IP normal a una del FTP"""
  #Splitea por .
  split=normal.split('.')
  
  #Comprueba que sea num.num.num.num y no num.num.num, num.num.num.num.num, etc
  if(len(split))!=4:
    return False
  #print split
    
  #Comprueba que sea un numero, que num<256 y que no tenga ceros a la izquierda.
  for i in range(0,4):
    num=split[i]
    if(not re.match('^[0-9]+$',num)):
      return False
    if(not int(num)<256):
      return False
    if(not re.match('^(0|[1-9][0-9]*)$',num)):
      return False
    
  #Setea ftp, joinea todo con ",", le añade el ultimo número y retorna
  ftp=''
  for i in range(0,3):
    ftp=ftp+split[i]+','
  ftp=ftp+split[3]
  return ftp
  
def ip_ftp_a_normal(ftp):
  """Convierte una IP del FTP a una normal"""
  #Splitea por ,
  split=ftp.split(',')
  
  #Comprueba que sea num.num.num.num y no num.num.num, num.num.num.num.num, etc
  if(len(split))!=6:
    return False
  #print split
  
  #Quita el puerto
  split=split[:4]
    
  #Comprueba que sea un numero, que num<256 y que no tenga ceros a la izquierda.
  for i in range(0,4):
    num=split[i]
    if(not re.match('^[0-9]+$',num)):
      return False
    if(not int(num)<256):
      return False
    if(not re.match('^(0|[1-9][0-9]*)$',num)):
      return False
    
  #Setea ftp, joinea todo con ".", le añade el ultimo número y retorna
  ftp=''
  for i in range(0,3):
    ftp=ftp+split[i]+'.'
  ftp=ftp+split[3]
  return ftp
  
def puerto_normal_a_ftp(normal):
  """Convierte un puerto normal a uno de FTP(el parametro es int)"""
  #Se fija que sea menos a 65536
  if(not normal<65536):
    return False
  
  puerto_a=normal/256
  puerto_b=normal%256
  puerto=str(puerto_a)+','+str(puerto_b)
  return puerto
  
def puerto_ftp_a_normal(ftp):
  """Convierte un puerto de FTP a uno normal(el parametro es str)"""
  #Splitea por ,
  split=ftp.split(',')
  
  #Se fija la longitud
  if(len(split)!=6):
    return False
    
  #Le quita la IP
  split=split[4:]
    
  #Hacer con cada split
  for num in split:
    #Se fija que sea un número
    if(not re.match('^[0-9]+$',num)):
      return False
    
    #Se fija que num<256
    if(not int(num)<256):
      return False
    
  return int(split[0])*256+int(split[1])

def mostrar_error(h_cliente,codigo):
  """Funcion para mostrar un error(o no error) en una conexion al servidor. Uso: mostrar_error(handle_cliente,error_code)"""
  h_cliente.sock.send(str(codigo)+' '+h_cliente.servidor.conf['errores'][codigo]+'\n')
  
def enviar_data_con(h_cliente,datos='',recibir=False):
  """Funcion para enviar datos a traves de la conexion de datos. Uso: enviar_data_con(handle_cliente,datos). Tambien permite recibir"""
  if(h_cliente.tipo_data_con==0):
    #No se especifica conexion de datos
    mostrar_error(h_cliente,425)
  elif(h_cliente.tipo_data_con==1):
    """Conexion pasiva"""
    try:
      aceptado=h_cliente.h_data_con.accept()
      mostrar_error(h_cliente,150)
      h_data_client=aceptado[0]
      if(h_cliente.servidor.conf['permitir_bounce']==True or aceptado[1][0]==h_cliente.datos[0]):
	#Si se permite el Bounce Attack o la IP que se conecto es la misma de la del cliente
	if(not recibir):
	  h_data_client.send(datos)
	  h_data_client.close()
	else:
	  #Lee hasta que se cierre la conexion
	  recibido=''
	  recibir=h_data_client.recv(h_cliente.servidor.conf['max_size'])
	  while(recibir!=''):
	    recibido=recibido+recibir
	    recibir=h_data_client.recv(h_cliente.servidor.conf['max_size'])
	  h_data_client.close()
	  mostrar_error(h_cliente,226)
	  return recibido
	correctamente=True
      else:
	mostrar_error(self,425)
	correctamente=False
    except socket.error, error:
      correctamente=False
      #print error
      try:
	h_data.close()
	h_data_client.close()
      except:
	pass
      h_cliente.error_socket(error,h_cliente.datos)
      mostrar_error(h_cliente,425)
    else:  
      mostrar_error(h_cliente,226)
      
  elif(h_cliente.tipo_data_con==2):
    #Si la conexion es activa
    try:
      h_data=socket.socket()
      h_data.connect((h_cliente.datos_data_con[0],h_cliente.datos_data_con[1]))
      mostrar_error(h_cliente,150)
      if(not recibir):
	h_data.send(datos)
	h_data.close()
      else:
	#Lee hasta que se cierre la conexion
	recibido=''
	recibir=h_data.recv(h_cliente.servidor.conf['max_size'])
	while(recibir!=''):
	  recibido=recibido+recibir
	  recibir=h_data.recv(h_cliente.servidor.conf['max_size'])
	h_data.close()
	mostrar_error(h_cliente,226)
	return recibido
    except socket.error, error:
      try:
	h_data.close()
      except:
	pass
      h_cliente.error_socket(error,h_cliente.datos)
      mostrar_error(h_cliente,425)
    else:
	mostrar_error(h_cliente,226)
  else:
      mostrar_error(h_cliente,425)
def tienepermisos(cliente,comando):
  """or comando=='STOR'
	    or comando=='DELE'
	    or comando=='RNFR'
	    or comando=='RNTO'
	    or comando=='MKD'
	    or comando=='RMD'
	    or comando=='STOU'
	    or comando=='APPE'"""
  comandos_write=[
    'STOR',
    'DELE',
    'RNFR',
    'RNTO',
    'MKD',
    'RMD',
    'STOU',
    'APPE'
  ] #Comandos que solo se ejecutan si se tiene permisos de escritura
  if(cliente.logueado):
    #Si se logueo
    if(comandos_write.count(comando)==0):
      #Si el comando no necesita permisos de escritura
      return True
    else:
      if(cliente.acceso_escritura):
	#Si el usuario tiene permisos de escritura
	return True
      else:
	return 553
  else:
    return 530

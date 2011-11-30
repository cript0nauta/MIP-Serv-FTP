#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Agregado a MIP-Ftp para mostrar lo que se realiza en la pantella
#by sh4r3m4n
#Esta aplicacion se encuentra bajo licensia Creative Commons, visible en
#http://creativecommons.org/licenses/by/2.5/ar/

def site_whoami(cliente,comando,parametros):
  if(cliente.logueado):
    cliente.sock.send('200 '+cliente.user+'\n')
  else:
    lib_mipftp.mostrar_error(cliente,530)

configuracion={
  'site':{'WHOAMI':site_whoami},
  'server_name':'Mip-Serv FTP v1.1 BETA by sh4r3m4n(http://sh4r3m4n.webcindario.com/mipserv/ftp/)',
  'run_user':'www-data', #Es conveniente darle un valor a esta variable para evitar correr con todos los privilegios
  'permitir_bounce':False,
  'ip':'',
  'ip_pasv':'192.168.2.3', #Cambiar por la IP pública
  'puerto':21,
  'usuarios':{
    'admin':['cuidado','/var/www',True],
    'anonymous':[False,'/var/www',False]
    },
  'rango_pasv':range(20000,21000),
  'errores':{
    150:'Conexion de datos aceptada',
    200:'OK',
    214:'Los siguientes comandos SITE son reconocidos', #Se muestran dos mensajes 214, esta variable indica el primero, el segundo es server_name
    220:'Bienvenido a Mip-Serv FTP. Debe loguearse antes de ejecutar algún comando',
    221:'Cerrando sesión',
    226:'Comando de conexion de datos ejecutado correctamente',
    227:'Iniciando modo pasivo',
    230:'Autenticado!',
    250:'OK',
    257:'Accion de directorio ejecutada correctamente',
    350:'OK',
    425:'No ha especificado una conexion de datos o no se pudo conectar',
    331:'Se requiere contraseña',
    500:'Comando no encontrado',
    501:'Parametros incorrectos',
    502:'Orden no implementada',
    530:'Login fallido',
    550:'Error en el sistema de ficheros. Compruebe su nombre y su tipo',
    553:'Operación no permitida. Pruebe usar una cuenta con más privilegios'
    },
  'max_cons':2,
  'max_size':1024*1024, #1 MegaByte
  'STOU_prefix':'mipftp_stoufile_'
  }

#Importa la librería principal
import lib_mipftp

class servidor(lib_mipftp.servidor):
  #Clase derivada del servidor original
  def escuchar(self,ip,puerto):
    print 'Escuchando conexiones (',ip,',',puerto,')'
  def nueva_con(self,datos):
    print 'Nueva conexión de',datos[0],'en el puerto',datos[1]
  def error_bindeando(self):
    print 'Error intentando escuchar en el puerto',self.conf['puerto']
  def interrupcion(self):
    print 'Cerrando el programa por interrupción'
class cliente(lib_mipftp.cliente):
  def pedir_archivo(self,nombre):
    print self.datos[0]+':'+str(self.datos[1]),'quiere leer el archivo',nombre
  def subir_archivo(self,nombre):
    print self.datos[0]+':'+str(self.datos[1]),'quiere escribir en el archivo',nombre
  def error_archivo(self,nombre,acceso,destino=''):
    dir_acceso={
      1:'leer',
      2:'escribir',
      3:'escribir en append',
      4:'borrar',
      5:'renombrar',
    }
    str_destino=''
    if(destino != ''):
      str_destino='con destino a '+destino
    print 'Error al',dir_acceso[acceso],nombre,str_destino
  def cambiar_carpeta(self,carpeta):
    print self.datos[0]+':'+str(self.datos[1]),'cambia el directorio de trabajo a',carpeta
  def error_carpeta(self,carpeta,acceso):
    dir_acceso={
      1:'cambiar',
      2:'crear',
      3:'borrar',
      4:'listar'
    }
    print 'Error al',dir_acceso[acceso],'la carpeta',carpeta
  def intento_login(self,user,contra,exitoso):
    exito={
      True:'correctamente',
      False:'incorrectamente'
    }
    print self.datos[0]+':'+str(self.datos[1]),'intenta loguearse',exito[exitoso],'con el usuario',user,'y la contraseña',contra
  def comando_ejecutado(self,comando,parametros):
    print self.datos[0]+':'+str(self.datos[1]),'ejecuta el comando',comando,'con los parámetros',parametros
  def setear_data_con(self,metodo,ip,puerto):
    metodos={
      1:'PASV',
      2:'PORT'
    }
    print self.datos[0]+':'+str(self.datos[1]),'setea su conexión de datos',metodos[metodo],'con la IP',ip,'y el puerto',puerto
  def logout(self,user,datos):
    print self.datos[0]+':'+str(self.datos[1]),'cerro sesión'

#Declara el servidor
server=servidor(configuracion,cliente)

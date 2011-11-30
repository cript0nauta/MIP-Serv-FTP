#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Servidor MIP-Ftp
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
  'server_name':'Mip-Serv FTP v1.0 by sh4r3m4n(http://sh4r3m4n.webcindario.com/mipserv/ftp/)',
  'run_user':False,
  'permitir_bounce':False, #No se permite Bounce Attack
  'ip':'',
  'ip_pasv':'127.0.0.1',
  'puerto':21,
  'usuarios':{
    'admin':['password','/',True],
    'anonymous':[False,'~',False]
    },
  'rango_pasv':range(1024,65535),
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
  'max_cons':20,
  'max_size':1024*1024, #1 MegaByte
  'STOU_prefix':'mipftp_stoufile_'
  }

#Importa la librería principal
import lib_mipftp

#Declara el servidor
server=lib_mipftp.servidor(configuracion)
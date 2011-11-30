#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Libreria con funciones de carga de archivos de configuración MIP-Serv FTP
#by sh4r3m4n
#Esta aplicacion se encuentra bajo licensia Creative Commons, visible en
#http://creativecommons.org/licenses/by/2.5/ar/

#Declaración de la función de conversión de archivo a array
def arc_a_array(arc):
  """Función a la que se le pasa el nombre de un archivo con extensión .py, lo importa y devuelve un array de configuración MIP-Serv FTP"""
  import arc
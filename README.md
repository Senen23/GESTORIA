# APP COMPENSACIONES

Esta aplicación permite gestionar la carga y búsqueda de información relacionada con compensaciones. Utiliza Tkinter para la interfaz gráfica y se conecta a una base de datos Oracle para almacenar y recuperar datos. Tambien permite el calculo de LAS COMPENSACIONES, Y EL CHEQUEO DE LOS PAGOS.

## Requisitos

- Python 3.x
- Las siguientes bibliotecas de Python (instalables a través del archivo `requirements.txt`):

  - pandas
  - openpyxl
  - cx_Oracle
  - tkcalendar


-PARA CREAR EL EJECUTABLE USA ESTE CODIGO: pyinstaller --hidden-import=babel.numbers --add-data "ui/images/*:images" --icon=icono.ico --windowed main.py

# por: Julian Esteban Suarez Gallego
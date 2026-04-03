# PyBridge - COM Port Connector & Manager

¡Bienvenido a **PyBridge**! Esta es una aplicación de escritorio desarrollada en Python que permite interconectar y gestionar puertos serie físicos y virtuales en Windows de manera muy sencilla, con una interfaz gráfica moderna. 

Con esta herramienta podrás:
- Crear y eliminar pares de puertos COM virtuales (ej. `COM20` conectado con `COM21`).
- Hacer "puentes" (relay) entre dos puertos (físicos o virtuales) para que se comuniquen entre sí a diferentes tasas de baudios de manera interactiva y transparente.
- Monitorear el flujo de datos intercambiados en tiempo real.

## Requisitos y Dependencias Previas

Para que el proyecto funcione correctamente desde el código fuente, es necesario contar con un entorno de **Python 3.8+** y las siguientes bibliotecas. Puedes instalarlas todas juntas desde la terminal:

```bash
pip install pyserial customtkinter pywinstyles
```

*(Nota: Si vas a utilizar la versión empaquetada `.exe`, no necesitas instalar Python ni estas librerías).*

---

## 1. Instalación del Driver de Puertos Virtuales (com0com)

Para poder crear puertos virtuales de la nada (por ejemplo, COM20 y COM21), el programa utiliza la herramienta de código abierto **com0com**.

Junto a este repositorio o carpeta encontrarás el archivo de instalación: `com0com-2.2.2.0-x64-fre-signed.zip`. Si no lo tienes instalado, sigue estos pasos:

1. **Descomprime** el archivo `.zip`.
2. Ejecuta el archivo instalador principal (`setup.exe`).
3. Asegúrate de otorgar todos los **Permisos de Administrador**.
4. ¡Sigue las instrucciones en pantalla! (puedes instalarlo con las opciones por defecto). Es posible que durante la instalación te pregunte si confías en el driver; asegúrate de marcar la opción de instalar los controladores de todas formas.
5. Una vez instalado, com0com quedará ubicado en `C:\Program Files (x86)\com0com\setupc.exe`. **Nuestra aplicación PyBridge está diseñada para buscarlo automáticamente en esta ruta**.

---

## 2. Cómo Usar PyBridge (Paso a Paso)

Ejecuta el archivo `gui.py` o el ejecutable compilado. *(Recomendación: Si planeas crear nuevos puertos virtuales desde la aplicación, haz clic derecho sobre ella o tu terminal y selecciona **"Ejecutar como Administrador"** para tener los permisos correctos).*

### Pestaña: "Admin Puertos (Virtual)"

Esta es la sección en la que podrás "fabricar" puertos COM virtuales que estarán emparejados. Todo lo que envíes al primer puerto COM de un par saldrá mágicamente por el segundo.

1. Navega a la pestaña de **Admin Puertos (Virtual)**.
2. Ingresa el nombre de **Puerto Virtual A** (ej. `COM20`) y el **Puerto Virtual B** (ej. `COM21`). *Asegúrate de escribir "COM" antes del número.*
3. Presiona **INSTALAR NUEVO PAR**.
4. Verás en el recuadro negro que ha aparecido un "Par" nuevo. A partir de este momento, en tu Administrador de Dispositivos de Windows verás instalados virtualmente tus puertos interconectados con un cable cruzado imaginario.
5. Para borrar uno permanentemente, simplemente selecciona el par en la lista desplegable inferior y presiona **Eliminar Par Seleccionado**.

### Pestaña: "Puente (Relay)"

Sirve para escuchar y enviar información entre dos puertos (físicos o virtuales) cualesquiera. Por ejemplo, si tienes un microcontrolador físico en el COM3 y creaste el COM20 virtual.

1. Dirígete a la pestaña **Puente (Relay)**.
2. Si acabas de conectar un dispositivo físico nuevo o sumaste puertos virtuales, presiona **Actualizar Lista**.
3. En la lista **Puerto A**, selecciona tu primer puerto.
4. En la lista **Puerto B**, selecciona el segundo puerto de destino.
5. Elige la **Tasa de Baudios** (ej. `9600`).
6. Presiona el gran botón **INICIAR PUENTE**.
7. ¡Listo! Todo el tráfico que entra por el Puerto A será retransmitido al Puerto B y viceversa. Podrás ver un registro en vivo en la consola inferior para confirmar el tránsito del flujo de datos en modo log.

---

## Cómo Compilar en Ejecutable (Opcional)
Si deseas generar tu propio archivo `.exe` final para distribur fácilmente sin revelar este código:
1. Asegúrate de tener PyInstaller instalado usando: `pip install pyinstaller`.
2. Asegúrate de estar en esta misma carpeta de desarrollo y ejecuta el archivo de empaquetado `package.py`:
```bash
python package.py
```
3. Tu archivo listo para usar aparecerá dentro de la carpeta `dist`.

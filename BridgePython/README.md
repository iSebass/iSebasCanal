# PyBridge - Conector y Gestor de Puertos COM

¡Bienvenido a **PyBridge**! 

¿Necesitas conectar dos puertos serie (físicos o virtuales) de forma sencilla? Esta aplicación con interfaz gráfica te permite "unir" dos puertos con un cable cruzado imaginario. Todo lo que envíes por un extremo pasará mágicamente al otro, ideal para depurar equipos electrónicos, interceptar datos o simular hardware de forma remota.

**📣 IMPORTANTE PARA USUARIOS FINALES:** 
**NO necesitas saber programar, ni instalar Python en tu computadora, ni usar la consola de comandos.** Hemos preparado una versión independiente y lista para usarse. La aplicación correrá con un simple doble clic (busca el archivo `.exe` que acompaña este manual). 

A continuación, tienes la guía "a prueba de fallos" detallada paso a paso.

---

## 📖 GUÍA PARA USUARIOS FINALES (No requiere conocimientos técnicos)

Para usar este programa con su máxima capacidad, lo único que tienes que hacer son dos pasos principales: instalar un simulador (solo si necesitas crear puertos inventados o virtuales) y abrir el programa.

### Paso 1: Instalar "com0com" (El motor de los Puertos Virtuales)
Nuestra aplicación utiliza para funcionar un driver informático muy confiable llamado **com0com**. Si quieres crear puertos virtuales (por ejemplo, inventarte un puerto "COM20" y conectarlo a un "COM21" aunque no tengas cables reales en tu PC), es obligatorio instalar este programa primero.

1. Dentro de esta carpeta, busca el archivo comprimido llamado `com0com-2.2.2.0-x64-fre-signed.zip`.
2. **Descomprímelo** (Clic derecho > Extraer aquí) y busca dentro el instalador (generalmente llamado `setup.exe`).
3. Dale **doble clic**. Cuando Windows te pida permisos administrativos, dile que **Sí / Aceptar**.
4. Sigue todas las ventanas dándole al botón **"Next"** (Siguiente). Las opciones que vienen marcadas por defecto son perfectas.
5. ⚠️ **MUY IMPORTANTE:** Si durante la instalación Windows hace sonar una advertencia de seguridad en rojo/amarillo preguntando si "confías en el origen de estos controladores", debes seleccionar obligatoriamente **"Instalar este software de controlador de todas formas"**. Es completamente seguro, pero Windows lo pregunta siempre con los simuladores de hardware.
6. ¡Listo! Una vez que termine de cargar, no necesitas hacer nada más con com0com. Operará silenciosamente en el fondo del sistema.

### Paso 2: Ejecutar el Programa principal (PyBridge)
1. Busca en la carpeta del repositorio el archivo llamado **`PyBridge.exe`**.
2. Dale **doble clic**. 
   *(💡 **Súper Recomendación:** Si planeas crear puertos virtuales utilizando la herramienta, dale en su lugar clic derecho y escoge la opción **"Ejecutar como Administrador"**. Esto garantizará que Window no bloquee la creación de los nuevos puertos).*
3. ¡Felicidades! Se abrirá la ventana principal de nuestra aplicación lista para facilitarte el trabajo. No tuviste que instalar Python en ningún lado.

---

## 🕹️ ¿CÓMO SE USA PYBRIDGE? (Manual de la Interfaz)

Una vez abierto nuestro ejecutable, verás dos pestañas en la parte superior:

### 1. Pestaña "Admin Puertos (Virtual)"
Úsala para generar pares nuevos de puertos desde cero que no existen físicamente.
- Asegúrate de haber abierto PyBridge con permisos de Administrador.
- En la casilla **Puerto Virtual A**, escribe cómo quieres que se llame, por ejemplo: `COM20`. *(Recuerda escribir siempre "COM" en mayúscula seguido del número).*
- En la casilla **Puerto Virtual B**, escribe a quién quieres que esté conectado, por ejemplo: `COM21`.
- Presiona el botón verde grande: **INSTALAR NUEVO PAR**.
- Observa el recuadro negro de la pantalla. Si todo salió bien, verás que tu par ya fue añadido con éxito. Si ahora vas a tu Administrador de Dispositivos de Windows descubrirás tus 2 puertos COM operando.
- Si te aburres del puerto o te equivocaste, sencillamente búscalo en la lista desplegable de abajo y presiona el botón rojo **Eliminar Par Seleccionado**.

### 2. Pestaña "Puente (Relay)"
Sirve para coger dos puertos que ya están en existencia (pueden ser equipos físicos reales que conectaste por USB o los puertos virtuales creados arriba) y enlazarlos para que charlen entre ellos.
- Presiona el botón gris claro **Actualizar Lista** a la derecha para que el programa escanee nuevamente todos tus puertos en Windows.
- Selecciona tu **Puerto A** en el primer menú desplegable de la izquierda.
- Selecciona tu **Puerto B** (el destino) en el segundo menú desplegable.
- Escoge a qué **velocidad (Baudios)** deseas que se comuniquen. *Si el fabricante no te requiere un número especial, déjalo en el normal que es `9600`.*
- ¡Dedo al gatillo! Dale clic al gran botón azul **INICIAR PUENTE**.
- Verás que en el cuadro negro inferior empieza a aparecer información en vivo registrando todos los bytes de respuesta que van viajando del Puerto A al B y viceversa. Para parar esta fiesta de tramas, simplemente presiona el mismo botón que ahora dice "DETENER PUENTE".

---

## 💻 SECCIÓN TÉCNICA (SÓLO PARA DESARROLLADORES)
*Ignora esta área si vas a usar el .exe.* 
Si eres un compañero programador que descargó el código fuente (los archivos `.py`), aquí te dejo los requisitos:

**1. Entorno Base (Source):**
- Instala Python 3.8+.
- Crea un `venv` e instala las dependencias gráficas y de puerto de serie por medio de la consola así:
  ```bash
  pip install pyserial customtkinter pywinstyles pyinstaller
  ```

**2. Cómo recomilar o modificar el Ejecutable (`.exe`):**
Si le hiciste cambios visuales a la interfaz (`gui.py`) o de eficiencia al puenteado (`serial_bridge.py`) y te gustaría distribuir de nuevo el producto final a las personas:
Sencillamente abre la terminal en esta mismísima ruta (raíz del proyecto) y corre nuestro script empaquetador automático:
```bash
python package.py
```
*Esto activará PyInstaller y pondrá tu flamante `PyBridge.exe` encapsulado y listo para usar en tu computadora dentro de la nueva carpeta llamada `dist`.*

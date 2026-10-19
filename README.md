# 🎯 Atrapa al Jugador

**Atrapa al Jugador** es un videojuego de estrategia y escape desarrollado en Python utilizando la librería Pygame. El objetivo es simple: debes guiar a tu personaje desde su posición inicial hasta la meta (la estrella verde) evitando ser interceptado por los enemigos. 

El proyecto incluye un modo de un jugador contra una Inteligencia Artificial (que utiliza el algoritmo de búsqueda BFS para cazarte) y un modo multijugador local 1 vs 1.

## ✨ Características

- **Modo 1 Jugador:** Escapa de los enemigos controlados por la computadora.
- **Modo 2 Jugadores (Local):** Juega contra un amigo en la misma pantalla. Personaliza los nombres de ambos jugadores.
- **3 Niveles de Dificultad:** Fácil (3x3), Medio (4x4) y Difícil (5x5), afectando el tamaño del tablero y la cantidad de enemigos.
- **Controles Flexibles:** Juega con el mouse o utiliza el teclado (soporta movimientos diagonales combinando teclas).
- **Interfaz Adaptable:** El menú, los botones y el tablero se ajustan dinámicamente al tamaño de la ventana. Puedes maximizar y restaurar la ventana sin problemas.
- **Sistema de Audio:** Efectos de sonido para movimientos, victorias, derrotas y navegación, con opción de silenciar.
- **Diseño Atractivo:** Gráficos generados dinámicamente con SVG, animaciones fluidas y resaltado del turno actual.

## 🛠️ Requisitos previos

Asegúrate de tener instalado Python (versión 3.8 o superior). El proyecto utiliza las siguientes librerías, las cuales están listadas en el archivo `requirements.txt`:

- `pygame-ce` (Community Edition de Pygame)
- `cairosvg` (Para la generación y conversión de gráficos SVG) 
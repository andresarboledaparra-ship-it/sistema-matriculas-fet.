# Sistema de Gestión de Matrículas Académicas - FET

Proyecto del parcial final: análisis y diseño de un sistema de matrículas para la Fundación Escuela Tecnológica de Neiva (FET).

## Integrantes
Andres Felipe Arboleda Parra

**Curso:** [Nombre del curso] · **Docente:** [Nombre del docente] · **Fecha:** 11 de noviembre de 2026

## Descripción
La FET maneja parte de sus matrículas de forma manual o en hojas de cálculo, lo que genera errores, demoras y poco control de los cupos. Este proyecto propone un sistema que permite:

- Registrar estudiantes y consultar sus datos.
- Consultar asignaturas, horarios y cupos disponibles.
- Verificar requisitos y conflictos de horario.
- Matricular o cancelar asignaturas.
- Generar comprobantes y reportes académicos.

## Enfoques aplicados
- **Estructurado:** cinco procesos principales y diagrama de flujo de la matrícula.
- **Orientado a objetos:** clases `Estudiante`, `Asignatura` y `Matricula` con su diagrama UML.
- **Ágil:** plan de cuatro Sprints de dos semanas.

## Estructura del repositorio
```
.
├── README.md
├── docs/
│   ├── Enfoques_Desarrollo_Software_Matriculas_FET.pdf
│   └── Enfoques_Desarrollo_Software_Matriculas_FET.docx
└── src/
    ├── modelos.py        # Clases Estudiante, Asignatura y Matricula
    ├── sistema.py        # Lógica del sistema y persistencia en JSON
    ├── main.py           # Menú de consola
    └── test_sistema.py   # Pruebas unitarias
```

## Documentación
El informe completo está en [PDF](docs/Enfoques_Desarrollo_Software_Matriculas_FET.pdf) y en [Word](docs/Enfoques_Desarrollo_Software_Matriculas_FET.docx). Incluye los procesos, el diagrama de flujo, el diagrama de clases UML, el plan de Sprints y la matriz comparativa.

## Tecnologías
- Python 3.9 o superior (solo biblioteca estándar, no hay que instalar nada).
- Datos guardados en un archivo JSON (`src/datos/sistema.json`, se crea al ejecutar).

## Ejecución
```bash
cd src
python main.py              # abre el menú del sistema
python -m unittest -v       # ejecuta las pruebas
```
En Windows, si `python` no funciona, probar con `py main.py`.

## Funcionalidades implementadas
- Registro y consulta de estudiantes (con validación de datos).
- Consulta de asignaturas, horarios y cupos disponibles.
- Verificación de prerrequisitos y detección automática de conflictos de horario.
- Matrícula y cancelación de asignaturas, con actualización del cupo.
- Comprobante de matrícula (se guarda en `src/comprobantes/`) y reportes de cupos y académico.

## Relación con el diagrama UML
Las clases implementan los atributos y métodos del diagrama (en `snake_case`). Se agregaron atributos de apoyo que el diagrama simplificado no muestra: `aprobadas` en Estudiante, y `cupo_total` y `prerrequisitos` en Asignatura.

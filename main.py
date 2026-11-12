"""Sistema de Gestión de Matrículas Académicas - FET (menú de consola)."""
from pathlib import Path

from modelos import ErrorMatricula
from sistema import SistemaMatriculas

MENU = """
===== MATRÍCULAS FET =====
1. Registrar estudiante
2. Consultar datos de un estudiante
3. Consultar asignaturas, horarios y cupos
4. Matricular asignatura
5. Cancelar matrícula
6. Ver matrículas y generar comprobante
7. Reporte de cupos
8. Reporte académico de un estudiante
0. Salir
Opción: """


def main():
    sistema = SistemaMatriculas()
    sistema.cargar()
    while True:
        opcion = input(MENU).strip()
        try:
            if opcion == "1":
                doc = input("Documento: ")
                nombres = input("Nombres: ")
                programa = input("Programa: ")
                correo = input("Correo: ")
                aprob = input("Asignaturas ya aprobadas (códigos separados por coma, o vacío): ")
                lista = [c.strip().upper() for c in aprob.split(",") if c.strip()]
                est = sistema.registrar_estudiante(doc, nombres, programa, correo, lista)
                print(f"Estudiante {est.nombres} registrado.")
            elif opcion == "2":
                datos = sistema.buscar_estudiante(input("Documento: ")).consultar_datos()
                for clave, valor in datos.items():
                    print(f"{clave}: {valor}")
            elif opcion == "3":
                for a in sistema.consultar_asignaturas():
                    req = f" (requiere {', '.join(a.prerrequisitos)})" if a.prerrequisitos else ""
                    print(f"{a.codigo} - {a.nombre}{req}\n    Horario: {a.consultar_horario()} | Cupos: {a.cupo_disponible}/{a.cupo_total}")
            elif opcion == "4":
                m = sistema.matricular(input("Documento del estudiante: "), input("Código de la asignatura: "))
                print(f"Matrícula {m.id_matricula} registrada.")
            elif opcion == "5":
                m = sistema.cancelar(input("Número de matrícula (ej. M0001): "))
                print(f"Matrícula {m.id_matricula} cancelada; se liberó el cupo.")
            elif opcion == "6":
                doc = input("Documento del estudiante: ")
                ms = sistema.matriculas_de(doc)
                if not ms:
                    print("No tiene matrículas.")
                for m in ms:
                    print(f"{m.id_matricula} - {m.asignatura.nombre} [{m.estado}]")
                numero = input("Número de matrícula para el comprobante (Enter para omitir): ").strip()
                if numero:
                    texto = sistema.comprobante(numero)
                    print(texto)
                    carpeta = Path(__file__).parent / "comprobantes"
                    carpeta.mkdir(exist_ok=True)
                    (carpeta / f"{numero.upper()}.txt").write_text(texto, encoding="utf-8")
                    print(f"Comprobante guardado en comprobantes/{numero.upper()}.txt")
            elif opcion == "7":
                print(sistema.reporte_cupos())
            elif opcion == "8":
                print(sistema.reporte_estudiante(input("Documento: ")))
            elif opcion == "0":
                sistema.guardar()
                print("Datos guardados. ¡Hasta pronto!")
                break
            else:
                print("Opción no válida.")
        except ErrorMatricula as error:
            print(f"No se pudo completar la operación: {error}")
        sistema.guardar()


if __name__ == "__main__":
    main()

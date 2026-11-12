"""Lógica del sistema de matrículas y persistencia en un archivo JSON."""
import json
from pathlib import Path

from modelos import Asignatura, Estudiante, ErrorMatricula, Matricula

PERIODO_ACTUAL = "2027-1"
ARCHIVO_POR_DEFECTO = Path(__file__).parent / "datos" / "sistema.json"

ASIGNATURAS_INICIALES = [
    Asignatura("PRO101", "Programación I", [("Lunes", "08:00", "10:00"), ("Miércoles", "08:00", "10:00")], 3),
    Asignatura("PRO102", "Programación II", [("Martes", "08:00", "10:00"), ("Jueves", "08:00", "10:00")], 30, ["PRO101"]),
    Asignatura("BD101", "Bases de Datos", [("Lunes", "09:00", "11:00")], 30),
    Asignatura("MAT101", "Matemáticas", [("Martes", "10:00", "12:00"), ("Jueves", "10:00", "12:00")], 40),
    Asignatura("ING201", "Ingeniería de Software", [("Viernes", "14:00", "18:00")], 25, ["PRO101"]),
    Asignatura("ENG101", "Inglés I", [("Miércoles", "14:00", "16:00")], 35),
]


class SistemaMatriculas:
    def __init__(self, archivo=ARCHIVO_POR_DEFECTO, periodo=PERIODO_ACTUAL):
        self.archivo = Path(archivo)
        self.periodo = periodo
        self.__estudiantes = {}
        self.__asignaturas = {}
        self.__matriculas = []
        self.__contador = 0

    # ---------- Estudiantes ----------
    def registrar_estudiante(self, id_estudiante, nombres, programa, correo, aprobadas=None):
        if str(id_estudiante).strip() in self.__estudiantes:
            raise ErrorMatricula("Ya existe un estudiante con ese documento.")
        est = Estudiante.registrar_estudiante(id_estudiante, nombres, programa, correo, aprobadas)
        self.__estudiantes[est.id_estudiante] = est
        return est

    def buscar_estudiante(self, id_estudiante):
        est = self.__estudiantes.get(str(id_estudiante).strip())
        if est is None:
            raise ErrorMatricula("No existe un estudiante con ese documento.")
        return est

    # ---------- Asignaturas ----------
    def agregar_asignatura(self, asignatura):
        self.__asignaturas[asignatura.codigo] = asignatura

    def consultar_asignaturas(self):
        return list(self.__asignaturas.values())

    def buscar_asignatura(self, codigo):
        asg = self.__asignaturas.get(codigo.strip().upper())
        if asg is None:
            raise ErrorMatricula("No existe una asignatura con ese código.")
        return asg

    # ---------- Matrículas ----------
    def matriculas_de(self, id_estudiante, solo_activas=False):
        res = [m for m in self.__matriculas if m.estudiante.id_estudiante == str(id_estudiante).strip()]
        return [m for m in res if m.esta_activa()] if solo_activas else res

    def matricular(self, id_estudiante, codigo):
        est = self.buscar_estudiante(id_estudiante)
        asg = self.buscar_asignatura(codigo)
        activas = self.matriculas_de(id_estudiante, solo_activas=True)
        self.__contador += 1
        mat = Matricula.matricular(f"M{self.__contador:04d}", est, asg, self.periodo, activas)
        self.__matriculas.append(mat)
        return mat

    def cancelar(self, id_matricula):
        for m in self.__matriculas:
            if m.id_matricula == id_matricula.strip().upper():
                m.cancelar()
                return m
        raise ErrorMatricula("No existe una matrícula con ese número.")

    def comprobante(self, id_matricula):
        for m in self.__matriculas:
            if m.id_matricula == id_matricula.strip().upper():
                return m.generar_comprobante()
        raise ErrorMatricula("No existe una matrícula con ese número.")

    # ---------- Reportes ----------
    def reporte_cupos(self):
        lineas = [f"{'Código':8}{'Asignatura':26}{'Cupo total':>11}{'Matric.':>9}{'Disp.':>7}", "-" * 61]
        for a in self.__asignaturas.values():
            usados = a.cupo_total - a.cupo_disponible
            lineas.append(f"{a.codigo:8}{a.nombre:26}{a.cupo_total:>11}{usados:>9}{a.cupo_disponible:>7}")
        return "\n".join(lineas)

    def reporte_estudiante(self, id_estudiante):
        est = self.buscar_estudiante(id_estudiante)
        lineas = [f"Reporte académico de {est.nombres} - Periodo {self.periodo}", "-" * 50]
        ms = self.matriculas_de(id_estudiante)
        if not ms:
            lineas.append("Sin matrículas registradas.")
        for m in ms:
            lineas.append(f"{m.id_matricula}  {m.asignatura.codigo}  {m.asignatura.nombre:24} {m.estado}")
        return "\n".join(lineas)

    # ---------- Persistencia ----------
    def guardar(self):
        self.archivo.parent.mkdir(parents=True, exist_ok=True)
        datos = {
            "contador": self.__contador,
            "estudiantes": [e.to_dict() for e in self.__estudiantes.values()],
            "asignaturas": [a.to_dict() for a in self.__asignaturas.values()],
            "matriculas": [m.to_dict() for m in self.__matriculas],
        }
        self.archivo.write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")

    def cargar(self):
        """Carga el archivo si existe; si no, usa los datos iniciales."""
        if not self.archivo.exists():
            for a in ASIGNATURAS_INICIALES:
                self.agregar_asignatura(Asignatura.from_dict(a.to_dict()))
            return
        d = json.loads(self.archivo.read_text(encoding="utf-8"))
        self.__contador = d.get("contador", 0)
        for e in d["estudiantes"]:
            est = Estudiante.from_dict(e)
            self.__estudiantes[est.id_estudiante] = est
        for a in d["asignaturas"]:
            asg = Asignatura.from_dict(a)
            self.__asignaturas[asg.codigo] = asg
        for m in d["matriculas"]:
            self.__matriculas.append(Matricula(m["id_matricula"], self.__estudiantes[m["id_estudiante"]],
                                               self.__asignaturas[m["codigo_asignatura"]], m["periodo"],
                                               m["fecha"], m["estado"]))

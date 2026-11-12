"""Clases del dominio: Estudiante, Asignatura y Matrícula.

Los atributos son privados (encapsulamiento) y se acceden mediante
propiedades y métodos, tal como se muestra en el diagrama de clases UML.
"""
from datetime import datetime


class ErrorMatricula(Exception):
    """Se lanza cuando una operación de matrícula no se puede realizar."""


def _a_minutos(hora):
    h, m = hora.split(":")
    return int(h) * 60 + int(m)


class Estudiante:
    def __init__(self, id_estudiante, nombres, programa, correo, aprobadas=None):
        self.__id_estudiante = id_estudiante
        self.__nombres = nombres
        self.__programa = programa
        self.__correo = correo
        # Códigos de asignaturas ya aprobadas (sirven para verificar prerrequisitos)
        self.__aprobadas = set(aprobadas or [])

    @classmethod
    def registrar_estudiante(cls, id_estudiante, nombres, programa, correo, aprobadas=None):
        """Crea un estudiante validando sus datos."""
        if not str(id_estudiante).strip():
            raise ErrorMatricula("El documento del estudiante es obligatorio.")
        if not nombres.strip() or not programa.strip():
            raise ErrorMatricula("El nombre y el programa son obligatorios.")
        if "@" not in correo or "." not in correo.split("@")[-1]:
            raise ErrorMatricula("El correo no es válido.")
        return cls(str(id_estudiante).strip(), nombres.strip(), programa.strip(), correo.strip(), aprobadas)

    @property
    def id_estudiante(self):
        return self.__id_estudiante

    @property
    def nombres(self):
        return self.__nombres

    @property
    def programa(self):
        return self.__programa

    @property
    def correo(self):
        return self.__correo

    @property
    def aprobadas(self):
        return set(self.__aprobadas)

    def consultar_datos(self):
        return {
            "id_estudiante": self.__id_estudiante,
            "nombres": self.__nombres,
            "programa": self.__programa,
            "correo": self.__correo,
            "aprobadas": sorted(self.__aprobadas),
        }

    def actualizar_datos(self, nombres=None, programa=None, correo=None):
        if correo is not None:
            if "@" not in correo or "." not in correo.split("@")[-1]:
                raise ErrorMatricula("El correo no es válido.")
            self.__correo = correo.strip()
        if nombres:
            self.__nombres = nombres.strip()
        if programa:
            self.__programa = programa.strip()

    def to_dict(self):
        return self.consultar_datos()

    @classmethod
    def from_dict(cls, d):
        return cls(d["id_estudiante"], d["nombres"], d["programa"], d["correo"], d.get("aprobadas"))


class Asignatura:
    def __init__(self, codigo, nombre, horario, cupo_total, prerrequisitos=None, cupo_disponible=None):
        # horario: lista de (dia, "HH:MM" inicio, "HH:MM" fin)
        self.__codigo = codigo
        self.__nombre = nombre
        self.__horario = [tuple(b) for b in horario]
        self.__cupo_total = cupo_total
        self.__cupo_disponible = cupo_total if cupo_disponible is None else cupo_disponible
        self.__prerrequisitos = list(prerrequisitos or [])

    @property
    def codigo(self):
        return self.__codigo

    @property
    def nombre(self):
        return self.__nombre

    @property
    def horario(self):
        return list(self.__horario)

    @property
    def cupo_total(self):
        return self.__cupo_total

    @property
    def cupo_disponible(self):
        return self.__cupo_disponible

    @property
    def prerrequisitos(self):
        return list(self.__prerrequisitos)

    def consultar_horario(self):
        return ", ".join(f"{d} {i}-{f}" for d, i, f in self.__horario)

    def verificar_cupo(self):
        return self.__cupo_disponible > 0

    def verificar_requisitos(self, estudiante):
        """Devuelve (cumple, faltantes) según las asignaturas aprobadas."""
        faltantes = [p for p in self.__prerrequisitos if p not in estudiante.aprobadas]
        return (not faltantes, faltantes)

    def cruza_con(self, otra):
        """True si algún bloque de esta asignatura se superpone con otra."""
        for d1, i1, f1 in self.__horario:
            for d2, i2, f2 in otra.horario:
                if d1 == d2 and _a_minutos(i1) < _a_minutos(f2) and _a_minutos(i2) < _a_minutos(f1):
                    return True
        return False

    def ocupar_cupo(self):
        if not self.verificar_cupo():
            raise ErrorMatricula(f"No hay cupos disponibles en {self.__nombre}.")
        self.__cupo_disponible -= 1

    def liberar_cupo(self):
        if self.__cupo_disponible < self.__cupo_total:
            self.__cupo_disponible += 1

    def to_dict(self):
        return {"codigo": self.__codigo, "nombre": self.__nombre, "horario": self.__horario,
                "cupo_total": self.__cupo_total, "cupo_disponible": self.__cupo_disponible,
                "prerrequisitos": self.__prerrequisitos}

    @classmethod
    def from_dict(cls, d):
        return cls(d["codigo"], d["nombre"], d["horario"], d["cupo_total"],
                   d.get("prerrequisitos"), d.get("cupo_disponible"))


class Matricula:
    ACTIVA = "Activa"
    CANCELADA = "Cancelada"

    def __init__(self, id_matricula, estudiante, asignatura, periodo, fecha=None, estado=ACTIVA):
        self.__id_matricula = id_matricula
        self.__estudiante = estudiante
        self.__asignatura = asignatura
        self.__periodo = periodo
        self.__fecha = fecha or datetime.now().strftime("%Y-%m-%d %H:%M")
        self.__estado = estado

    @classmethod
    def matricular(cls, id_matricula, estudiante, asignatura, periodo, matriculas_activas):
        """Valida y crea una matrícula. Lanza ErrorMatricula si no es posible."""
        for m in matriculas_activas:
            if m.asignatura.codigo == asignatura.codigo:
                raise ErrorMatricula(f"Ya estás matriculado en {asignatura.nombre}.")
        cumple, faltantes = asignatura.verificar_requisitos(estudiante)
        if not cumple:
            raise ErrorMatricula(f"Faltan prerrequisitos para {asignatura.nombre}: {', '.join(faltantes)}.")
        for m in matriculas_activas:
            if asignatura.cruza_con(m.asignatura):
                raise ErrorMatricula(f"Conflicto de horario: {asignatura.nombre} se cruza con {m.asignatura.nombre}.")
        asignatura.ocupar_cupo()  # lanza error si no hay cupos
        return cls(id_matricula, estudiante, asignatura, periodo)

    def cancelar(self):
        if self.__estado == self.CANCELADA:
            raise ErrorMatricula("La matrícula ya estaba cancelada.")
        self.__estado = self.CANCELADA
        self.__asignatura.liberar_cupo()

    @property
    def id_matricula(self):
        return self.__id_matricula

    @property
    def estudiante(self):
        return self.__estudiante

    @property
    def asignatura(self):
        return self.__asignatura

    @property
    def periodo(self):
        return self.__periodo

    @property
    def fecha(self):
        return self.__fecha

    @property
    def estado(self):
        return self.__estado

    def esta_activa(self):
        return self.__estado == self.ACTIVA

    def generar_comprobante(self):
        e, a = self.__estudiante, self.__asignatura
        return "\n".join([
            "=" * 52,
            "  FUNDACIÓN ESCUELA TECNOLÓGICA DE NEIVA (FET)",
            "  COMPROBANTE DE MATRÍCULA",
            "=" * 52,
            f"Matrícula N.º : {self.__id_matricula}",
            f"Fecha         : {self.__fecha}",
            f"Periodo       : {self.__periodo}",
            f"Estado        : {self.__estado}",
            "-" * 52,
            f"Estudiante    : {e.nombres} (Doc. {e.id_estudiante})",
            f"Programa      : {e.programa}",
            "-" * 52,
            f"Asignatura    : {a.codigo} - {a.nombre}",
            f"Horario       : {a.consultar_horario()}",
            "=" * 52,
        ])

    def to_dict(self):
        return {"id_matricula": self.__id_matricula, "id_estudiante": self.__estudiante.id_estudiante,
                "codigo_asignatura": self.__asignatura.codigo, "periodo": self.__periodo,
                "fecha": self.__fecha, "estado": self.__estado}

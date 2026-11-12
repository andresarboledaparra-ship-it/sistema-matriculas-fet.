"""Pruebas unitarias. Ejecutar desde la carpeta src con:  python -m unittest -v"""
import tempfile
import unittest
from pathlib import Path

from modelos import Asignatura, ErrorMatricula
from sistema import SistemaMatriculas


def nuevo_sistema():
    s = SistemaMatriculas(archivo=Path(tempfile.mkdtemp()) / "t.json")
    s.cargar()
    s.registrar_estudiante("1001", "Ana Pérez", "Tecnología en Desarrollo de Software", "ana@correo.com")
    s.registrar_estudiante("1002", "Luis Gómez", "Tecnología en Desarrollo de Software", "luis@correo.com")
    s.registrar_estudiante("1003", "Sara Rojas", "Tecnología en Desarrollo de Software", "sara@correo.com", ["PRO101"])
    return s


class PruebasMatricula(unittest.TestCase):
    def test_matricular_descuenta_cupo(self):
        s = nuevo_sistema()
        antes = s.buscar_asignatura("MAT101").cupo_disponible
        s.matricular("1001", "MAT101")
        self.assertEqual(s.buscar_asignatura("MAT101").cupo_disponible, antes - 1)

    def test_sin_cupos(self):
        s = nuevo_sistema()  # PRO101 tiene solo 3 cupos
        s.registrar_estudiante("2001", "A Uno", "Prog", "a@x.com")
        s.registrar_estudiante("2002", "B Dos", "Prog", "b@x.com")
        for doc in ("1001", "1002", "1003"):
            s.matricular(doc, "PRO101")
        with self.assertRaises(ErrorMatricula):
            s.matricular("2001", "PRO101")

    def test_prerrequisito_faltante(self):
        s = nuevo_sistema()
        with self.assertRaisesRegex(ErrorMatricula, "prerrequisitos"):
            s.matricular("1001", "PRO102")

    def test_prerrequisito_cumplido(self):
        s = nuevo_sistema()
        m = s.matricular("1003", "PRO102")
        self.assertTrue(m.esta_activa())

    def test_conflicto_de_horario(self):
        s = nuevo_sistema()
        s.matricular("1001", "PRO101")   # Lunes 08-10
        with self.assertRaisesRegex(ErrorMatricula, "Conflicto de horario"):
            s.matricular("1001", "BD101")  # Lunes 09-11

    def test_sin_conflicto_si_no_se_superponen(self):
        a = Asignatura("X1", "X", [("Lunes", "08:00", "10:00")], 5)
        b = Asignatura("X2", "Y", [("Lunes", "10:00", "12:00")], 5)
        self.assertFalse(a.cruza_con(b))

    def test_no_duplicar_matricula(self):
        s = nuevo_sistema()
        s.matricular("1001", "MAT101")
        with self.assertRaisesRegex(ErrorMatricula, "Ya estás matriculado"):
            s.matricular("1001", "MAT101")

    def test_cancelar_libera_cupo(self):
        s = nuevo_sistema()
        antes = s.buscar_asignatura("MAT101").cupo_disponible
        m = s.matricular("1001", "MAT101")
        s.cancelar(m.id_matricula)
        self.assertEqual(s.buscar_asignatura("MAT101").cupo_disponible, antes)
        self.assertEqual(m.estado, "Cancelada")

    def test_comprobante(self):
        s = nuevo_sistema()
        m = s.matricular("1001", "MAT101")
        texto = s.comprobante(m.id_matricula)
        self.assertIn("Ana Pérez", texto)
        self.assertIn("Matemáticas", texto)

    def test_correo_invalido(self):
        s = nuevo_sistema()
        with self.assertRaises(ErrorMatricula):
            s.registrar_estudiante("3000", "Pedro", "Prog", "correo-malo")

    def test_persistencia(self):
        s = nuevo_sistema()
        s.matricular("1001", "MAT101")
        s.guardar()
        s2 = SistemaMatriculas(archivo=s.archivo)
        s2.cargar()
        self.assertEqual(len(s2.matriculas_de("1001")), 1)
        self.assertEqual(s2.buscar_asignatura("MAT101").cupo_disponible, 39)


if __name__ == "__main__":
    unittest.main()

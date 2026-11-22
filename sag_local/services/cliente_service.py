import datetime
import storage as db
from models.cliente import Cliente
from models.celular import Celular


class ClienteService:
    """CRUD de clientes y celulares en memoria (RF-05, RF-20)."""

    def registrar(
        self,
        nombre: str,
        apellido_paterno: str,
        apellido_materno: str,
        fecha_nacimiento: datetime.date,
        colonia: str,
        calle: str,
        celulares: list[str],
    ) -> int:
        codigo = db.next_id("cliente")
        db.clientes.append({
            "codigo_cliente": codigo,
            "nombre": nombre,
            "apellido_paterno": apellido_paterno,
            "apellido_materno": apellido_materno,
            "fecha_nacimiento": fecha_nacimiento,
            "colonia": colonia,
            "calle": calle,
            "estado": True,
        })
        for numero in celulares:
            cid = db.next_id("celular")
            db.celulares.append({"codigo_celular": cid, "numero": numero, "codigo_cliente": codigo})
        return codigo

    def buscar(self, termino: str) -> list[Cliente]:
        termino_l = termino.lower()
        # Celulares que coincidan exactamente
        clientes_por_cel = {
            c["codigo_cliente"]
            for c in db.celulares
            if c["numero"] == termino
        }
        resultado = []
        vistos = set()
        for r in db.clientes:
            coincide = (
                termino_l in r["nombre"].lower()
                or termino_l in r["apellido_paterno"].lower()
                or r["codigo_cliente"] in clientes_por_cel
            )
            if coincide and r["codigo_cliente"] not in vistos:
                vistos.add(r["codigo_cliente"])
                resultado.append(self._row_to_cliente(r))
        return resultado

    def obtener_por_id(self, codigo_cliente: int) -> Cliente | None:
        row = next((c for c in db.clientes if c["codigo_cliente"] == codigo_cliente), None)
        return self._row_to_cliente(row) if row else None

    def editar(self, codigo_cliente: int, **campos) -> None:
        for c in db.clientes:
            if c["codigo_cliente"] == codigo_cliente:
                c.update(campos)
                return

    def cambiar_estado(self, codigo_cliente: int, estado: bool) -> None:
        self.editar(codigo_cliente, estado=estado)

    def listar_celulares(self, codigo_cliente: int) -> list[Celular]:
        return [
            Celular(c["codigo_celular"], c["numero"], c["codigo_cliente"])
            for c in db.celulares
            if c["codigo_cliente"] == codigo_cliente
        ]

    def agregar_celular(self, numero: str, codigo_cliente: int) -> None:
        cid = db.next_id("celular")
        db.celulares.append({"codigo_celular": cid, "numero": numero, "codigo_cliente": codigo_cliente})

    # ------------------------------------------------------------------
    @staticmethod
    def _row_to_cliente(row: dict) -> Cliente:
        return Cliente(
            codigo_cliente=row["codigo_cliente"],
            nombre=row["nombre"],
            apellido_paterno=row["apellido_paterno"],
            apellido_materno=row["apellido_materno"],
            fecha_nacimiento=row["fecha_nacimiento"],
            colonia=row["colonia"],
            calle=row["calle"],
            estado=row["estado"],
        )

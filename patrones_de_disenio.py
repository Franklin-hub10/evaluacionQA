# -*- coding: utf-8 -*-
# ejercicio_3_minimal_claro.py
"""
Sistema de gestión de usuarios con 3 patrones:
1) Singleton  -> una sola "BD" en memoria (diccionario compartido).
2) Adapter    -> misma interfaz de login para usuario o email.
3) Strategy   -> políticas de contraseña (débil, media, fuerte) intercambiables.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, Protocol

# ===========================
# 1) SINGLETON: "BD" única
# ===========================
class DBConnection:
    _instance: Optional["DBConnection"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._usuarios: Dict[str, Dict[str, Any]] = {}   # {username: {"email":..., "password":...}}
            cls._instance._index_email: Dict[str, str] = {}           # {email: username}
        return cls._instance

    # CRUD mínimo
    def create_user(self, username: str, email: str, password: str) -> bool:
        if username in self._usuarios or email in self._index_email:
            return False
        self._usuarios[username] = {"email": email, "password": password}
        self._index_email[email] = username
        return True

    def get_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        return self._usuarios.get(username)

    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        uname = self._index_email.get(email)
        return self._usuarios.get(uname) if uname else None

    def list_users(self):
        return [{"username": u, **rec} for u, rec in self._usuarios.items()]

# ===========================
# 2) STRATEGY: políticas de contraseña
# ===========================
class PasswordPolicy(Protocol):
    def is_valid(self, password: str) -> bool: ...
    def name(self) -> str: ...

class WeakPolicy:
    def is_valid(self, p: str) -> bool: return len(p) >= 4
    def name(self) -> str: return "Débil (>=4)"

class MediumPolicy:
    def is_valid(self, p: str) -> bool:
        if len(p) < 6: return False
        return any(c.isdigit() for c in p) and any(c.isalpha() for c in p)
    def name(self) -> str: return "Media (>=6, letras y número)"

class StrongPolicy:
    def is_valid(self, p: str) -> bool:
        if len(p) < 8: return False
        has_low = any(c.islower() for c in p)
        has_up  = any(c.isupper() for c in p)
        has_num = any(c.isdigit() for c in p)
        has_sym = any(not c.isalnum() for c in p)
        return has_low and has_up and has_num and has_sym
    def name(self) -> str: return "Fuerte (>=8, min/mayus, número, símbolo)"

# ===========================
# 3) ADAPTER: autenticación unificada
# ===========================
class AuthProvider(Protocol):
    def authenticate(self, identifier: str, password: str) -> bool: ...

class UsernameAuth:
    """Autentica con: identifier = username"""
    def __init__(self, db: DBConnection): self.db = db
    def authenticate(self, username: str, password: str) -> bool:
        u = self.db.get_by_username(username)
        return bool(u and u["password"] == password)

class EmailAuthSystem:
    """Sistema 'legado' que autentica con email (firma distinta)."""
    def __init__(self, db: DBConnection): self.db = db
    def login_with_email(self, email: str, pwd: str) -> bool:
        u = self.db.get_by_email(email)
        return bool(u and u["password"] == pwd)

class EmailAuthAdapter:
    """Expone authenticate(identifier, password) usando EmailAuthSystem."""
    def __init__(self, legacy: EmailAuthSystem): self.legacy = legacy
    def authenticate(self, email: str, password: str) -> bool:
        return self.legacy.login_with_email(email, password)

# ===========================
# Gestor de usuarios
# ===========================
@dataclass
class User:
    username: str
    email: str
    password: str

class UserManager:
    def __init__(self, db: DBConnection, policy: PasswordPolicy, auth: AuthProvider):
        self.db = db
        self.policy = policy
        self.auth = auth

    def set_policy(self, policy: PasswordPolicy): self.policy = policy
    def set_auth(self, auth: AuthProvider): self.auth = auth

    def register(self, user: User) -> bool:
        if not self.policy.is_valid(user.password):  # VALIDACIÓN via STRATEGY
            return False
        return self.db.create_user(user.username, user.email, user.password)  # GUARDA en SINGLETON

    def login(self, identifier: str, password: str) -> bool:
        return self.auth.authenticate(identifier, password)  # USA el PROVIDER (USERNAME o EMAIL via ADAPTER)

# ===========================
# Demo MUY clara en consola
# ===========================
def linea(): print("-"*70)
def titulo(t): linea(); print(t); linea()
def fila(*cols, widths=(18, 22, 22, 6)):  # tablita simple
    fmt = f"{{:<{widths[0]}}}{{:<{widths[1]}}}{{:<{widths[2]}}}{{:<{widths[3]}}}"
    print(fmt.format(*cols))

if __name__ == "__main__":
    db = DBConnection()                       # SINGLETON
    policy = StrongPolicy()                   # STRATEGY inicial
    um = UserManager(db, policy, UsernameAuth(db))  # AUTH por username

    # Usuarios de ejemplo
    alice = User("alice", "alice@site.com", "S3guro!2025")  # fuerte (debe pasar)
    bob   = User("bob",   "bob@site.com",   "bob123")       # NO pasa en fuerte
    carl  = User("carl",  "carl@site.com",  "F0rte#Key")    # fuerte (debe pasar)

    titulo("1) Registro con política FUERTE")
    fila("Usuario", "Email", "Contraseña", "OK")
    fila(alice.username, alice.email, alice.password, "✔" if um.register(alice) else "✘")
    fila(bob.username,   bob.email,   bob.password,   "✔" if um.register(bob)   else "✘")
    fila(carl.username,  carl.email,  carl.password,  "✔" if um.register(carl)  else "✘")

    titulo("2) Usuarios existentes en la BD (Singleton compartida)")
    for u in db.list_users():
        print(f"- {u['username']}  |  {u['email']}  |  (pass guardada)")

    titulo("3) Login por NOMBRE DE USUARIO (UsernameAuth)")
    print("alice / correcto  ->", um.login("alice", "S3guro!2025"))
    print("alice / incorrecto->", um.login("alice", "malaPass"))
    print("carl  / correcto  ->", um.login("carl",  "F0rte#Key"))

    titulo("4) Cambio a LOGIN por EMAIL (Adapter)")
    um.set_auth(EmailAuthAdapter(EmailAuthSystem(db)))
    print("alice@site.com / correcto  ->", um.login("alice@site.com", "S3guro!2025"))
    print("bob@site.com   / intento   ->", um.login("bob@site.com",   "bob123"))  # no registrado antes

    titulo("5) Cambio de política a MEDIA y reintento registro de 'bob'")
    um.set_policy(MediumPolicy())
    print("Política actual:", um.policy.name())
    print("Registro bob con política MEDIA ->", um.register(bob))

    titulo("6) Usuarios en BD (final)")
    for u in db.list_users():
        print(f"- {u['username']}  |  {u['email']}")

    linea()
    print("FIN DEMO — Patrones aplicados: Singleton + Adapter + Strategy")
    linea()

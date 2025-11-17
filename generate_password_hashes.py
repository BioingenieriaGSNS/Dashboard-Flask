"""
Script para generar hashes de contraseñas iniciales
Ejecuta este script para obtener los hashes correctos para tus usuarios iniciales
"""

from werkzeug.security import generate_password_hash

# Definir usuarios iniciales
usuarios_iniciales = [
    {
        'username': 'admin',
        'email': 'admin@syemed.com',
        'password': 'Admin123!',  # CAMBIAR después del primer login
        'role': 'admin'
    },
    {
        'username': 'viewer',
        'email': 'viewer@syemed.com',
        'password': 'Viewer123!',
        'role': 'viewer'
    },
    {
        'username': 'editor',
        'email': 'editor@syemed.com',
        'password': 'Editor123!',
        'role': 'editor'
    }
]

print("=" * 80)
print("HASHES DE CONTRASEÑAS PARA USUARIOS INICIALES")
print("=" * 80)
print("\nCopia estos INSERT statements en tu base de datos Neon:\n")

for user in usuarios_iniciales:
    password_hash = generate_password_hash(user['password'])
    
    print(f"\n-- Usuario: {user['username']} (Password: {user['password']})")
    print(f"INSERT INTO usuarios (username, email, password_hash, role, activo)")
    print(f"VALUES (")
    print(f"    '{user['username']}',")
    print(f"    '{user['email']}',")
    print(f"    '{password_hash}',")
    print(f"    '{user['role']}',")
    print(f"    true")
    print(f");")

print("\n" + "=" * 80)
print("⚠️  IMPORTANTE: Cambia las contraseñas después del primer login")
print("=" * 80)

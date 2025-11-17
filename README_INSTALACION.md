# 🔐 Sistema de Autenticación para Dashboard Syemed

## 📋 Descripción

Sistema de autenticación completo con 3 roles de usuario:
- **👁️ Viewer (Visualizador)**: Solo lectura, puede ver toda la información
- **✏️ Editor**: Puede ver y editar información
- **👑 Admin (Administrador)**: Acceso completo + gestión de usuarios

## 🚀 Instalación Rápida

### Paso 1: Instalar Dependencias

```bash
pip install flask flask-login werkzeug psycopg2-binary python-dotenv
```

### Paso 2: Configurar la Base de Datos

1. **Conéctate a tu base de datos Neon** y ejecuta el script SQL:

```sql
-- Crear tabla de usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('viewer', 'editor', 'admin')),
    activo BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Crear índices
CREATE INDEX idx_usuarios_username ON usuarios(username);
CREATE INDEX idx_usuarios_email ON usuarios(email);
CREATE INDEX idx_usuarios_activo ON usuarios(activo);
```

2. **Genera los hashes de contraseñas** ejecutando:

```bash
python generate_password_hashes.py
```

Este script te mostrará los INSERT statements con los hashes correctos. Cópialos y ejecútalos en tu base de datos Neon.

### Paso 3: Actualizar Variables de Entorno

Añade a tu archivo `.env`:

```env
DATABASE_URL=tu_connection_string_de_neon
SECRET_KEY=genera-una-clave-secreta-random-aqui-123456
```

**⚠️ IMPORTANTE:** Genera una SECRET_KEY segura en producción. Puedes usar:

```python
import secrets
print(secrets.token_hex(32))
```

### Paso 4: Actualizar tu Conexión en auth.py

Abre `auth.py` y actualiza la función `get_db_connection()` para usar tu configuración:

```python
def get_db_connection():
    """Obtiene conexión a la base de datos"""
    # Opción 1: Usar os.getenv (recomendado)
    DATABASE_URL = os.getenv('DATABASE_URL')
    db_url_clean = DATABASE_URL.replace('&channel_binding=require', '')
    conn = psycopg2.connect(db_url_clean, cursor_factory=RealDictCursor)
    return conn
```

### Paso 5: Reemplazar Archivos

1. **Reemplaza `app.py`** con `app_with_auth.py`
2. **Reemplaza `templates/base.html`** con `base_with_auth.html`
3. **Añade** `templates/login.html` (nuevo archivo)
4. **Añade** `templates/usuarios.html` (nuevo archivo)
5. **Añade** `auth.py` en el directorio raíz

### Paso 6: Estructura de Archivos

Tu proyecto debería verse así:

```
tu-proyecto/
│
├── app.py                          # ← Reemplazar con app_with_auth.py
├── auth.py                         # ← Nuevo archivo
├── generate_password_hashes.py     # ← Script auxiliar
├── .env                            # ← Actualizar con SECRET_KEY
│
└── templates/
    ├── base.html                   # ← Reemplazar con base_with_auth.html
    ├── login.html                  # ← Nuevo archivo
    ├── usuarios.html               # ← Nuevo archivo
    ├── dashboard.html              # (sin cambios)
    ├── solicitudes.html            # (sin cambios)
    ├── equipos.html                # (sin cambios)
    └── archivos.html               # (sin cambios)
```

## 👤 Usuarios Iniciales

Después de ejecutar `generate_password_hashes.py` y los INSERT statements, tendrás:

| Username | Password    | Rol          | Email             |
|----------|-------------|--------------|-------------------|
| admin    | Admin123!   | Administrador| admin@syemed.com  |
| editor   | Editor123!  | Editor       | editor@syemed.com |
| viewer   | Viewer123!  | Visualizador | viewer@syemed.com |

**⚠️ CAMBIA ESTAS CONTRASEÑAS** inmediatamente después del primer login.

## 🔒 Cómo Funciona

### Flujo de Autenticación

1. Usuario accede a cualquier ruta → Redirige a `/login` si no está autenticado
2. Usuario ingresa credenciales en `/login`
3. Sistema valida contra base de datos
4. Si es válido → Crea sesión y redirige al dashboard
5. Usuario navega con su rol específico
6. Al cerrar sesión → Redirige a `/login`

### Permisos por Rol

| Acción                    | Viewer | Editor | Admin |
|---------------------------|--------|--------|-------|
| Ver información           | ✅     | ✅     | ✅    |
| Editar equipos/solicitudes| ❌     | ✅     | ✅    |
| Crear equipos             | ❌     | ✅     | ✅    |
| Eliminar registros        | ❌     | ❌     | ✅    |
| Gestionar usuarios        | ❌     | ❌     | ✅    |

### Protección de Rutas

El sistema protege automáticamente:
- Todas las páginas requieren login (`@login_required`)
- Edición de datos requiere rol Editor o Admin (`@permission_required('edit')`)
- Gestión de usuarios solo para Admin (`@permission_required('manage_users')`)

## 🎨 Funcionalidades del Panel de Admin

Los administradores pueden:
- ➕ Crear nuevos usuarios
- 🔧 Cambiar roles de usuarios existentes
- 🔑 Cambiar contraseñas de usuarios
- 🚫 Activar/Desactivar usuarios
- 👁️ Ver estadísticas de último login

## 🔐 Seguridad Implementada

✅ Contraseñas hasheadas con Werkzeug (scrypt)
✅ Sesiones seguras con Flask-Login
✅ Control de acceso por roles
✅ Protección CSRF automática
✅ Usuarios inactivos no pueden hacer login
✅ Seguimiento de último login

## 🛠️ Administración de Usuarios

### Crear Usuario Nuevo (desde código)

```python
from auth import create_user

# Crear usuario
user_id = create_user(
    username='nuevo_usuario',
    email='usuario@syemed.com',
    password='ContraseñaSegura123!',
    role='editor'  # viewer, editor, o admin
)
```

### Cambiar Rol de Usuario

```python
from auth import update_user_role

update_user_role(user_id=5, new_role='admin')
```

### Cambiar Contraseña

```python
from auth import update_user_password

update_user_password(user_id=5, new_password='NuevaContraseña123!')
```

### Desactivar Usuario

```python
from auth import toggle_user_status

toggle_user_status(user_id=5)  # Alterna entre activo/inactivo
```

## 🔄 Migración desde tu App Actual

1. **Backup**: Haz backup de tu `app.py` actual
2. **Importa auth.py**: El módulo de autenticación es independiente
3. **Reemplaza app.py**: Usa `app_with_auth.py` que incluye toda tu lógica actual + autenticación
4. **Actualiza templates**: Solo necesitas actualizar `base.html` para mostrar info del usuario
5. **Prueba**: Todo debería seguir funcionando, pero ahora con login

## 🚨 Solución de Problemas

### Error: "No module named 'flask_login'"
```bash
pip install flask-login
```

### Error: "scrypt hash could not be decoded"
- Regenera los hashes ejecutando `generate_password_hashes.py`
- Copia los nuevos INSERT statements a tu BD

### Error: "SECRET_KEY not found"
- Añade `SECRET_KEY` a tu archivo `.env`
- Nunca uses la misma SECRET_KEY en desarrollo y producción

### Error de conexión a la base de datos
- Verifica que tu `DATABASE_URL` en `.env` sea correcta
- Asegúrate de que la tabla `usuarios` existe
- Comprueba que puedes conectarte a Neon desde tu terminal

## 📝 Personalización

### Cambiar la duración de la sesión

En `app.py`:

```python
from datetime import timedelta

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
```

### Agregar más roles

En `auth.py`, modifica el diccionario `ROLES`:

```python
ROLES = {
    'viewer': {
        'name': 'Visualizador',
        'permissions': ['view']
    },
    'supervisor': {  # Nuevo rol
        'name': 'Supervisor',
        'permissions': ['view', 'edit', 'approve']
    },
    # ... otros roles
}
```

## 🎯 Próximos Pasos Recomendados

1. **Cambiar contraseñas** de los usuarios iniciales
2. **Crear usuarios reales** desde el panel de admin
3. **Eliminar usuarios de ejemplo** si no los necesitas
4. **Configurar SECRET_KEY única** para producción
5. **Implementar recuperación de contraseña** (opcional)
6. **Agregar 2FA** (opcional, más avanzado)

## ✅ Checklist de Implementación

- [ ] Instalar dependencias (`pip install -r requirements.txt`)
- [ ] Crear tabla `usuarios` en Neon
- [ ] Ejecutar `generate_password_hashes.py`
- [ ] Insertar usuarios iniciales en BD
- [ ] Actualizar `.env` con SECRET_KEY
- [ ] Reemplazar archivos según instrucciones
- [ ] Probar login con usuario admin
- [ ] Cambiar contraseñas iniciales
- [ ] Crear usuarios reales
- [ ] Verificar permisos por rol

## 📧 Soporte

Si tienes problemas:
1. Verifica que todos los archivos estén en su lugar
2. Revisa los logs de Flask para errores específicos
3. Asegúrate de que la tabla de usuarios existe en Neon
4. Verifica que los hashes de contraseña sean correctos

---

**¡Listo! 🎉** Tu dashboard ahora tiene autenticación segura con control de acceso por roles.

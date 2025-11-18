#!/usr/bin/env python3
"""
Script de Pruebas - Sistema de Permisos y Auditoría
Verifica que la implementación esté correcta

Ejecutar: python test_implementacion.py
"""

import os
import sys

def print_header(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_check(message, status):
    icon = "✅" if status else "❌"
    print(f"{icon} {message}")

def test_archivos():
    """Verifica que todos los archivos necesarios existan"""
    print_header("1. VERIFICACIÓN DE ARCHIVOS")
    
    archivos_requeridos = {
        'auth.py': 'Sistema de autenticación',
        'app.py': 'Aplicación principal',
        'templates/base.html': 'Template base',
        'templates/usuarios.html': 'Gestión de usuarios',
        'templates/auditoria.html': 'Vista de auditoría',
        'templates/equipos.html': 'Gestión de equipos',
        'create_audit_table.sql': 'Script SQL de auditoría'
    }
    
    todos_ok = True
    for archivo, descripcion in archivos_requeridos.items():
        existe = os.path.exists(archivo)
        print_check(f"{descripcion}: {archivo}", existe)
        if not existe:
            todos_ok = False
    
    return todos_ok

def test_auth_py():
    """Verifica que auth.py tenga los roles correctos"""
    print_header("2. VERIFICACIÓN DE auth.py")
    
    try:
        with open('auth.py', 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Verificar roles
        roles_requeridos = ['viewer', 'editor_v2', 'editor', 'admin']
        roles_ok = all(f"'{rol}'" in contenido for rol in roles_requeridos)
        print_check("Roles viewer, editor_v2, editor, admin definidos", roles_ok)
        
        # Verificar permisos
        permisos = ['view', 'edit', 'delete', 'manage_users', 'view_audit']
        permisos_ok = all(f"'{permiso}'" in contenido for permiso in permisos)
        print_check("Permisos básicos definidos", permisos_ok)
        
        return roles_ok and permisos_ok
    except Exception as e:
        print_check(f"Error al leer auth.py: {e}", False)
        return False

def test_app_py():
    """Verifica que app.py tenga las funciones necesarias"""
    print_header("3. VERIFICACIÓN DE app.py")
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Verificar función de auditoría
        tiene_auditoria = 'def registrar_auditoria' in contenido
        print_check("Función registrar_auditoria() existe", tiene_auditoria)
        
        # Verificar ruta de auditoría
        tiene_ruta_auditoria = "@app.route('/auditoria')" in contenido
        print_check("Ruta /auditoria definida", tiene_ruta_auditoria)
        
        # Verificar API DELETE
        tiene_delete = "methods=['DELETE']" in contenido and 'delete_equipo' in contenido
        print_check("API DELETE para equipos existe", tiene_delete)
        
        # Verificar permission_required en UPDATE
        tiene_permisos_update = "@permission_required('edit')" in contenido
        print_check("Decorador @permission_required en rutas", tiene_permisos_update)
        
        return tiene_auditoria and tiene_ruta_auditoria and tiene_delete and tiene_permisos_update
    except Exception as e:
        print_check(f"Error al leer app.py: {e}", False)
        return False

def test_templates():
    """Verifica que los templates tengan las modificaciones necesarias"""
    print_header("4. VERIFICACIÓN DE TEMPLATES")
    
    templates_ok = True
    
    # base.html
    try:
        with open('templates/base.html', 'r', encoding='utf-8') as f:
            base_content = f.read()
        
        tiene_menu_auditoria = "url_for('auditoria')" in base_content
        print_check("base.html tiene enlace a Auditoría", tiene_menu_auditoria)
        templates_ok = templates_ok and tiene_menu_auditoria
    except:
        print_check("Error al verificar base.html", False)
        templates_ok = False
    
    # usuarios.html
    try:
        with open('templates/usuarios.html', 'r', encoding='utf-8') as f:
            usuarios_content = f.read()
        
        tiene_editor_v2 = 'editor_v2' in usuarios_content
        print_check("usuarios.html incluye rol editor_v2", tiene_editor_v2)
        templates_ok = templates_ok and tiene_editor_v2
    except:
        print_check("Error al verificar usuarios.html", False)
        templates_ok = False
    
    # auditoria.html
    existe_auditoria = os.path.exists('templates/auditoria.html')
    print_check("auditoria.html existe", existe_auditoria)
    templates_ok = templates_ok and existe_auditoria
    
    # equipos.html
    try:
        with open('templates/equipos.html', 'r', encoding='utf-8') as f:
            equipos_content = f.read()
        
        tiene_permisos_js = 'userPermissions' in equipos_content
        print_check("equipos.html tiene variables de permisos JS", tiene_permisos_js)
        
        tiene_funcion_eliminar = 'eliminarEquipo' in equipos_content
        print_check("equipos.html tiene función eliminarEquipo()", tiene_funcion_eliminar)
        
        tiene_condicional_edit = "current_user.has_permission('edit')" in equipos_content
        print_check("equipos.html verifica permisos en template", tiene_condicional_edit)
        
        templates_ok = templates_ok and tiene_permisos_js and tiene_funcion_eliminar and tiene_condicional_edit
    except:
        print_check("Error al verificar equipos.html", False)
        templates_ok = False
    
    return templates_ok

def test_sql():
    """Verifica que el script SQL esté correcto"""
    print_header("5. VERIFICACIÓN DE SQL")
    
    try:
        with open('create_audit_table.sql', 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        tiene_tabla = 'CREATE TABLE' in sql_content and 'equipos_auditoria' in sql_content
        print_check("Script crea tabla equipos_auditoria", tiene_tabla)
        
        tiene_indices = 'CREATE INDEX' in sql_content
        print_check("Script crea índices", tiene_indices)
        
        tiene_campos = all(campo in sql_content for campo in [
            'equipo_id', 'usuario_id', 'usuario_nombre', 
            'campo_modificado', 'valor_anterior', 'valor_nuevo', 'fecha_cambio'
        ])
        print_check("Todos los campos necesarios están definidos", tiene_campos)
        
        return tiene_tabla and tiene_indices and tiene_campos
    except Exception as e:
        print_check(f"Error al leer SQL: {e}", False)
        return False

def generar_reporte(resultados):
    """Genera un reporte final de la verificación"""
    print_header("RESUMEN DE VERIFICACIÓN")
    
    total = len(resultados)
    aprobados = sum(resultados.values())
    porcentaje = (aprobados / total * 100) if total > 0 else 0
    
    print(f"\nPruebas ejecutadas: {total}")
    print(f"Pruebas aprobadas: {aprobados}")
    print(f"Pruebas fallidas: {total - aprobados}")
    print(f"Porcentaje: {porcentaje:.1f}%")
    
    if porcentaje == 100:
        print("\n✅ ¡TODAS LAS VERIFICACIONES PASARON!")
        print("Tu implementación está lista para usarse.")
    elif porcentaje >= 80:
        print("\n⚠️ MAYORÍA DE VERIFICACIONES PASARON")
        print("Revisa las pruebas fallidas y corrige los problemas.")
    else:
        print("\n❌ VARIAS VERIFICACIONES FALLARON")
        print("Por favor revisa la implementación siguiendo el README.")
    
    print("\n" + "="*60)
    print("\n📋 PRÓXIMOS PASOS:")
    print("1. Corrige cualquier prueba fallida")
    print("2. Ejecuta create_audit_table.sql en la base de datos")
    print("3. Reinicia la aplicación")
    print("4. Prueba con diferentes roles de usuario")
    print("5. Verifica que la auditoría registre cambios")
    print("\n" + "="*60)

def main():
    print("\n" + "🚀 "*20)
    print("   VERIFICACIÓN DE IMPLEMENTACIÓN - SISTEMA DE PERMISOS")
    print("🚀 "*20)
    
    resultados = {
        'Archivos': test_archivos(),
        'auth.py': test_auth_py(),
        'app.py': test_app_py(),
        'Templates': test_templates(),
        'SQL': test_sql()
    }
    
    generar_reporte(resultados)
    
    # Código de salida
    sys.exit(0 if all(resultados.values()) else 1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Verificación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error inesperado: {e}")
        sys.exit(1)

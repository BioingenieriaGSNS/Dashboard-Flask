# 🚀 MEGA-GUÍA COMPLETA - CÓDIGO Y PASOS

## 📋 TABLA DE CONTENIDOS
1. [Paso 1: Base de Datos](#paso-1-base-de-datos)
2. [Paso 2: Archivos a Reemplazar](#paso-2-archivos-a-reemplazar)
3. [Paso 3: Modificar equipos.html](#paso-3-modificar-equiposhtml)
4. [Paso 4: Verificar](#paso-4-verificar)

---

# PASO 1: BASE DE DATOS

## Ejecutar este SQL en PostgreSQL:

```sql
-- Tabla de auditoría para registrar cambios en equipos
CREATE TABLE IF NOT EXISTS equipos_auditoria (
    id SERIAL PRIMARY KEY,
    equipo_id INTEGER NOT NULL REFERENCES equipos(id) ON DELETE CASCADE,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
    usuario_nombre VARCHAR(100) NOT NULL,
    campo_modificado VARCHAR(100) NOT NULL,
    valor_anterior TEXT,
    valor_nuevo TEXT,
    fecha_cambio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    accion VARCHAR(20) DEFAULT 'UPDATE'
);

-- Índices para mejorar el rendimiento
CREATE INDEX IF NOT EXISTS idx_equipos_auditoria_equipo ON equipos_auditoria(equipo_id);
CREATE INDEX IF NOT EXISTS idx_equipos_auditoria_usuario ON equipos_auditoria(usuario_id);
CREATE INDEX IF NOT EXISTS idx_equipos_auditoria_fecha ON equipos_auditoria(fecha_cambio);

-- Comentario en la tabla
COMMENT ON TABLE equipos_auditoria IS 'Registro de auditoría de todos los cambios realizados en la tabla equipos';
```

---

# PASO 2: ARCHIVOS A REEMPLAZAR

Ya tienes estos archivos listos en /outputs:
- ✅ auth.py (REEMPLAZAR)
- ✅ app.py (REEMPLAZAR)
- ✅ base.html (REEMPLAZAR en templates/)
- ✅ usuarios.html (REEMPLAZAR en templates/)
- ✅ auditoria.html (AGREGAR NUEVO en templates/)

---

# PASO 3: MODIFICAR EQUIPOS.HTML

## 🎨 PARTE 1: Agregar estos ESTILOS CSS

Busca la sección `<style>` en equipos.html (línea ~6-300) y agrega AL FINAL de los estilos:

```css
/* ==================== ESTILOS NUEVOS PARA PERMISOS ==================== */

/* Botón de eliminar */
.btn-delete {
    background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);
    color: white;
    border: none;
    padding: 0.5rem 0.75rem;
    border-radius: 6px;
    cursor: pointer;
    font-size: 1.2rem;
    transition: all 0.3s;
    box-shadow: 0 2px 8px rgba(244, 67, 54, 0.3);
}

.btn-delete:hover {
    background: linear-gradient(135deg, #d32f2f 0%, #c62828 100%);
    transform: scale(1.1);
    box-shadow: 0 4px 12px rgba(244, 67, 54, 0.5);
}

.btn-delete:active {
    transform: scale(0.95);
}

/* Estilo general para botones de acción */
.btn-action {
    border: none;
    padding: 0.5rem 0.75rem;
    border-radius: 6px;
    cursor: pointer;
    font-size: 1.2rem;
    transition: all 0.3s;
    margin: 0 0.2rem;
}

/* Botón de guardar mejorado */
.btn-save {
    background: linear-gradient(135deg, #4caf50 0%, #45a049 100%);
    color: white;
    box-shadow: 0 2px 8px rgba(76, 175, 80, 0.3);
}

.btn-save:hover {
    background: linear-gradient(135deg, #45a049 0%, #3d8b40 100%);
    transform: scale(1.1);
    box-shadow: 0 4px 12px rgba(76, 175, 80, 0.5);
}

.btn-save:active {
    transform: scale(0.95);
}

/* Fila modificada (cambios no guardados) */
.data-row.modified {
    border-left: 4px solid #ff9800 !important;
}

/* Indicador de cambios no guardados */
@keyframes slideIn {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

/* Celda no editable (viewer) */
.cell.non-editable {
    cursor: default !important;
    background-color: #fafafa !important;
}

.cell.non-editable:hover {
    background-color: #f5f5f5 !important;
}
```

## 📝 PARTE 2: Modificar COLUMNA DE ACCIONES

Busca donde se genera la columna de acciones (dentro del loop `{% for equipo in equipos %}`).

**BUSCAR ESTO:**
```html
<div class="cell ch-acciones">
    <button onclick="guardarCambios({{ equipo.id }})">💾</button>
</div>
```

**REEMPLAZAR CON ESTO:**
```html
<div class="cell ch-acciones" style="justify-content: center; gap: 0.5rem; display: flex; align-items: center;">
    {% if current_user.has_permission('edit') %}
    <button class="btn-action btn-save" 
            onclick="guardarCambios({{ equipo.id }})" 
            title="Guardar cambios">
        💾
    </button>
    {% endif %}
    
    {% if current_user.has_permission('delete') %}
    <button class="btn-action btn-delete" 
            onclick="eliminarEquipo({{ equipo.id }}, '{{ equipo.ost }}')" 
            title="Eliminar equipo">
        🗑️
    </button>
    {% endif %}
    
    {% if not current_user.has_permission('edit') and not current_user.has_permission('delete') %}
    <span style="color: #999; font-size: 0.85rem;">👁️ Solo lectura</span>
    {% endif %}
</div>
```

## ✏️ PARTE 3: Modificar CELDAS EDITABLES

**IMPORTANTE:** Debes modificar TODAS las celdas con `class="editable"`.

**BUSCAR ESTO** (ejemplo con cliente):
```html
<div class="cell editable" contenteditable="true" data-field="cliente">
    {{ equipo.cliente }}
</div>
```

**REEMPLAZAR CON ESTO:**
```html
<div class="cell {% if current_user.has_permission('edit') %}editable{% endif %}" 
     {% if current_user.has_permission('edit') %}contenteditable="true"{% endif %}
     {% if not current_user.has_permission('edit') %}style="cursor: default; background-color: #fafafa;"{% endif %}
     data-field="cliente">
    {{ equipo.cliente }}
</div>
```

**Aplicar este cambio a TODAS estas celdas:**
- cliente
- tipo_equipo
- marca
- modelo
- numero_serie
- accesorios
- observacion_ingreso
- detalle_reparacion
- horas_trabajo
- informe_tecnico
- costo_reparacion
- precio_cliente
- numero_ov
- remito
- remito_entrega

## 🔧 PARTE 4: Modificar SELECTS (estado, prioridad, etc)

**BUSCAR ESTO:**
```html
<div class="cell editable-select" data-field="estado" onclick="mostrarSelectEstado(this, {{ equipo.id }})">
    {{ equipo.estado }}
</div>
```

**REEMPLAZAR CON ESTO:**
```html
<div class="cell {% if current_user.has_permission('edit') %}editable-select{% endif %}" 
     data-field="estado" 
     {% if current_user.has_permission('edit') %}onclick="mostrarSelectEstado(this, {{ equipo.id }})"{% endif %}
     {% if not current_user.has_permission('edit') %}style="cursor: default; background-color: #fafafa;"{% endif %}>
    {{ equipo.estado }}
</div>
```

**Aplicar a:** estado, prioridad, reingreso, estado_ov

## 📅 PARTE 5: Modificar FECHAS

**BUSCAR ESTO:**
```html
<div class="cell editable-date" data-field="fecha_ingreso" onclick="mostrarInputFecha(this, {{ equipo.id }})">
    {{ equipo.fecha_ingreso.strftime('%d/%m/%Y') if equipo.fecha_ingreso else 'N/A' }}
</div>
```

**REEMPLAZAR CON ESTO:**
```html
<div class="cell {% if current_user.has_permission('edit') %}editable-date{% endif %}" 
     data-field="fecha_ingreso" 
     {% if current_user.has_permission('edit') %}onclick="mostrarInputFecha(this, {{ equipo.id }})"{% endif %}
     {% if not current_user.has_permission('edit') %}style="cursor: default; background-color: #fafafa;"{% endif %}>
    {{ equipo.fecha_ingreso.strftime('%d/%m/%Y') if equipo.fecha_ingreso else 'N/A' }}
</div>
```

**Aplicar a:** fecha_ingreso, fecha_envio_proveedor, fecha_entrega

## 💰 PARTE 6: Modificar DINERO

**BUSCAR ESTO:**
```html
<div class="cell editable-money" data-field="precio_cliente" onclick="mostrarInputDinero(this, {{ equipo.id }})">
    {{ '${:,.2f}'.format(equipo.precio_cliente) if equipo.precio_cliente else 'N/A' }}
</div>
```

**REEMPLAZAR CON ESTO:**
```html
<div class="cell {% if current_user.has_permission('edit') %}editable-money{% endif %}" 
     data-field="precio_cliente" 
     {% if current_user.has_permission('edit') %}onclick="mostrarInputDinero(this, {{ equipo.id }})"{% endif %}
     {% if not current_user.has_permission('edit') %}style="cursor: default; background-color: #fafafa;"{% endif %}>
    {{ '${:,.2f}'.format(equipo.precio_cliente) if equipo.precio_cliente else 'N/A' }}
</div>
```

**Aplicar a:** precio_cliente, costo_reparacion

---

## 💻 PARTE 7: AGREGAR TODO ESTE JAVASCRIPT

**UBICACIÓN:** Al final del archivo equipos.html, dentro del bloque `<script>` existente (antes del `</script>` final).

**COPIAR Y PEGAR TODO ESTE CÓDIGO:**

```javascript
// ==================== CÓDIGO DE PERMISOS Y AUDITORÍA ====================

// 1. VARIABLES DE PERMISOS
const userPermissions = {
    canEdit: {{ 'true' if current_user.has_permission('edit') else 'false' }},
    canDelete: {{ 'true' if current_user.has_permission('delete') else 'false' }},
    isViewer: {{ 'true' if current_user.role == 'viewer' else 'false' }}
};

console.log('🔐 Permisos del usuario:', userPermissions);

// Deshabilitar edición para viewers
document.addEventListener('DOMContentLoaded', function() {
    if (userPermissions.isViewer) {
        document.querySelectorAll('.editable').forEach(cell => {
            cell.removeAttribute('contenteditable');
            cell.style.cursor = 'default';
            cell.classList.remove('editable');
        });
        
        document.querySelectorAll('.editable-select, .editable-date, .editable-money').forEach(cell => {
            cell.style.cursor = 'default';
            cell.onclick = null;
        });
        
        console.log('👁️ Modo solo lectura activado');
    }
});

// 2. FUNCIÓN PARA ELIMINAR EQUIPO
async function eliminarEquipo(equipoId, ost) {
    if (!userPermissions.canDelete) {
        alert('⛔ No tienes permisos para eliminar equipos');
        return;
    }
    
    const confirmacion = confirm(
        `⚠️ ¿Estás seguro de eliminar el equipo OST ${ost}?\n\n` +
        `Esta acción NO se puede deshacer.\n` +
        `Se eliminarán también todos los archivos adjuntos.`
    );
    
    if (!confirmacion) return;
    
    const doubleCheck = confirm(
        `🚨 ÚLTIMA CONFIRMACIÓN\n\n` +
        `¿REALMENTE deseas eliminar OST ${ost}?`
    );
    
    if (!doubleCheck) return;
    
    const finalCheck = prompt('Escribe "ELIMINAR" para confirmar:');
    if (finalCheck !== 'ELIMINAR') {
        alert('❌ Operación cancelada');
        return;
    }
    
    const loadingMsg = document.createElement('div');
    loadingMsg.style.cssText = `
        position: fixed; top: 50%; left: 50%;
        transform: translate(-50%, -50%);
        background: white; padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        z-index: 10000; text-align: center;
    `;
    loadingMsg.innerHTML = '<h3>🔄 Eliminando...</h3>';
    document.body.appendChild(loadingMsg);
    
    try {
        const response = await fetch(`/api/equipo/${equipoId}`, {
            method: 'DELETE',
            headers: {'Content-Type': 'application/json'}
        });
        
        const result = await response.json();
        document.body.removeChild(loadingMsg);
        
        if (result.success) {
            alert('✅ Equipo eliminado correctamente');
            window.location.reload();
        } else {
            alert('❌ Error: ' + (result.error || 'Error desconocido'));
        }
    } catch (error) {
        document.body.removeChild(loadingMsg);
        alert('❌ Error de red al eliminar');
    }
}

// 3. AUTO-GUARDADO (opcional)
let autoSaveTimeout;
const AUTO_SAVE_DELAY = 3000; // 3 segundos

function setupAutoSave() {
    if (!userPermissions.canEdit) return;
    
    document.querySelectorAll('.editable').forEach(cell => {
        cell.addEventListener('input', function() {
            const equipoId = this.closest('.data-row').getAttribute('data-id');
            clearTimeout(autoSaveTimeout);
            this.style.borderLeft = '3px solid #ffc107';
            
            autoSaveTimeout = setTimeout(() => {
                console.log('💾 Auto-guardando equipo', equipoId);
                guardarCambios(equipoId);
                this.style.borderLeft = '';
            }, AUTO_SAVE_DELAY);
        });
    });
    
    console.log('🤖 Auto-guardado activado');
}

document.addEventListener('DOMContentLoaded', setupAutoSave);

// 4. ATAJO Ctrl+S
document.addEventListener('keydown', function(e) {
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        
        if (!userPermissions.canEdit) {
            alert('⛔ No tienes permisos para guardar');
            return;
        }
        
        const activeCell = document.activeElement;
        if (activeCell && activeCell.closest('.data-row')) {
            const equipoId = activeCell.closest('.data-row').getAttribute('data-id');
            if (equipoId) {
                console.log('⌨️ Guardando con Ctrl+S');
                guardarCambios(equipoId);
            }
        }
    }
});

console.log('✅ Sistema de permisos cargado');
```

---

# PASO 4: VERIFICAR

## 1. Reiniciar aplicación
```bash
python app.py
```

## 2. Probar con diferentes usuarios:

### Usuario VIEWER:
- ❌ No puede editar celdas
- ❌ No ve botones
- ✅ Puede ver todo

### Usuario EDITOR V2:
- ✅ Puede editar celdas
- ✅ Ve botón 💾 Guardar
- ❌ NO ve botón 🗑️

### Usuario EDITOR FULL:
- ✅ Puede editar celdas
- ✅ Ve botón 💾 Guardar
- ✅ Ve botón 🗑️ Eliminar

### Usuario ADMIN:
- ✅ Todo lo anterior
- ✅ Ve menú "📊 Auditoría"
- ✅ Puede gestionar usuarios

---

# 📊 RESUMEN DE CAMBIOS EN EQUIPOS.HTML

| Sección | Cambios | Ubicación |
|---------|---------|-----------|
| CSS | Agregar estilos de botones | Dentro de `<style>` |
| Columna Acciones | Botones condicionales | Loop de equipos |
| Celdas Editables | Condicional por permiso | ~15-20 celdas |
| Selects | Condicional onclick | 4 campos |
| Fechas | Condicional onclick | 3 campos |
| Dinero | Condicional onclick | 2 campos |
| JavaScript | Código completo | Dentro de `<script>` |

**Total aproximado: 30-40 modificaciones**

---

# ✅ CHECKLIST FINAL

- [ ] SQL ejecutado en base de datos
- [ ] auth.py reemplazado
- [ ] app.py reemplazado
- [ ] base.html reemplazado
- [ ] usuarios.html reemplazado
- [ ] auditoria.html agregado
- [ ] equipos.html: CSS agregado
- [ ] equipos.html: Columna acciones modificada
- [ ] equipos.html: Celdas editables modificadas
- [ ] equipos.html: JavaScript agregado
- [ ] Aplicación reiniciada
- [ ] Probado con viewer
- [ ] Probado con editor
- [ ] Probado con admin
- [ ] Auditoría funciona

---

# 🎉 ¡LISTO!

Tu sistema ahora tiene:
- ✅ 4 niveles de permisos
- ✅ Auditoría completa
- ✅ Botones según rol
- ✅ Celdas bloqueadas para viewers
- ✅ Triple confirmación para eliminar
- ✅ Auto-guardado opcional
- ✅ Historial de cambios

**¡Tu aplicación está lista para producción!** 🚀

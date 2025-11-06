from flask import Flask, render_template, request, jsonify, redirect, url_for
import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv
from datetime import datetime, date

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'

DATABASE_URL = os.getenv('DATABASE_URL')

def get_db_connection():
    """Conexión a la base de datos"""
    try:
        db_url_clean = DATABASE_URL.replace('&channel_binding=require', '')
        conn = psycopg2.connect(db_url_clean, cursor_factory=psycopg2.extras.RealDictCursor)
        return conn
    except Exception as e:
        print(f"Error de conexión: {e}")
        return None

@app.route('/')
def index():
    """Página principal - Dashboard"""
    conn = get_db_connection()
    if not conn:
        return "Error de conexión a la base de datos", 500
    
    cursor = conn.cursor()
    
    # Métricas
    cursor.execute("SELECT COUNT(*) as total FROM solicitudes")
    total_solicitudes = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as total FROM equipos")
    total_equipos = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as total FROM solicitudes WHERE estado = 'Pendiente'")
    pendientes = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as total FROM equipos WHERE en_garantia = true")
    en_garantia = cursor.fetchone()['total']
    
    # Estados de solicitudes
    cursor.execute("""
        SELECT estado, COUNT(*) as cantidad 
        FROM solicitudes 
        GROUP BY estado
    """)
    estados = cursor.fetchall()
    
    # Categorías de archivos
    cursor.execute("""
        SELECT categoria, COUNT(*) as cantidad 
        FROM archivos_adjuntos 
        GROUP BY categoria
    """)
    categorias = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('dashboard.html', 
                         total_solicitudes=total_solicitudes,
                         total_equipos=total_equipos,
                         pendientes=pendientes,
                         en_garantia=en_garantia,
                         estados=estados,
                         categorias=categorias)

@app.route('/solicitudes')
def solicitudes():
    """Página de solicitudes"""
    conn = get_db_connection()
    if not conn:
        return "Error de conexión a la base de datos", 500
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, fecha_solicitud, email_solicitante, quien_completa, 
               area_solicitante, solicitante, nivel_urgencia, logistica_cargo,
               comentarios_caso, equipo_corresponde_a, motivo_solicitud, estado
        FROM solicitudes
        ORDER BY fecha_solicitud DESC
    """)
    solicitudes = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('solicitudes.html', solicitudes=solicitudes)

@app.route('/equipos')
def equipos():
    """Página de equipos"""
    conn = get_db_connection()
    if not conn:
        return "Error de conexión a la base de datos", 500
    
    cursor = conn.cursor()
    
    # Obtener equipos
    cursor.execute("""
        SELECT id, cliente, ost, estado, fecha_ingreso, remito,
               tipo_equipo, marca, modelo, numero_serie, accesorios,
               observacion_ingreso, prioridad, fecha_envio, proveedor,
               detalles_reparacion, horas_trabajo, reingreso, 
               informe AS informe_tecnico,
               costo AS costo_reparacion, 
               precio AS precio_cliente, 
               ov AS numero_ov, 
               estado_ov, fecha_entrega, remito_entrega
        FROM equipos
        ORDER BY fecha_ingreso DESC
    """)
    equipos = cursor.fetchall()
    
    # Obtener archivos para las fotos (hacer JOIN con equipos para obtener numero_serie)
    cursor.execute("""
        SELECT e.numero_serie, a.categoria, a.url_cloudinary
        FROM archivos_adjuntos a
        INNER JOIN equipos e ON a.equipo_id = e.id
        WHERE e.numero_serie IS NOT NULL
    """)
    archivos = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('equipos.html', equipos=equipos, archivos=archivos)

@app.route('/archivos')
def archivos():
    """Página de archivos adjuntos"""
    conn = get_db_connection()
    if not conn:
        return "Error de conexión a la base de datos", 500
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.id, a.solicitud_id, a.equipo_id, a.nombre_archivo,
               a.url_cloudinary, a.tipo_archivo, a.categoria,
               a.tamano_bytes, a.fecha_subida,
               e.ost, e.numero_serie
        FROM archivos_adjuntos a
        LEFT JOIN equipos e ON a.equipo_id = e.id
        ORDER BY a.fecha_subida DESC
    """)
    archivos = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('archivos.html', archivos=archivos)

@app.route('/api/solicitud/<int:id>', methods=['PUT'])
def update_solicitud(id):
    """API para actualizar solicitud"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Error de conexión'}), 500
    
    data = request.json
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE solicitudes SET 
                email_solicitante = %s, quien_completa = %s,
                area_solicitante = %s, solicitante = %s, nivel_urgencia = %s,
                logistica_cargo = %s, comentarios_caso = %s, equipo_corresponde_a = %s,
                motivo_solicitud = %s, estado = %s
            WHERE id = %s
        """, (
            data.get('email_solicitante'),
            data.get('quien_completa'),
            data.get('area_solicitante'),
            data.get('solicitante'),
            data.get('nivel_urgencia'),
            data.get('logistica_cargo'),
            data.get('comentarios_caso'),
            data.get('equipo_corresponde_a'),
            data.get('motivo_solicitud'),
            data.get('estado'),
            id
        ))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return jsonify({'error': str(e)}), 500

# ============================================
# NUEVOS ENDPOINTS PARA EL FORMULARIO DE AGREGAR EQUIPO
# ============================================

@app.route('/api/proximo-ost', methods=['GET'])
def obtener_proximo_ost():
    """Obtiene el próximo número OST disponible"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Error de conexión'}), 500
    
    cursor = conn.cursor()
    
    try:
        # Obtener el OST máximo actual
        cursor.execute("SELECT MAX(ost) as ultimo_ost FROM equipos")
        result = cursor.fetchone()
        ultimo_ost = result['ultimo_ost']
        
        # Si no hay equipos, empezar desde 1
        if ultimo_ost is None or ultimo_ost == 0:
            proximo_ost = 1
        else:
            proximo_ost = ultimo_ost + 1
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'proximo_ost': str(proximo_ost)
        })
    
    except Exception as e:
        cursor.close()
        conn.close()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/equipos', methods=['POST'])
def crear_equipo():
    """API para crear un nuevo equipo (usado por el formulario de agregar)"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Error de conexión'}), 500
    
    data = request.json
    cursor = conn.cursor()
    
    try:
        # Validar campos requeridos
        if not data.get('cliente'):
            return jsonify({'success': False, 'error': 'El campo "cliente" es requerido'}), 400
        
        if not data.get('tipo_equipo'):
            return jsonify({'success': False, 'error': 'El campo "tipo_equipo" es requerido'}), 400
        
        # Convertir fecha de string a date si viene como string
        fecha_ingreso = data.get('fecha_ingreso')
        if isinstance(fecha_ingreso, str):
            try:
                fecha_ingreso = datetime.strptime(fecha_ingreso, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'error': 'Formato de fecha inválido'}), 400
        
        # Insertar el equipo (el OST se autogenera por la secuencia PostgreSQL)
        # Convertir cadenas vacías a None para la base de datos
        def empty_to_none(value):
            return None if value == '' or value is None else value
        
        # Insertar el equipo (el OST se autogenera por la secuencia PostgreSQL)
        cursor.execute("""
            INSERT INTO equipos (
                cliente, tipo_equipo, marca, modelo, numero_serie,
                fecha_ingreso, remito, accesorios, prioridad, 
                observacion_ingreso, estado
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, ost
        """, (
            data.get('cliente'),
            data.get('tipo_equipo'),
            empty_to_none(data.get('marca')),
            empty_to_none(data.get('modelo')),
            empty_to_none(data.get('numero_serie')),
            fecha_ingreso,
            empty_to_none(data.get('remito')),
            empty_to_none(data.get('accesorios')),
            data.get('prioridad', 'Media'),
            empty_to_none(data.get('observacion_ingreso')),
            'Pendiente'
        ))
        result = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'id': result['id'],
            'ost': result['ost'],
            'message': 'Equipo creado exitosamente'
        }), 201
    
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================
# FIN DE NUEVOS ENDPOINTS
# ============================================

@app.route('/api/equipo/add', methods=['POST'])
def add_equipo():
    """API para agregar equipo (antiguo endpoint - mantener por compatibilidad)"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Error de conexión'}), 500
    
    data = request.json
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO equipos (solicitud_id, numero_equipo, tipo_equipo, marca, modelo,
                               numero_serie, cliente, accesorios, prioridad, 
                               observacion_ingreso, fecha_ingreso, en_garantia)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_DATE, false)
            RETURNING id, ost
        """, (
            data.get('solicitud_id'),
            data.get('numero_equipo'),
            data.get('tipo_equipo'),
            data.get('marca'),
            data.get('modelo'),
            data.get('numero_serie'),
            data.get('cliente', 'Syemed'),
            data.get('accesorios'),
            data.get('prioridad', 'Media'),
            data.get('observacion_ingreso')
        ))
        result = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'id': result['id'], 'ost': result['ost']})
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/equipo/<int:id>', methods=['PUT'])
def update_equipo(id):
    """API para actualizar equipo"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Error de conexión'}), 500
    
    data = request.json
    cursor = conn.cursor()
    
    try:
        # Construir la consulta dinámicamente solo con los campos que vienen
        campos = []
        valores = []
        
        if 'cliente' in data:
            campos.append('cliente = %s')
            valores.append(data.get('cliente'))
        if 'tipo_equipo' in data:
            campos.append('tipo_equipo = %s')
            valores.append(data.get('tipo_equipo'))
        if 'marca' in data:
            campos.append('marca = %s')
            valores.append(data.get('marca'))
        if 'modelo' in data:
            campos.append('modelo = %s')
            valores.append(data.get('modelo'))
        if 'numero_serie' in data:
            campos.append('numero_serie = %s')
            valores.append(data.get('numero_serie'))
        if 'accesorios' in data:
            campos.append('accesorios = %s')
            valores.append(data.get('accesorios'))
        if 'prioridad' in data:
            campos.append('prioridad = %s')
            valores.append(data.get('prioridad'))
        if 'remito' in data:
            campos.append('remito = %s')
            valores.append(data.get('remito'))
        if 'observacion_ingreso' in data:
            campos.append('observacion_ingreso = %s')
            valores.append(data.get('observacion_ingreso'))
        if 'detalle_reparacion' in data:
            campos.append('detalles_reparacion = %s')
            valores.append(data.get('detalle_reparacion'))
        if 'horas_trabajo' in data:
            campos.append('horas_trabajo = %s')
            valores.append(data.get('horas_trabajo'))
        if 'reingreso' in data:
            campos.append('reingreso = %s')
            valores.append(data.get('reingreso'))
        if 'informe_tecnico' in data:
            campos.append('informe = %s')
            valores.append(data.get('informe_tecnico'))
        if 'costo_reparacion' in data:
            campos.append('costo = %s')
            valores.append(data.get('costo_reparacion'))
        if 'precio_cliente' in data:
            campos.append('precio = %s')
            valores.append(data.get('precio_cliente'))
        if 'numero_ov' in data:
            campos.append('ov = %s')
            valores.append(data.get('numero_ov'))
        if 'estado_ov' in data:
            campos.append('estado_ov = %s')
            valores.append(data.get('estado_ov'))
        if 'fecha_ingreso' in data:
            campos.append('fecha_ingreso = %s')
            valores.append(data.get('fecha_ingreso'))
        if 'fecha_envio_proveedor' in data:
            campos.append('fecha_envio = %s')
            valores.append(data.get('fecha_envio_proveedor'))
        if 'fecha_entrega' in data:
            campos.append('fecha_entrega = %s')
            valores.append(data.get('fecha_entrega'))
        if 'remito_entrega' in data:
            campos.append('remito_entrega = %s')
            valores.append(data.get('remito_entrega'))
        if 'estado' in data:
            campos.append('estado = %s')
            valores.append(data.get('estado'))
        if 'proveedor' in data:
            campos.append('proveedor = %s')
            valores.append(data.get('proveedor'))
        
        if not campos:
            return jsonify({'error': 'No hay campos para actualizar'}), 400
        
        # Agregar el ID al final
        valores.append(id)
        
        query = f"UPDATE equipos SET {', '.join(campos)} WHERE id = %s"
        
        cursor.execute(query, valores)
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error al actualizar: {e}")
        conn.rollback()
        cursor.close()
        conn.close()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
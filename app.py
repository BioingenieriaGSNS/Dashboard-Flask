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
    cursor.execute("""
        SELECT e.id, e.solicitud_id, s.fecha_solicitud, s.solicitante, s.estado as estado_solicitud,
               e.ost, e.numero_equipo, e.tipo_equipo, e.marca, e.modelo, 
               e.numero_serie, e.en_garantia, e.fecha_compra, e.fecha_ingreso,
               e.cliente, e.remito, e.accesorios, e.prioridad, 
               e.observacion_ingreso, e.fecha_envio, e.proveedor,
               e.detalles_reparacion, e.horas_trabajo, e.reingreso,
               e.informe, e.costo, e.precio, e.ov, e.estado_ov,
               e.fecha_entrega, e.remito_entrega, e.estado,
               STRING_AGG(
                   CASE WHEN a.categoria = 'falla' 
                   THEN a.url_cloudinary 
                   END, '||'
               ) as urls_fotos_fallas,
               STRING_AGG(
                   CASE WHEN a.categoria = 'factura' 
                   THEN a.url_cloudinary 
                   END, '||'
               ) as urls_facturas
        FROM equipos e
        LEFT JOIN solicitudes s ON e.solicitud_id = s.id
        LEFT JOIN archivos_adjuntos a ON a.equipo_id = e.id
        GROUP BY e.id, s.fecha_solicitud, s.solicitante, s.estado
        ORDER BY e.fecha_ingreso DESC
    """)
    equipos = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('equipos.html', equipos=equipos)

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

@app.route('/api/equipo/add', methods=['POST'])
def add_equipo():
    """API para agregar equipo"""
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
        cursor.execute("""
            UPDATE equipos SET 
                tipo_equipo = %s, marca = %s, modelo = %s,
                numero_serie = %s, accesorios = %s, prioridad = %s,
                observacion_ingreso = %s, detalles_reparacion = %s,
                horas_trabajo = %s, costo = %s, precio = %s,
                ov = %s, estado_ov = %s, estado = %s
            WHERE id = %s
        """, (
            data.get('tipo_equipo'),
            data.get('marca'),
            data.get('modelo'),
            data.get('numero_serie'),
            data.get('accesorios'),
            data.get('prioridad'),
            data.get('observacion_ingreso'),
            data.get('detalles_reparacion'),
            data.get('horas_trabajo'),
            data.get('costo'),
            data.get('precio'),
            data.get('ov'),
            data.get('estado_ov'),
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
    

    

if __name__ == '__main__':
    app.run(debug=True)